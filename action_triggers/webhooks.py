import typing as _t
from action_triggers.models import Webhook


def process_webhook(webhook: Webhook, payload: _t.Union[str, dict]) -> None:
    """Process the webhook action and send the payload to the webhook URL.

    Args:
        webhook: The webhook object to process.
        payload: The payload to send to the webhook.

    Returns:
        None
    """
    pass
