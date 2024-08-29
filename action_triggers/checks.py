from django.core.checks import Error, register, Warning, Tags
from django.conf import settings


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
