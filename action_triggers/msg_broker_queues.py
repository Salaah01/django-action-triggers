import typing as _t

from action_triggers.models import MessageBrokerQueue


def process_msg_broker_queue(
    msg_broker_queue: MessageBrokerQueue,
    payload: _t.Union[str, dict],
) -> None:
    """Process the action for the message broker queue.

    Args:
        msg_broker_queue: The message broker queue object to process.
        payload: The payload to send to the message broker queue.

    Returns:
        None
    """