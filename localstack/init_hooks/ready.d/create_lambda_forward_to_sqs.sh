#!/usr/bin/env bash

awslocal sqs create-queue --queue-name echo-back-queue

cp /root/files/lambda_forward_to_sqs.py lambda_function.py
zip lambda_function.zip lambda_function.py

awslocal lambda create-function \
  --function-name forward-to-sqs-lambda \
  --runtime python3.9 \
  --zip-file fileb://lambda_function.zip \
  --handler lambda_function.lambda_handler \
  --role arn:aws:iam::000000000000:role/lambda-role
