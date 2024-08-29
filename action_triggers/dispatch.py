"""Handles the dispatching of actions to the appropriate action handler."""

import logging

from django.db.models import Model

from action_triggers.models import Config
from action_triggers.msg_broker_queues import process_msg_broker_queue
from action_triggers.payload import get_payload_generator
from action_triggers.webhooks import WebhookProcessor

logger = logging.getLogger(__name__)


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

    for webhook in config.webhooks.all():
        try:
            WebhookProcessor(webhook, payload).process()
        except Exception as e:
            logger.error(
                "Error processing webhook %s for config %s: %s",
                webhook.id,
                config.id,
                e,
            )

    for msg_broker_queue in config.message_broker_queues.all():
        try:
            process_msg_broker_queue(msg_broker_queue, payload)
        except Exception as e:
            logger.error(
                "Error processing message broker queue %s for config %s: %s",
                msg_broker_queue.id,
                config.id,
                e,
            )
