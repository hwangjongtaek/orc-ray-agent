"""
Ray Actor for executing plugin containers
Implementation from blueprint specification
"""

import json
import logging

import docker
import pika
import ray

logger = logging.getLogger(__name__)


@ray.remote
class PluginExecutorActor:
    """
    Ray Actor responsible for executing plugin containers.

    This actor receives job information, executes the plugin in a Docker container,
    and reports status updates back via RabbitMQ.
    """

    def __init__(self, rabbitmq_url: str):
        """
        Initialize the PluginExecutorActor.

        Args:
            rabbitmq_url: RabbitMQ connection URL
        """
        self.docker_client = docker.from_env()
        self.rabbitmq_url = rabbitmq_url

        # Setup RabbitMQ connection
        parameters = pika.URLParameters(rabbitmq_url)
        self.connection = pika.BlockingConnection(parameters)
        self.channel = self.connection.channel()

        # Declare status queue
        self.channel.queue_declare(queue="status_queue", durable=True)

        logger.info("PluginExecutorActor initialized")

    def execute_plugin(self, job_id: int, image_url: str, input_data: dict) -> None:
        """
        Execute a plugin container.

        Args:
            job_id: Job ID
            image_url: Docker image URL for the plugin
            input_data: Input data to pass to the plugin
        """
        logger.info(f"Executing plugin for job {job_id} with image {image_url}")

        # Update status to 'processing'
        self._update_status(job_id, "processing")

        try:
            # Execute Docker container
            # Pass input_data as command line argument
            container = self.docker_client.containers.run(
                image_url,
                command=f"python main.py '{json.dumps(input_data)}'",
                detach=True,
                remove=False,  # Keep container for log retrieval
            )

            # Wait for container to finish
            result = container.wait()
            logs = container.logs().decode("utf-8")

            # Clean up container
            container.remove()

            # Check exit code
            if result["StatusCode"] == 0:
                # Success - parse output from stdout
                try:
                    output = json.loads(logs)
                    self._update_status(job_id, "completed", result=output)
                    logger.info(f"Job {job_id} completed successfully")
                except json.JSONDecodeError:
                    # If output is not valid JSON, treat as error
                    self._update_status(
                        job_id,
                        "failed",
                        error_message=f"Invalid JSON output: {logs}",
                    )
            else:
                # Failure - report error
                self._update_status(job_id, "failed", error_message=logs)
                logger.error(
                    f"Job {job_id} failed with exit code {result['StatusCode']}"
                )

        except Exception as e:
            # Exception during execution
            error_msg = str(e)
            self._update_status(job_id, "failed", error_message=error_msg)
            logger.error(f"Job {job_id} failed with exception: {error_msg}")

    def _update_status(self, job_id: int, status: str, result=None, error_message=None):
        """
        Send status update to status_queue.

        Args:
            job_id: Job ID
            status: New status (processing, completed, failed)
            result: Result data (for completed jobs)
            error_message: Error message (for failed jobs)
        """
        from datetime import datetime

        message = {
            "job_id": job_id,
            "status": status,
            "result": result,
            "error_message": error_message,
            "updated_at": datetime.utcnow().isoformat(),
        }

        self.channel.basic_publish(
            exchange="",
            routing_key="status_queue",
            body=json.dumps(message),
            properties=pika.BasicProperties(
                delivery_mode=2,  # Persistent message
                content_type="application/json",
            ),
        )

        logger.info(f"Status update sent for job {job_id}: {status}")
