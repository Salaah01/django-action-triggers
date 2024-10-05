"""Module to support sending messages to AWS Lambda."""

import asyncio
from action_triggers.utils.module_import import MissingImportWrapper
from action_triggers.core.config import ConnectionCore
from action_triggers.actions.error import ActionError
from action_triggers.config_required_fields import HasField

try:
    import boto3  # type: ignore[import]
except ImportError:  # pragma: no cover
    boto3 = MissingImportWrapper("boto3")  # type: ignore[assignment]


class AwsLambdaConnection(ConnectionCore):
    """Connection class for AWS Lambda."""

    error_class = ActionError
    required_conn_detail_fields = (HasField("endpoint_url", str),)
    required_param_fields = (HasField("FunctionName", str),)

    async def connect(self) -> None:
        """Connect to the AWS Lambda service."""

        self.conn = boto3.client("lambda", **self.conn_details)

    async def close(self) -> None:
        """Close the connection to the AWS Lambda service."""

        self.conn = None
