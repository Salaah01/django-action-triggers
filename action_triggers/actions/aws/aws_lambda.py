"""Module to support sending messages to AWS Lambda."""

import asyncio
import json
from functools import partial

from action_triggers.actions.error import ActionError
from action_triggers.base.config import ActionTriggerActionBase
from action_triggers.config_required_fields import HasField
from action_triggers.core.config import ConnectionCore
from action_triggers.enums import ActionTriggerType
from action_triggers.utils.module_import import MissingImportWrapper

try:
    import boto3  # type: ignore[import]
except ImportError:  # pragma: no cover
    boto3 = MissingImportWrapper("boto3")  # type: ignore[assignment]


class AwsLambdaConnection(ConnectionCore):
    """Connection class for AWS Lambda."""

    error_class = ActionError
    required_conn_detail_fields = (HasField("endpoint_url", str),)
    required_params_fields = (HasField("FunctionName", str),)

    async def connect(self) -> None:
        """Connect to the AWS Lambda service."""

        self.conn = boto3.client("lambda", **self.conn_details)

    async def close(self) -> None:
        """Close the connection to the AWS Lambda service."""

        self.conn = None


class AwsLambdaAction(ActionTriggerActionBase):
    """Action class for AWS Lambda."""

    conn_class = AwsLambdaConnection
    action_trigger_type = ActionTriggerType.ACTIONS

    async def _send_message_impl(
        self,
        conn: AwsLambdaConnection,
        message: str,
    ) -> None:
        """Invoke the AWS Lambda function.

        :param conn: The connection to the AWS Lambda service.
        :param message: The message to send.
        """

        loop = asyncio.get_event_loop()
        await loop.run_in_executor(
            None,
            partial(
                conn.conn.invoke,
                Payload=json.dumps(message),
                **conn.params,
            ),
        )
