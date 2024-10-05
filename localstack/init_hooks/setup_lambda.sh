#!/bin/bash

awslocal sqs create-queue --queue-name test-queue
awslocal sns create-topic --name test-topic

# Deploy the Lambda function
awslocal lambda create-function \
    --function-name test-lambda \
    --runtime python3.8 \
    --handler lambda_function.lambda_handler \
    --role arn:aws:iam::000000000000:role/lambda-ex \
    --zip-file fileb:///var/lib/localstack/files/lambda_function.py.zip

# Setup environment variables for Lambda
awslocal lambda update-function-configuration \
    --function-name test-lambda \
    --environment "Variables={SQS_QUEUE_URL=http://localhost:4566/000000000000/test-queue,SNS_TOPIC_ARN=arn:aws:sns:us-east-1:000000000000:test-topic}"

