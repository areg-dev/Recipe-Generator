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
            parameters = pika.URLParameters(RABBITMQ_URL)
            parameters.heartbeat = 10
            return pika.BlockingConnection(parameters)
        except Exception:
            time.sleep(3)


def construct_nutritional_calculator_prompt(data):
    data = json.loads(data.decode())

    request_string = f"""
        You are food technologist.
        The recipe is defined between <recipe> and </recipe>.
        Calculate the weight of this dish, the number of servings,
        and the nutritional values (calories, protein, fat, carbohydrates)
        Your output should be in format defined between <format> and </format>.
        You are not asking questions, just responding with JSON that contains nutritional values.
        <format>
        1. Each of your answers is a JSON, consisting of few main parameters "calories",
        "protein", "fat", "carbohydrates", "totalWeight"
        </format>
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
    recipe = construct_nutritional_calculator_prompt(body)
    response = chat_gpt(recipe)

    ch.basic_publish(
        exchange='',
        # Could be passed from .env file to make sure everywhere the same value
        routing_key='queue_nutritional_calculator_response',
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
        channel.queue_declare(queue="queue_nutritional_calculator_request", durable=False)
        channel.queue_declare(queue="queue_nutritional_calculator_response", durable=False)

        channel.basic_consume(
            queue="queue_nutritional_calculator_request",
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
