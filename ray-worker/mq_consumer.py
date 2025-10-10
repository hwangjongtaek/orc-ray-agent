"""
RabbitMQ consumer for job queue
"""

import json
import logging

import pika
import ray

from actors import PluginExecutorActor
from config import settings

logger = logging.getLogger(__name__)


class JobQueueConsumer:
    """Consumes jobs from RabbitMQ job_queue and dispatches to Ray actors"""

    def __init__(self, rabbitmq_url: str, num_actors: int = 5):
        """
        Initialize JobQueueConsumer.

        Args:
            rabbitmq_url: RabbitMQ connection URL
            num_actors: Number of PluginExecutorActor instances to create
        """
        self.rabbitmq_url = rabbitmq_url
        self.connection = None
        self.channel = None

        # Create pool of Ray actors
        self.actors = [
            PluginExecutorActor.remote(rabbitmq_url) for _ in range(num_actors)
        ]
        self.current_actor_idx = 0

        logger.info(f"Created {num_actors} PluginExecutorActor instances")

    def connect(self):
        """Connect to RabbitMQ"""
        parameters = pika.URLParameters(self.rabbitmq_url)
        self.connection = pika.BlockingConnection(parameters)
        self.channel = self.connection.channel()

        # Declare job queue
        self.channel.queue_declare(queue="job_queue", durable=True)

        # Set QoS to process one message at a time
        self.channel.basic_qos(prefetch_count=1)

        logger.info("Connected to RabbitMQ")

    def on_message(self, ch, method, properties, body):
        """
        Callback for processing job messages.

        Args:
            ch: Channel
            method: Delivery method
            properties: Message properties
            body: Message body
        """
        try:
            # Parse job message
            job_data = json.loads(body)
            job_id = job_data["job_id"]
            image_url = job_data["docker_image_url"]
            input_data = job_data["input_data"]

            logger.info(f"Received job {job_id}")

            # Get next actor from pool (round-robin)
            actor = self.actors[self.current_actor_idx]
            self.current_actor_idx = (self.current_actor_idx + 1) % len(self.actors)

            # Execute plugin asynchronously via Ray actor
            actor.execute_plugin.remote(job_id, image_url, input_data)

            # Acknowledge message
            ch.basic_ack(delivery_tag=method.delivery_tag)

            logger.info(f"Job {job_id} dispatched to Ray actor")

        except Exception as e:
            logger.error(f"Error processing job: {e}")
            # Reject message and requeue
            ch.basic_nack(delivery_tag=method.delivery_tag, requeue=True)

    def start_consuming(self):
        """Start consuming messages from job_queue"""
        self.connect()

        logger.info("Starting to consume jobs from job_queue")

        self.channel.basic_consume(
            queue="job_queue", on_message_callback=self.on_message
        )

        try:
            self.channel.start_consuming()
        except KeyboardInterrupt:
            logger.info("Stopping consumer...")
            self.channel.stop_consuming()
        finally:
            if self.connection and not self.connection.is_closed:
                self.connection.close()
