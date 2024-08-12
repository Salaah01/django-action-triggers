from django.apps import AppConfig, apps


class ActionTriggersConfig(AppConfig):
    name = "action_triggers"
    verbose_name = "Action Triggers"

    def ready(self):
        """Register the models with the registry."""

        self._register_models()
        self._setup_signals()

    @staticmethod
    def _register_models():
        """Register the models with the registry."""
        from .registry import add_to_registry

        for model in apps.get_models():
            add_to_registry(model)

    @staticmethod
    def _setup_signals():
        """Setup the signals for the registered models."""
        from . import signals

        signals.setup()
