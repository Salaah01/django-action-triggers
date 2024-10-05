#!/usr/bin/env bash

cp /root/files/lambda_echo_back.js index.js
zip index.zip index.js

awslocal lambda create-function \
  --function-name echo-back-lambda \
  --runtime nodejs18.x \
  --zip-file fileb://index.zip \
  --handler index.handler \
  --role arn:aws:iam::000000000000:role/lambda-role
