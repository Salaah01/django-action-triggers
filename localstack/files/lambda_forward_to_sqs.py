import json
import boto3

sqs = boto3.client("sqs")


def lambda_handler(event, context):
    """AWS Lambda function to forward messages to an SQS queue."""

    message = json.dumps(event)
    response = sqs.send_message(
        QueueUrl=message["queue_url"],
        MessageBody=message,
    )

    return response
