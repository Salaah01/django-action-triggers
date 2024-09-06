import pytest
from django.conf import settings

from action_triggers.message_broker.aws_sqs import (
    AwsSqsBroker,
    AwsSqsConnection,
)
from action_triggers.message_broker.exceptions import ConnectionValidationError
from tests.utils.aws_sqs import (
    QUEUE_NAME,
    can_connect_to_sqs,
    SQSUser,
    SQSQueue,
)

try:
    import boto3  # type: ignore[import-untyped]
except ImportError:
    boto3 = None  # type: ignore[assignment]


@pytest.fixture(autouse=True, scope="module")
def sqs_user(sqs_user_mod):
    yield sqs_user_mod


@pytest.fixture(autouse=True, scope="module")
def sqs_queue(sqs_queue_mod):
    yield sqs_queue_mod


class TestAwsSqsConnection:
    """Tests for the `AwsSqsConnection` class."""

    def test_raise_exception_if_no_endpoint_url_found(self):
        with pytest.raises(ConnectionValidationError):
            AwsSqsConnection(
                config={},
                conn_details={},
                params={"queue": "queue"},
            )

    def test_raises_exception_if_no_queue_found(self):
        with pytest.raises(ConnectionValidationError):
            AwsSqsConnection(
                config={},
                conn_details={"endpoint_url": "http://test_endpoint"},
                params={},
            )

    @pytest.mark.parametrize(
        "parms",
        [
            {"queue_url": "http://test_queue_1"},
            {"queue_name": "test_queue_1"},
        ],
    )
    def test_passes_when_queue_exists(self, parms):
        AwsSqsConnection(
            config={},
            conn_details={"endpoint_url": "http://test_endpoint"},
            params=parms,
        )

    @pytest.mark.asyncio
    @pytest.mark.skipif(
        not can_connect_to_sqs(),
        reason="localstack (AWS emulator) is not running.",
    )
    async def test_connection_and_close_mechanism_using_conn_details(
        self,
        sqs_user,
    ):
        aws_access_key_id = sqs_user.aws_access_key_id
        aws_secret_access_key = sqs_user.aws_secret_access_key
        conn = AwsSqsConnection(
            config={},
            conn_details={
                "aws_access_key_id": aws_access_key_id,
                "aws_secret_access_key": aws_secret_access_key,
                "endpoint_url": settings.AWS_ENDPOINT,
            },
            params={"queue_name": QUEUE_NAME},
        )
        await conn.connect()
        assert conn.conn is not None
        assert conn.queue_url is not None
        await conn.close()
        assert conn.conn is None
        assert conn.queue_url is None

    @pytest.mark.asyncio
    @pytest.mark.skipif(
        not can_connect_to_sqs(),
        reason="localstack (AWS emulator) is not running.",
    )
    async def test_connection_and_close_mechanism_using_config(self, sqs_user):
        aws_access_key_id = sqs_user.aws_access_key_id
        aws_secret_access_key = sqs_user.aws_secret_access_key
        conn = AwsSqsConnection(
            config={
                "conn_details": {
                    "aws_access_key_id": aws_access_key_id,
                    "aws_secret_access_key": aws_secret_access_key,
                    "endpoint_url": settings.AWS_ENDPOINT,
                },
            },
            conn_details={},
            params={"queue_name": QUEUE_NAME},
        )
        await conn.connect()
        assert conn.conn is not None
        assert conn.queue_url is not None
        await conn.close()
        assert conn.conn is None
        assert conn.queue_url is None

    def test_if_queue_url_preferred_over_queue_name(self):
        conn = AwsSqsConnection(
            config={},
            conn_details={"endpoint_url": "http://test_endpoint"},
            params={"queue_url": "http://test_queue_1", "queue_name": "bad"},
        )
        assert conn.get_queue_url() == "http://test_queue_1"

    @pytest.mark.asyncio
    async def test_get_queue_url_works_using_queue_name(self):
        user = SQSUser()
        url = SQSQueue(user, "my-queue").create_queue()
        conn = AwsSqsConnection(
            config={},
            conn_details={
                "endpoint_url": settings.AWS_ENDPOINT,
                "aws_access_key_id": user.aws_access_key_id,
                "aws_secret_access_key": user.aws_secret_access_key,
            },
            params={"queue_name": "my-queue"},
        )
        await conn.connect()
        assert conn.queue_url == url


@pytest.mark.skipif(
    not can_connect_to_sqs(),
    reason="localstack (AWS emulator) is not running.",
)
class TestAwsSqsBroker:
    """Tests for the `AwsSqsBroker` class."""

    @pytest.mark.asyncio
    async def test_message_can_be_sent(self):
        broker = AwsSqsBroker(
            broker_key="aws_sqs",
            conn_details={},
            params={},
        )
        await broker.send_message("test_message")
