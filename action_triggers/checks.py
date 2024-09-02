from django.conf import settings
from django.core.checks import Error, Tags, Warning, register

from action_triggers.message_broker.enums import BrokerType

__all__ = [
    "check_action_triggers_set",
    "check_broker_types_are_valid",
    "warning_whitelist_content_types_set",
    "warning_whitelisted_webhook_endpoint_patterns_not_provided",
]


@register(Tags.compatibility)
def check_action_triggers_set(app_configs, **kwargs):
    """Check that `ACTION_TRIGGERS` has been set.

    :param app_configs: The app configuration.
    :param kwargs: Additional keyword arguments.
    """
    if getattr(settings, "ACTION_TRIGGERS", None) is None:
        return [
            Error(
                "ACTION_TRIGGERS not set in settings.py",
                hint="Add ACTION_TRIGGERS to settings.py",
                id="action_triggers.E001",
            )
        ]
    return []


@register(Tags.compatibility)
def check_action_trigger_settings_set(app_configs, **kwargs):
    """Check that `ACTION_TRIGGER_SETTINGS` has been set.

    :param app_configs: The app configuration.
    :param kwargs: Additional keyword arguments.
    """
    if getattr(settings, "ACTION_TRIGGER_SETTINGS", None) is None:
        return [
            Error(
                "ACTION_TRIGGER_SETTINGS not set in settings.py",
                hint="Add ACTION_TRIGGER_SETTINGS to settings.py",
                id="action_triggers.E004",
            )
        ]
    return []


@register(Tags.compatibility)
def check_broker_types_are_valid(app_configs, **kwargs):
    """Test that the `broker_type`s provied in `ACTION_TRIGGERS.brorkers` are
    valid.

    :param app_config: The app configuration.
    :param kwargs: Additional keyword arguments.
    """
    if getattr(settings, "ACTION_TRIGGERS", None) is None:
        return []

    valid_broker_types = [
        broker_type.value.lower() for broker_type in BrokerType
    ]

    errors = []
    invalid_msg = (
        "Invalid `broker_type` provided for broker {broker_key}: "
        "{broker_type}. Valid broker types are: {valid_broker_types}"
    )
    invalid_hint = (
        "Use valid broker types in ACTION_TRIGGERS['brokers'][{broker_key}]"
    )
    missing_msg = "`broker_type` not set for broker {broker_key}"
    missing_hint = (
        "Set `broker_type` in ACTION_TRIGGERS['brokers'][{broker_key}]"
    )

    brokers = settings.ACTION_TRIGGERS.get("brokers", {})

    for broker_key, broker_settings in brokers.items():
        broker_type = broker_settings.get("broker_type")
        if broker_type is None:
            errors.append(
                Error(
                    missing_msg.format(broker_key=broker_key),
                    hint=missing_hint.format(broker_key=broker_key),
                    id="action_triggers.E002",
                )
            )
        elif broker_type.lower() not in valid_broker_types:
            errors.append(
                Error(
                    invalid_msg.format(
                        broker_key=broker_key,
                        broker_type=broker_type,
                        valid_broker_types=valid_broker_types,
                    ),
                    hint=invalid_hint.format(broker_key=broker_key),
                    id="action_triggers.E003",
                )
            )
    return errors


@register(Tags.security)
def warning_whitelist_content_types_set(app_configs, **kwargs):
    """Check that `ACTION_TRIGGERS.whitelisted_content_types` has been set.
    If it has not, show a depreciation warning that in the future, the allowed
    content types will be set in the action trigger configuration.

    :param app_configs: The app configuration.
    :param kwargs: Additional keyword arguments.
    """

    if getattr(settings, "ACTION_TRIGGERS", None) is None:
        return []

    if "whitelisted_content_types" not in settings.ACTION_TRIGGERS:
        msg = (
            "ACTION_TRIGGERS.whitelisted_content_types not set in "
            "settings.py. This will be required in the future where the "
            "allowed content types will need be set in the action trigger "
            "configuration."
        )
        hint = "Add ACTION_TRIGGERS.whitelisted_content_types to settings.py"
        return [
            Warning(
                msg,
                hint=hint,
                id="action_triggers.W001",
            )
        ]
    return []


@register(Tags.security)
def warning_whitelisted_webhook_endpoint_patterns_not_provided(
    app_configs, **kwargs
):
    """Check that `ACTION_TRIGGERS.whitelisted_webhook_endpoint_patterns` has
    been set. If it has not, show a message that any webhook endpoint will be
    allowed and that this is a security risk.

    :param app_configs: The app configuration.
    :param kwargs: Additional keyword arguments.
    """

    if getattr(settings, "ACTION_TRIGGERS", None) is None:
        return []

    if "whitelisted_webhook_endpoint_patterns" not in settings.ACTION_TRIGGERS:
        msg = (
            "ACTION_TRIGGERS.whitelisted_webhook_endpoint_patterns not set in "
            "settings.py. This means that any webhook endpoint will be "
            "allowed which is a security risk. In the future, this will be "
            "required to be set."
        )
        hint = (
            "Add ACTION_TRIGGERS.whitelisted_webhook_endpoint_patterns to "
            "settings.py"
        )
        return [
            Warning(
                msg,
                hint=hint,
                id="action_triggers.W002",
            )
        ]
    return []


@register(Tags.compatibility)
def warning_timeout_settings_set(app_configs, **kwargs):
    """Check if the setting settings are set. If it is not, show a warning that
    it is recommended to set the setting.

    :param app_configs: The app configuration.
    :param kwargs: Additional keyword arguments.
    """

    if getattr(settings, "ACTION_TRIGGER_SETTINGS", None) is None:
        return []

    keys = (
        "MAX_BROKER_TIMEOUT",
        "MAX_WEBHOOK_TIMEOUT",
    )
    errors = []
    msg = (
        "{key} not set in ACTION_TRIGGER_SETTINGS, it is recommended to set "
        "this setting to ensure that the action triggers do not hang by "
        "waiting indefinitely for a response when processing webhooks or "
        "message broker queues."
    )
    hint = "Set {key} in ACTION_TRIGGER_SETTINGS"

    for key in keys:
        if not settings.ACTION_TRIGGER_SETTINGS.get(key):
            errors.append(
                Warning(
                    msg.format(key=key),
                    hint=hint.format(key=key),
                    id="action_triggers.W003",
                )
            )

    return errors
