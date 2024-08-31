import json
import logging
import typing as _t

from action_triggers.message_broker.broker import get_broker_class
from action_triggers.models import MessageBrokerQueue

logger = logging.getLogger(__name__)


async def process_msg_broker_queue(
    msg_broker_queue: MessageBrokerQueue,
    payload: _t.Union[str, dict],
) -> None:
    """Process the action for the message broker queue.

    :param msg_broker_queue: The message broker queue object to process.
    :type msg_broker_queue: MessageBrokerQueue
    :param payload: The payload to send to the message broker queue.
    :type payload: Union[str, dict]
    :return: None
    """

    try:
        broker_class = get_broker_class(msg_broker_queue.name)
        broker = broker_class(
            msg_broker_queue.name,
            msg_broker_queue.conn_details,
            msg_broker_queue.parameters,
        )

        await broker.send_message(json.dumps(payload))
    except Exception as e:
        logger.error(
            "Error processing message broker queue %s for config %s: %s",
            msg_broker_queue.id,
            msg_broker_queue.config.id,
            e,
        )
