import pytest

from action_triggers.message_broker.aws_sns import (
    AwsSnsBroker,
    AwsSnsConnection,
)
from action_triggers.message_broker.exceptions import ConnectionValidationError
from tests.utils.aws import (
    TOPIC_ARN,
    CONN_DETAILS,
    SNSTopic,
    can_connect_to_localstack,
)

try:
    import boto3  # type: ignore[import-untyped]
except ImportError:
    boto3 = None  # type: ignore[assignment]


@pytest.fixture(autouse=True, scope="module")
def sns_queue(sns_queue_mod):
    yield sns_queue_mod


@pytest.mark.skipif(
    not can_connect_to_localstack(),
    reason="localstack (AWS emulator) is not running.",
)
class TestAwsSnsConnection:
    """Tests for the `AwsSnsConnection` class."""

    def test_raise_exception_if_no_endpoint_url_found(self):
        with pytest.raises(ConnectionValidationError):
            AwsSnsConnection(
                config={},
                conn_details={},
                params={"topic": "topic"},
            )

    def test_raises_exception_if_no_topic_arn_found(self):
        with pytest.raises(ConnectionValidationError):
            AwsSnsConnection(
                config={},
                conn_details=CONN_DETAILS,
                params={},
            )

    def test_passes_when_topic_arn_exists(self):
        AwsSnsConnection(
            config={},
            conn_details=CONN_DETAILS,
            params={"topic_arn": "http://test_topic_1"},
        )

    @pytest.mark.asyncio
    async def test_connection_and_close_mechanism_using_conn_details(
        self,
        sns_queue,
    ):
        conn = AwsSnsConnection(
            config={},
            conn_details=CONN_DETAILS,
            params={"topic_arn": "test_topic_1"},
        )
        await conn.connect()
        assert conn.conn
        await conn.close()
        assert not conn.conn

    @pytest.mark.asyncio
    async def test_connection_and_close_mechanism_using_config(self):
        conn = AwsSnsConnection(
            config={
                "conn_details": {
                    **CONN_DETAILS,
                },
            },
            conn_details={},
            params={"topic_arn": TOPIC_ARN},
        )
        await conn.connect()
        assert conn.conn
        await conn.close()
        assert not conn.conn


@pytest.mark.skipif(
    not can_connect_to_localstack(),
    reason="localstack (AWS emulator) is not running.",
)
class TestAwsSnsBroker:
    """Tests for the `AwsSnsBroker` class."""

    @pytest.mark.asyncio
    async def test_send_message(self, sns_queue):
        broker = AwsSnsBroker(
            broker_key="aws_sns",
            conn_details={},
            params={},
        )
        await broker.send_message("test message")
