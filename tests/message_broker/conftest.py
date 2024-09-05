import pytest

try:
    import boto3
except ImportError:
    boto3 = None  # type: ignore[assignment]

from tests.utils.aws_sqs import (
    can_connect_to_sqs,
    SQSUser,
    SQSQueue,
)


@pytest.fixture(scope="module")
def sqs_user_mod():
    if not can_connect_to_sqs():
        return None, None

    sqs = SQSUser()
    sqs()
    yield sqs
    del sqs


@pytest.fixture(scope="module")
def sqs_queue_mod(sqs_user_mod):
    if not can_connect_to_sqs():
        return None

    queue = SQSQueue(sqs_user_mod)
    queue()
    yield queue
    del queue
