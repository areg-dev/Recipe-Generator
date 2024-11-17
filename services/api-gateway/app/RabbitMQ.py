import uuid
import pika
import time

from config import *
from Logger import Logger


class RabbitMQ:
    RABBITMQ_CONNECTION = None
    QUEUE_RECIPE_GENERATION = "queue_recipe_generation"
    QUEUE_NUTRITIONAL_CALCULATOR = "queue_nutritional_calculator"
    QUEUE_RECIPE_VALIDATION = "queue_recipe_validation"

    @staticmethod
    def connect_to_rabbitmq():
        while True:
            try:
                parameters = pika.URLParameters(RABBITMQ_URL)
                parameters.heartbeat = 10
                return pika.BlockingConnection(parameters)
            except Exception:
                time.sleep(3)

    @staticmethod
    def initialize_rabbitmq():
        RabbitMQ.RABBITMQ_CONNECTION = RabbitMQ.connect_to_rabbitmq()

    def __init__(self, queue):
        self.queue = queue
        self.request_queue = self.queue + '_request'
        self.response_queue = self.queue + '_response'

        self.response = None
        self.connection = None
        self.channel = None
        self.connect()

    def connect(self):
        if RabbitMQ.RABBITMQ_CONNECTION is None or RabbitMQ.RABBITMQ_CONNECTION.is_closed:
            RabbitMQ.initialize_rabbitmq()
        try:
            self.channel = RabbitMQ.RABBITMQ_CONNECTION.channel()
            self.channel.queue_declare(queue=self.response_queue)
        except Exception:
            RabbitMQ.initialize_rabbitmq()  # Try reconnect
            self.channel = RabbitMQ.RABBITMQ_CONNECTION.channel()
            self.channel.queue_declare(queue=self.response_queue)

    def publish(self, corr_id, data):
        if not self.channel.is_open:
            self.connect()
        if not self.channel.is_open:
            Logger.error("Channel disconnected: " + self.request_queue)
            return
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
            Logger.error("Channel disconnected: " + self.request_queue)
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

        corr_id = str(uuid.uuid4())  # Identifier for multiple requests
        self.publish(corr_id, data)
        self.consume(on_response)
        if self.response:
            return self.response.decode()
        return self.response
