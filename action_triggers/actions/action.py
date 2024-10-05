import asyncio
import json
import logging
import traceback
import typing as _t

from django.conf import settings

from action_triggers.actions.aws.aws_lambda import AwsLambdaAction
from action_triggers.actions.enums import ActionType
from action_triggers.base.config import ActionTriggerActionBase
from action_triggers.models import Action

logger = logging.getLogger(__name__)


def get_action_class(action_name: str) -> _t.Type[ActionTriggerActionBase]:
    """Get the action class based on the action name.

    :param action_name: The name of the action.
    :return: The action class.
    :raises ValueError: If the action name is not found.
    """

    action_type_to_class_map: _t.Dict[
        str, _t.Type[ActionTriggerActionBase]
    ] = {
        ActionType.AWS_LAMBDA.name: AwsLambdaAction,
    }

    return action_type_to_class_map[
        _t.cast(
            str,
            settings.ACTION_TRIGGERS["actions"][action_name]["action_type"],  # type: ignore[index]  # noqa E501
        ).upper()
    ]


async def process_action(action: Action, payload: _t.Union[str, dict]) -> None:
    """Process the action for the action trigger.

    :param action: The action object to process.
    :param payload: The payload to send to the action.
    :return: None
    """

    try:
        action_class = get_action_class(action.name)
        action_obj = action_class(
            action.name,
            action.conn_details,
            action.parameters,
        )

        await asyncio.wait_for(
            action_obj.send_message(json.dumps(payload)),
            action.timeout_respecting_max,
        )
    except Exception as e:
        logger.error(
            "Error processing action %s for config %s:Exception Type:%s\nTraceback:\n%s",  # noqa: E501
            action.id,
            action.config.id,
            type(e),
            traceback.format_exc(),
        )
