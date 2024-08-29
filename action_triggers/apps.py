from django.apps import AppConfig, apps
from django.conf import settings

from action_triggers.checks import (
    check_action_triggers_set,
    warning_whitelist_content_types_set,
)


class ActionTriggersConfig(AppConfig):
    name = "action_triggers"
    verbose_name = "Action Triggers"

    def ready(self):
        """Register the models with the registry."""

        check_action_triggers_set(app_configs=None)
        warning_whitelist_content_types_set(app_configs=None)

        self._register_models()
        self._setup_signals()

    @staticmethod
    def _register_models():
        """Register the models with the registry."""
        from action_triggers.registry import add_to_registry

        models = apps.get_models()
        choices = set(
            settings.ACTION_TRIGGERS.get("whitelisted_content_types", {})
        )
        if choices:
            models = filter(
                lambda model: f"{model._meta.app_label}.{model._meta.model_name}"  # noqa: E501
                in choices,
                models,
            )

        for model in models:
            add_to_registry(model)

    @staticmethod
    def _setup_signals():
        """Setup the signals for the registered models."""
        from . import signals

        signals.setup()
