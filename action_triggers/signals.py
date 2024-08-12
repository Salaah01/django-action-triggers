"""Dynamically create signals for each model so that the relevant actions can
be triggered.
"""

import typing as _t
from functools import partial

from django.db.models import Model, signals
from django.db.models.signals import (
    post_delete,
    post_save,
    pre_delete,
    pre_save,
)

from action_triggers.enums import SignalChoices
from action_triggers.models import Config


def signal_callback(
    instance: _t.Type[Model],
    signal: signals.ModelSignal,
    **kwargs,
) -> None:
    """Callback function to be called when a signal is triggered.
    The callback function will dispatch the relevant signals for the
    model.

    Args:
        instance: The model instance which triggered the signal.
        signal: The signal which was triggered.
        **kwargs: Additional keyword arguments.

    Returns:
        None
    """
    configs = (
        Config.objects.for_signal(SignalChoices.for_signal(signal))
        .for_model(instance)
        .active()
    )

    for config in configs:
        print("Signal triggered for config:", config)


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