"""
Ray Worker entry point
Initializes Ray and starts consuming jobs from RabbitMQ
"""

import logging
import os

import ray

from config import settings
from mq_consumer import JobQueueConsumer

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


def main():
    """Main entry point for Ray worker"""
    logger.info("Starting Ray Worker")

    # Initialize Ray
    if settings.RAY_DEBUG:
        # Local mode for debugging
        ray.init(local_mode=True)
        logger.info("Ray initialized in local mode (debug)")
    else:
        # Connect to Ray cluster
        ray.init(address=settings.RAY_HEAD_ADDRESS)
        logger.info(f"Ray initialized, connected to {settings.RAY_HEAD_ADDRESS}")

    # Create and start job queue consumer
    consumer = JobQueueConsumer(
        rabbitmq_url=settings.RABBITMQ_URL,
        num_actors=5,  # Create 5 actor instances
    )

    logger.info("Starting job queue consumer...")
    consumer.start_consuming()


if __name__ == "__main__":
    main()
