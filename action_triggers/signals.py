"""Dynamically create signals for each model so that the relevant actions can
be triggered.
"""

import logging
from functools import partial

from django.db.models import Model, signals
from django.db.models.signals import (
    post_delete,
    post_save,
    pre_delete,
    pre_save,
)

from action_triggers.dispatch import handle_action
from action_triggers.enums import SignalChoices
from action_triggers.models import Config

logger = logging.getLogger(__name__)


def signal_callback(
    instance: Model,
    signal: signals.ModelSignal,
    **kwargs,
) -> None:
    """Callback function to be called when a signal is triggered.
    The callback function will dispatch the relevant signals for the
    model.

    :param instance: The model instance which triggered the signal.
    :type instance: Model
    :param signal: The signal which was triggered.
    :type signal: signals.ModelSignal
    :param kwargs: Additional keyword arguments.
    :type kwargs: Any
    """
    configs = (
        Config.objects.for_signal(SignalChoices.for_signal(signal))
        .for_model(instance)
        .active()
    )

    for config in configs:
        logger.debug(f"Signal triggered for config: {config}")
        handle_action(config, instance)


def setup() -> None:
    """Connects signals to each model which will trigger the callback function
    when the signal is dispatched.
    """

    from action_triggers.registry import registered_models

    signal_types = (pre_save, post_save, pre_delete, post_delete)
    signal_factory = []

    for model in registered_models.values():
        for signal in signal_types:
            signal_factory.append(
                partial(signal.connect, signal_callback, sender=model)
            )

    for factory in signal_factory:
        factory()
