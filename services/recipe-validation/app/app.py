import pika
import json
import time
from openai import OpenAI

from config import *
from Logger import Logger

Logger.initialize_logger()

RABBITMQ_CONNECTION = None
OPENAI_CLIENT = OpenAI(api_key=OPENAI_API_SECRET)


# This function is used to repeatedly try to connect RabitMQ
# We can use healthy check in docker compose file as well on startup
def connect_to_rabbitmq():
    while True:
        try:
            return pika.BlockingConnection(pika.URLParameters(RABBITMQ_URL))
        except Exception:
            time.sleep(3)


def construct_recipe_validation_prompt(data):
    data = json.loads(data.decode())

    request_string = f"""
        You are a professional chef. The recipe is defined between <recipe> and </recipe>.
        Check if it is realistic or not.
        Check all the recipe parameters: the ratio of ingredients;
        Step-by-step directions is clear and precise;
        combination of ingredients and flavour pairings are correct, harmonious, and enjoyable.
        You are answering only “Yes” or “No”.
        
        <recipe>
            {data["recipe"]}
        </recipe>"""
    return request_string


def chat_gpt(prompt):
    response = OPENAI_CLIENT.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content.strip()


def on_request(ch, method, properties, body):
    recipe = construct_recipe_validation_prompt(body)
    response = chat_gpt(recipe)

    ch.basic_publish(
        exchange='',
        # Could be passed from .env file to make sure everywhere the same value
        routing_key='queue_recipe_validation_response',
        properties=pika.BasicProperties(
            correlation_id=properties.correlation_id
        ),
        body=response,
    )
    ch.basic_ack(delivery_tag=method.delivery_tag)


def start_rabbitmq_consumer():
    try:
        global RABBITMQ_CONNECTION
        channel = RABBITMQ_CONNECTION.channel()
        channel.queue_declare(queue="queue_recipe_validation_request", durable=False)
        channel.queue_declare(queue="queue_recipe_validation_response", durable=False)

        channel.basic_consume(
            queue="queue_recipe_validation_request",
            on_message_callback=on_request,
            auto_ack=False
        )
        channel.start_consuming()

    except Exception as e:
        Logger.error(f"Not connecting to RabbitMQ: {e}")

def main():
    global RABBITMQ_CONNECTION
    RABBITMQ_CONNECTION = connect_to_rabbitmq()
    start_rabbitmq_consumer()


if __name__ == "__main__":
    main()