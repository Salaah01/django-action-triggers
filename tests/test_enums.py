"""Tests for the `enums` module."""

import pytest
from django.db.models.signals import (
    m2m_changed,
    post_delete,
    post_save,
    pre_delete,
    pre_save,
)

from action_triggers.enums import SignalChoices


class TestSignalChoices:
    @pytest.mark.parametrize(
        "signal, expected",
        (
            (pre_save, SignalChoices.PRE_SAVE),
            (post_save, SignalChoices.POST_SAVE),
            (pre_delete, SignalChoices.PRE_DELETE),
            (post_delete, SignalChoices.POST_DELETE),
        ),
    )
    def test_for_signal_returns_correct_enum(self, signal, expected):
        assert SignalChoices.for_signal(signal) == expected

    def test_unsupported_signal_raises_value_error(self):
        with pytest.raises(KeyError):
            SignalChoices.for_signal(m2m_changed)
