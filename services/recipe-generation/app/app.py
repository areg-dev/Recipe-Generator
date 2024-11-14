import pika
import json
import time
from openai import OpenAI

from config import *

RABBITMQ_CONNECT = None
OPENAI_CLIENT = OpenAI(api_key=OPENAI_API_SECRET)


# This function is used to repeatedly try to connect RabitMQ
# We can use healthy check in docker compose file as well on startup
def connect_to_rabbitmq():
    while True:
        try:
            return pika.BlockingConnection(pika.URLParameters(RABBITMQ_URL))
        except Exception:
            time.sleep(3)


def construct_recipe(data):
    data = json.loads(data.decode())
    amount_of_persons = data["number_of_persons"]
    dish_type = data["dish_type"]
    max_cooking = data["max_cooking_time"]
    allergies_list = ", ".join(data["allergies_list"])
    diet_requirements = ", ".join(data["diet_requirements"])
    cuisine_list = ", ".join(data["cuisine_list"])

    request_string = f"""
        Hey, ChatGPT, generate me a meal recipe for {amount_of_persons} and {dish_type}
        with cooking time under {max_cooking} minutes,
        good for people with allergies to {allergies_list},
        following {diet_requirements},
        preferring the {cuisine_list} given."""
    return request_string


def chat_gpt(prompt):
    response = OPENAI_CLIENT.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content.strip()


def on_request(ch, method, properties, body):
    print(f"[Recipe Generation] Received {body.decode()}")
    recipe = construct_recipe(body)
    response = chat_gpt(recipe)

    ch.basic_publish(
        exchange='',
        # Could be passed from .env file to make sure everywhere the same value
        routing_key='queue_recipe_generation_response',
        properties=pika.BasicProperties(
            correlation_id=properties.correlation_id
        ),
        body=response,
    )
    print(f"[Recipe Generation] Sent response: {response}")
    ch.basic_ack(delivery_tag=method.delivery_tag)


def start_rabbitmq_consumer():
    try:
        print("[Recipe Generation] start_rabbitmq_consumer")
        global RABBITMQ_CONNECT
        channel = RABBITMQ_CONNECT.channel()
        # Because of Recipe Generation starting before API Gateway for safety creating 2 direction queues
        channel.queue_declare(queue="queue_recipe_generation_request", durable=False)
        channel.queue_declare(queue="queue_recipe_generation_response", durable=False)

        channel.basic_consume(
            queue="queue_recipe_generation_request",
            on_message_callback=on_request,
            auto_ack=False
        )
        print("[Recipe Generation] Waiting for requests. To exit press CTRL+C")
        channel.start_consuming()

    except Exception as e:
        print(f"[Recipe Generation] Error connecting to RabbitMQ: {e}")


def main():
    global RABBITMQ_CONNECT
    RABBITMQ_CONNECT = connect_to_rabbitmq()
    start_rabbitmq_consumer()


if __name__ == "__main__":
    main()
