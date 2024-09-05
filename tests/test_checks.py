"""Tests for the "checks" module."""

from django.core.checks import Error, Warning
from django.test import override_settings

from action_triggers.checks import (
    check_action_trigger_settings_set,
    check_action_triggers_set,
    check_broker_types_are_valid,
    warning_timeout_settings_set,
    warning_whitelist_content_types_set,
    warning_whitelisted_webhook_endpoint_patterns_not_provided,
)


class TestCheckActionTriggersSet:
    """Tests for the `check_action_triggers_set` function."""

    @override_settings(ACTION_TRIGGERS=None)
    def test_unset_action_triggers_shows_error(self):
        result = check_action_triggers_set(app_configs=None)

        assert len(result) == 1
        assert isinstance(result[0], Error)
        assert result[0].id == "action_triggers.E001"
        assert result[0].msg == "ACTION_TRIGGERS not set in settings.py"
        assert result[0].hint == "Add ACTION_TRIGGERS to settings.py"

    def test_set_action_triggers_no_error(self):
        result = check_action_triggers_set(app_configs=None)

        assert result == []


class TestCheckActionTriggerSettingsSet:
    """Tests for the `check_action_trigger_settings_set` function."""

    @override_settings(ACTION_TRIGGER_SETTINGS=None)
    def test_unset_action_trigger_settings_shows_error(self):
        result = check_action_trigger_settings_set(app_configs=None)

        assert len(result) == 1
        assert isinstance(result[0], Error)
        assert result[0].id == "action_triggers.E004"
        assert (
            result[0].msg == "ACTION_TRIGGER_SETTINGS not set in settings.py"
        )
        assert result[0].hint == "Add ACTION_TRIGGER_SETTINGS to settings.py"

    def test_set_action_trigger_settings_no_error(self):
        result = check_action_trigger_settings_set(app_configs=None)

        assert result == []


class TestCheckBrokerTypesAreValid:
    """Tests for the `check_broker_types_are_valid` function."""

    @override_settings(ACTION_TRIGGERS=None)
    def test_unset_action_triggers_do_nothing(self):
        result = check_broker_types_are_valid(app_configs=None)

        assert result == []

    @override_settings(
        ACTION_TRIGGERS={
            "brokers": {
                "broker_1": {"broker_type": "invalid"},
                "broker_2": {"broker_type": "kafka"},
            }
        }
    )
    def test_invalid_broker_type_shows_error(self):
        result = check_broker_types_are_valid(app_configs=None)

        assert len(result) == 1
        assert isinstance(result[0], Error)
        assert result[0].id == "action_triggers.E003"
        assert result[0].msg == (
            "Invalid `broker_type` provided for broker broker_1: invalid. "
            "Valid broker types are: ['rabbitmq', 'kafka', 'redis', 'aws_sqs']"
        )
        assert (
            result[0].hint
            == "Use valid broker types in ACTION_TRIGGERS['brokers'][broker_1]"
        )

    @override_settings(
        ACTION_TRIGGERS={
            "brokers": {
                "broker_1": {},
                "broker_2": {"broker_type": "kafka"},
            }
        }
    )
    def test_missing_broker_type_shows_error(self):
        result = check_broker_types_are_valid(app_configs=None)

        assert len(result) == 1
        assert isinstance(result[0], Error)
        assert result[0].id == "action_triggers.E002"
        assert result[0].msg == "`broker_type` not set for broker broker_1"
        assert (
            result[0].hint
            == "Set `broker_type` in ACTION_TRIGGERS['brokers'][broker_1]"
        )

    @override_settings(
        ACTION_TRIGGERS={
            "brokers": {
                "broker_1": {"broker_type": "rabbitmq"},
                "broker_2": {"broker_type": "kafka"},
            }
        }
    )
    def test_valid_broker_types_no_error(self):
        result = check_broker_types_are_valid(app_configs=None)

        assert result == []


class TestWarningWhitelistContentTypesSet:
    """Tests for the `warning_whitelist_content_types_set` function."""

    @override_settings(ACTION_TRIGGERS={"abc": []})
    def test_unset_whitelist_content_types_shows_warning(self):
        result = warning_whitelist_content_types_set(app_configs=None)

        assert len(result) == 1
        assert isinstance(result[0], Warning)
        assert result[0].id == "action_triggers.W001"

    def test_set_whitelist_content_types_no_warning(self):
        result = warning_whitelist_content_types_set(app_configs=None)

        assert result == []

    @override_settings(ACTION_TRIGGERS=None)
    def test_if_no_action_triggers_do_nothing(self):
        """Note: We are doing nothing here as the check for the action triggers
        is done by another check.
        """
        result = warning_whitelist_content_types_set(app_configs=None)

        assert result == []


class TestWarningWhitelistedWebhookEndpointPatternsNotProvided:
    """Tests for the
    `warning_whitelisted_webhook_endpoint_patterns_not_provided` function.
    """

    @override_settings(ACTION_TRIGGERS={"abc": []})
    def test_unset_no_whitelisted_webhook_endpoint_patterns_shows_warning(
        self,
    ):
        result = warning_whitelisted_webhook_endpoint_patterns_not_provided(
            app_configs=None
        )

        assert len(result) == 1
        assert isinstance(result[0], Warning)
        assert result[0].id == "action_triggers.W002"

    def test_set_whitelisted_webhook_endpoint_patterns_no_warning(self):
        result = warning_whitelisted_webhook_endpoint_patterns_not_provided(
            app_configs=None
        )

        assert result == []

    @override_settings(ACTION_TRIGGERS=None)
    def test_if_no_action_triggers_do_nothing(self):
        """Note: We are doing nothing here as the check for the action triggers
        is done by another check.
        """
        result = warning_whitelisted_webhook_endpoint_patterns_not_provided(
            app_configs=None
        )

        assert result == []


class TestWarningTimeoutSettingsSet:
    """Tests for the `warning_timeout_settings_set` function."""

    @override_settings(ACTION_TRIGGER_SETTINGS={})
    def test_unset_timeout_settings_shows_warning(self):
        result = warning_timeout_settings_set(app_configs=None)

        assert len(result) == 2
        assert isinstance(result[0], Warning)
        assert result[0].id == "action_triggers.W003"

    @override_settings(
        ACTION_TRIGGER_SETTINGS={
            "MAX_BROKER_TIMEOUT": 10.0,
            "MAX_WEBHOOK_TIMEOUT": 20.0,
        }
    )
    def test_set_timeout_settings_no_warning(self):
        result = warning_timeout_settings_set(app_configs=None)

        assert result == []

    @override_settings(ACTION_TRIGGER_SETTINGS=None)
    def test_no_warnings_if_main_dict_missing(self):
        """Note: We are doing nothing here as the check for the action trigger
        settings is done by another check.
        """
        result = warning_timeout_settings_set(app_configs=None)

        assert result == []
