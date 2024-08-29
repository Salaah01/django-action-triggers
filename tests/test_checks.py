"""Tests for the "checks" module."""

from django.conf import settings
from django.core.checks import Error, Tags, Warning
from django.test import override_settings
from action_triggers.checks import check_action_triggers_set
from action_triggers.checks import warning_whitelist_content_types_set


class TestCheckActionTriggersSet:
    """Tests for the "check_action_triggers_set" function."""

    @override_settings(ACTION_TRIGGERS=None)
    def test_no_action_triggers_shows_error(self):
        result = check_action_triggers_set(app_configs=None)

        assert len(result) == 1
        assert isinstance(result[0], Error)
        assert result[0].id == "action_triggers.E001"
        assert result[0].msg == "ACTION_TRIGGERS not set in settings.py"
        assert result[0].hint == "Add ACTION_TRIGGERS to settings.py"

    def test_action_triggers_set_no_error(self):
        result = check_action_triggers_set(app_configs=None)

        assert result == []


class TestWarningWhitelistContentTypesSet:
    """Tests for the "warning_whitelist_content_types_set" function."""

    @override_settings(ACTION_TRIGGERS={"abc": []})
    def test_no_whitelist_content_types_shows_warning(self):
        result = warning_whitelist_content_types_set(app_configs=None)

        assert len(result) == 1
        assert isinstance(result[0], Warning)
        assert result[0].id == "action_triggers.W001"

    def test_whitelist_content_types_set_no_warning(self):
        result = warning_whitelist_content_types_set(app_configs=None)

        assert result == []

    @override_settings(ACTION_TRIGGERS=None)
    def test_if_no_action_triggers_do_nothing(self):
        """Note: We are doing nothing here as the check for the action triggers
        is done by another check.
        """
        result = warning_whitelist_content_types_set(app_configs=None)

        assert result == []
