import json
import typing as _t

from action_triggers.message_broker.broker import get_broker_class
from action_triggers.models import MessageBrokerQueue


def process_msg_broker_queue(
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

    broker_class = get_broker_class(msg_broker_queue.name)
    broker_class(
        msg_broker_queue.name,
        msg_broker_queue.conn_details,
        msg_broker_queue.parameters,
    ).send_message(json.dumps(payload))
