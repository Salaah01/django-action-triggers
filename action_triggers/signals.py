"""Dynamically create signals for each model so that the relevant actions can
be triggered.
"""

from django.db.models.signals import (
    post_save,
    post_delete,
    pre_save,
    post_save,
)
from functools import partial
from django.db.models import Model, signals


def signal_callback(
    instance: Model,
    signals: signals.ModelSignal,
    **kwargs,
) -> None:
    """Callback function to be called when a signal is triggered.
    The callback function will dispatch the relevant signals for the
    model.
    """
