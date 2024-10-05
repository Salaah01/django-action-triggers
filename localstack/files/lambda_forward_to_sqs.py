import json
import boto3
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

sqs = boto3.client("sqs")

QUEUE_NAME = "echo-back-queue"


def get_queue_url(queue_name):
    response = sqs.get_queue_url(QueueName=queue_name)
    return response["QueueUrl"]


def lambda_handler(event, context):
    logger.info("Starting lambda function")
    logger.info(f"Raw event data: {event}")

    try:
        if not event:
            raise ValueError("Received an empty event payload.")

        logger.info(f"Received event: {json.dumps(event, indent=2)}")
        queue_url = get_queue_url(QUEUE_NAME)

        response = sqs.send_message(
            QueueUrl=queue_url,
            MessageBody=json.dumps(event),
        )

        logger.info(f"Message sent to queue: {response['MessageId']}")

        return {
            "statusCode": 200,
            "body": json.dumps(
                {
                    "message": "Message sent to queue",
                    "messageId": response["MessageId"],
                }
            ),
        }

    except Exception as e:
        logger.error(f"Error processing event: {str(e)}")
        return {
            "statusCode": 500,
            "body": json.dumps({"error": str(e)})
        }
