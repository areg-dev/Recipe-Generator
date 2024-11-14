import json
import time
import uuid

import pika
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from config import *


def connect_to_rabbitmq():
    while True:
        try:
            return pika.BlockingConnection(pika.URLParameters(RABBITMQ_URL))
        except Exception:
            time.sleep(3)



class RabbitMQ:
    RABBITMQ_CONNECT = None
    QUEUE_RECIPE_GENERATION = "queue_recipe_generation"

    def __init__(self, queue):
        self.queue = queue
        self.request_queue = self.queue + '_request'
        self.response_queue = self.queue + '_response'

        self.response = None
        self.connection = None
        self.channel = None
        self.connect()

    def connect(self):
        if RabbitMQ.RABBITMQ_CONNECT is None:
            RabbitMQ.RABBITMQ_CONNECT = connect_to_rabbitmq()

        self.channel = RabbitMQ.RABBITMQ_CONNECT.channel()
        self.channel.queue_declare(queue=self.response_queue)

    def disconnect(self):
        if self.channel and self.channel.is_open:
            self.channel.close()

    def __del__(self):
        self.disconnect()

    def publish(self, corr_id, data):
        if not self.channel.is_open:
            self.connect()
        if not self.channel.is_open:
            print("[API Gateway] Channel disconnected: ", self.request_queue)
            return

        print(data)
        self.channel.basic_publish(
            exchange='',
            routing_key=self.request_queue,
            properties=pika.BasicProperties(
                reply_to='',
                correlation_id=corr_id
            ),
            body=data
        )

    def consume(self, callback):
        if not self.channel.is_open:
            self.connect()
        if not self.channel.is_open:
            print("[API Gateway] Channel disconnected: ", self.response_queue)
            return

        self.channel.basic_consume(
            queue=self.response_queue,
            on_message_callback=callback,
            auto_ack=True
        )
        self.channel.start_consuming()

    async def request(self, data):
        def on_response(ch, method, properties, queue_data):
            if properties.correlation_id == corr_id:
                self.response = queue_data
                self.channel.close()  # Need to make with timeout

        corr_id = str(uuid.uuid4()) # Identifier for multiple requests
        self.publish(corr_id, data)
        self.consume(on_response)
        if self.response:
            return self.response.decode()
        return self.response


app = FastAPI()


class RecipeRequest(BaseModel):
    number_of_persons: int
    dish_type: str
    max_cooking_time: int
    allergies_list: list
    diet_requirements: list
    cuisine_list: list


@app.post("/generate-recipe")
async def generate_recipe(data: RecipeRequest):
    # The channel object (not connection) will create on each request
    # I think could it be better to separate the channel connect/disconnect logic
    try:
        rmq = RabbitMQ(RabbitMQ.QUEUE_RECIPE_GENERATION)
        response = await rmq.request(data.model_dump_json())
        return {"message": response}
    except Exception as e:
        print("[API Gateway] Internal Exception: ", e)  # We can also handle exceptions with log files
        raise HTTPException(status_code=500, detail=f"Error processing request: {str(e)}")


@app.post("/calculate-nutrition")
async def calculate_nutrition(data: dict):
    return {"message": "ok"}


@app.post("/validate-recipe")
async def validate_recipe(data: dict):
    return {"message": "ok"}
