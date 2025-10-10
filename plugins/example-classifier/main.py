"""
Example ML Classifier Plugin
Demonstrates plugin interface contract
"""

import sys
import json
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def process(input_data):
    """
    Plugin core logic - simple classification example

    Args:
        input_data: Dict with 'features' array

    Returns:
        Dict with prediction results
    """
    try:
        features = input_data.get("features", [])
        model_params = input_data.get("model_params", {})

        # Simple rule-based classification (example)
        # In real plugin, this would be actual ML model inference
        if not features:
            raise ValueError("No features provided")

        # Simple logic: classify based on average value
        avg = sum(features) / len(features)
        if avg > 2.0:
            prediction = "class_A"
            confidence = 0.95
        else:
            prediction = "class_B"
            confidence = 0.87

        return {
            "prediction": prediction,
            "confidence": confidence,
            "metadata": {
                "model_version": "1.0.0",
                "features_count": len(features),
                "average_value": avg,
            },
        }

    except Exception as e:
        logger.error(f"Processing failed: {str(e)}")
        raise


if __name__ == "__main__":
    try:
        # Read input data from command line argument
        if len(sys.argv) > 1:
            input_data = json.loads(sys.argv[1])
        else:
            # Or from stdin
            input_data = json.load(sys.stdin)

        # Process
        result = process(input_data)

        # Output result as JSON to stdout
        print(json.dumps(result))
        sys.exit(0)

    except Exception as e:
        logger.error(f"Fatal error: {str(e)}")
        sys.exit(1)
