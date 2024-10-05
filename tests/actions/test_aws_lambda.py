import pytest

from action_triggers.actions.aws.aws_lambda import (
    AwsLambdaAction,
    AwsLambdaConnection,
)
from action_triggers.exceptions import ConnectionValidationError
from tests.utils.aws import (
    CONN_DETAILS,
    LAMBDA_FUNCTION_NAME,
    can_connect_to_localstack,
)

try:
    import boto3  # type: ignore[import-untyped]
except ImportError:
    boto3 = None  # type: ignore[assignment]


class TestAwsLambdaConnection:
    """Tests for the `AwsLambdaConnection` class."""

    def test_raise_exception_if_no_endpoint_url_found(self):
        with pytest.raises(ConnectionValidationError):
            AwsLambdaConnection(
                config={},
                conn_details={},
                params={"FunctionName": "fn"},
            )

    def test_raises_exception_if_no_function_name_found(self):
        with pytest.raises(ConnectionValidationError):
            AwsLambdaConnection(
                config={},
                conn_details={"endpoint_url": "http://test_endpoint"},
                params={},
            )

    def test_passes_when_all_required_fields_exist(self):
        AwsLambdaConnection(
            config={},
            conn_details={"endpoint_url": "http://test_endpoint"},
            params={"FunctionName": "fn"},
        )

    @pytest.mark.asyncio
    async def test_connection_and_close_mechanism_using_conn_details(self):
        conn = AwsLambdaConnection(
            config={},
            conn_details=CONN_DETAILS,
            params={"FunctionName": "fn"},
        )
        await conn.connect()
        assert conn.conn
        await conn.close()
        assert not conn.conn

    @pytest.mark.asyncio
    async def test_connection_and_close_mechanism_using_config(self):
        conn = AwsLambdaConnection(
            config={
                "conn_details": {
                    **CONN_DETAILS,
                },
            },
            conn_details={},
            params={"FunctionName": LAMBDA_FUNCTION_NAME},
        )
        await conn.connect()
        assert conn.conn
        await conn.close()
        assert not conn.conn


@pytest.mark.skipif(
    not can_connect_to_localstack(),
    reason="localstack (AWS emulator) is not running.",
)
class TestAwsLambdaAction:
    """Tests for the `AwsLambdaAction` class."""

    @pytest.mark.asyncio
    async def test_can_send_message(self):
        action = AwsLambdaAction(
            key="aws_lambda",
            config={},
            conn_details=CONN_DETAILS,
            params={"FunctionName": LAMBDA_FUNCTION_NAME},
        )
        await action.send_message("test message")
