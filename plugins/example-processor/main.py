"""
Example Data Processor Plugin
Demonstrates data transformation plugin
"""

import sys
import json
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def process(input_data):
    """
    Plugin core logic - simple data processing example

    Args:
        input_data: Dict with data to process

    Returns:
        Dict with processed results
    """
    try:
        data = input_data.get("data", [])
        operation = input_data.get("operation", "sum")

        if not data:
            raise ValueError("No data provided")

        # Simple data processing operations
        if operation == "sum":
            result_value = sum(data)
        elif operation == "average":
            result_value = sum(data) / len(data)
        elif operation == "max":
            result_value = max(data)
        elif operation == "min":
            result_value = min(data)
        else:
            raise ValueError(f"Unknown operation: {operation}")

        return {
            "operation": operation,
            "result": result_value,
            "input_count": len(data),
            "metadata": {
                "processor_version": "1.0.0",
            },
        }

    except Exception as e:
        logger.error(f"Processing failed: {str(e)}")
        raise


if __name__ == "__main__":
    try:
        # Read input data
        if len(sys.argv) > 1:
            input_data = json.loads(sys.argv[1])
        else:
            input_data = json.load(sys.stdin)

        # Process
        result = process(input_data)

        # Output result as JSON
        print(json.dumps(result))
        sys.exit(0)

    except Exception as e:
        logger.error(f"Fatal error: {str(e)}")
        sys.exit(1)
