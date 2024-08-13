"""Handles the dispatching of actions to the appropriate action handler."""

from django.db.models import Model

from action_triggers.models import Config
from action_triggers.msg_broker_queues import process_msg_broker_queue
from action_triggers.payload import get_payload_generator
from action_triggers.webhooks import WebhookProcessor


def handle_action(config: Config, instance: Model) -> None:
    payload_gen = get_payload_generator(config)
    payload = payload_gen(instance)
    webhooks = config.webhooks.all()
    for webhook in webhooks:
        WebhookProcessor(webhook, payload).process()
    for msg_broker_queue in config.message_broker_queues.all():
        process_msg_broker_queue(msg_broker_queue, payload)
