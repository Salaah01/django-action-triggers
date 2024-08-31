"""Handles the dispatching of actions to the appropriate action handler."""

import asyncio
import logging
import typing as _t

from django.db.models import Model

from action_triggers.models import Config, Webhook
from action_triggers.msg_broker_queues import process_msg_broker_queue
from action_triggers.payload import get_payload_generator
from action_triggers.webhooks import WebhookProcessor

logger = logging.getLogger(__name__)


async def process_webhook(
    config: Config,
    instance: Webhook,
    payload: _t.Union[dict, str],
) -> None:
    """Process the webhook for the given config and instance.

    :param config: The configuration object.
    :param instance: The webhook instance to process.
    :param payload: The payload to send with the webhook.
    :return: None
    """

    try:
        processor = WebhookProcessor(instance, payload)
        await processor()
    except Exception as e:
        logger.error(
            "Error processing webhook %s for config %s: %s",
            instance.id,
            config.id,
            e,
        )


def handle_action(config: Config, instance: Model) -> None:
    """Handle the action for the given config and instance.

    For each webhook and message broker queue associated with the config,
    the payload is generated and sent to the respective handlers.

    :param config: The configuration object.
    :param instance: The model instance which triggered the action.
    :return: None
    """

    payload_gen = get_payload_generator(config)
    payload = payload_gen(instance)
    tasks = []
    for webhook in config.webhooks.all():
        tasks.append(process_webhook(config, webhook, payload))

    for msg_broker_queue in config.message_broker_queues.all():
        tasks.append(process_msg_broker_queue(msg_broker_queue, payload))

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(asyncio.gather(*tasks, return_exceptions=True))
