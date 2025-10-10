"""
RabbitMQ message queue service
Handles job queue and status queue communication
"""

import json
import logging
from typing import Dict, Optional

import pika
from pika.adapters.blocking_connection import BlockingChannel, BlockingConnection

from app.core.config import settings

logger = logging.getLogger(__name__)


class RabbitMQService:
    """Service for RabbitMQ operations"""

    def __init__(self):
        self.connection: Optional[BlockingConnection] = None
        self.channel: Optional[BlockingChannel] = None

    def connect(self):
        """Establish connection to RabbitMQ"""
        try:
            parameters = pika.URLParameters(settings.RABBITMQ_URL)
            self.connection = pika.BlockingConnection(parameters)
            self.channel = self.connection.channel()

            # Declare queues
            self._declare_queues()

            logger.info("Connected to RabbitMQ")
        except Exception as e:
            logger.error(f"Failed to connect to RabbitMQ: {e}")
            raise

    def _declare_queues(self):
        """Declare required queues with configurations"""
        # Job queue - for sending jobs to Ray workers
        self.channel.queue_declare(
            queue="job_queue",
            durable=True,
            arguments={
                "x-message-ttl": 3600000,  # 1 hour
                "x-max-length": 10000,
                "x-dead-letter-exchange": "dlx_exchange",
            },
        )

        # Status queue - for receiving status updates from Ray workers
        self.channel.queue_declare(
            queue="status_queue",
            durable=True,
            arguments={
                "x-message-ttl": 1800000,  # 30 minutes
            },
        )

        # Dead letter exchange and queue
        self.channel.exchange_declare(
            exchange="dlx_exchange",
            exchange_type="direct",
            durable=True,
        )

        self.channel.queue_declare(
            queue="dead_letter_queue",
            durable=True,
        )

        self.channel.queue_bind(
            queue="dead_letter_queue",
            exchange="dlx_exchange",
            routing_key="job_queue",
        )

    def publish_job(self, job_data: Dict):
        """
        Publish job to job_queue

        Args:
            job_data: Dictionary with job information
        """
        if not self.channel:
            self.connect()

        try:
            message = json.dumps(job_data)
            self.channel.basic_publish(
                exchange="",
                routing_key="job_queue",
                body=message,
                properties=pika.BasicProperties(
                    delivery_mode=2,  # Make message persistent
                    content_type="application/json",
                ),
            )
            logger.info(f"Published job {job_data.get('job_id')} to queue")
        except Exception as e:
            logger.error(f"Failed to publish job: {e}")
            raise

    def consume_status_updates(self, callback):
        """
        Start consuming status updates from status_queue

        Args:
            callback: Function to call for each message
        """
        if not self.channel:
            self.connect()

        def on_message(ch, method, properties, body):
            try:
                message = json.loads(body)
                callback(message)
                ch.basic_ack(delivery_tag=method.delivery_tag)
            except Exception as e:
                logger.error(f"Error processing status update: {e}")
                ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)

        self.channel.basic_qos(prefetch_count=1)
        self.channel.basic_consume(
            queue="status_queue",
            on_message_callback=on_message,
        )

        logger.info("Starting to consume status updates")
        self.channel.start_consuming()

    def close(self):
        """Close RabbitMQ connection"""
        if self.connection and not self.connection.is_closed:
            self.connection.close()
            logger.info("Closed RabbitMQ connection")


# Global instance
mq_service = RabbitMQService()


def get_mq_service() -> RabbitMQService:
    """Get RabbitMQ service instance"""
    if not mq_service.connection or mq_service.connection.is_closed:
        mq_service.connect()
    return mq_service
