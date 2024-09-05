#!/usr/bin/env bash

set -e

USERNAME="${1:-sqs-user}"
ENDPOINT="${3:-http://localhost:4566}"
POLICY_ARN='arn:aws:iam::aws:policy/AmazonSQSFullAccess'

delete_user_if_exists() {
  if aws --endpoint-url=${ENDPOINT} iam get-user --user-name "${USERNAME}" &>/dev/null; then

    # detach policy
    aws --endpoint-url=${ENDPOINT} iam list-attached-user-policies --user-name "${USERNAME}" | jq -r '.AttachedPolicies[].PolicyArn' | while read -r policy_arn; do
      aws --endpoint-url=${ENDPOINT} iam detach-user-policy --user-name "${USERNAME}" --policy-arn "${policy_arn}"
    done

    # delete user
    aws --endpoint-url=${ENDPOINT} iam delete-user --user-name "${USERNAME}"

  fi
}

create_user() {
  aws --endpoint-url=${ENDPOINT} iam create-user --user-name "${USERNAME}" >/dev/null
}

attach_policy() {
  aws \
    --endpoint-url=${ENDPOINT} \
    iam attach-user-policy \
    --user-name "${USERNAME}" \
    --policy-arn "${POLICY_ARN}"
}

create_access_key() {
  ACCESS_KEYS=$(aws --endpoint-url=${ENDPOINT} iam create-access-key --user-name "${USERNAME}")
  ACCESS_KEY_ID=$(echo "${ACCESS_KEYS}" | jq -r ".AccessKey.AccessKeyId")
  SECRET_ACCESS_KEY=$(echo "${ACCESS_KEYS}" | jq -r ".AccessKey.SecretAccessKey")
  echo "{\"AccessKeyId\": \"${ACCESS_KEY_ID}\", \"SecretAccessKey\": \"${SECRET_ACCESS_KEY}\"}"
}

main() {
  delete_user_if_exists
  create_user
  attach_policy
  create_access_key
}

main
