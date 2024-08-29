import re
import typing as _t

from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from action_triggers import conf
from action_triggers.enums import HTTPMethodChoices, SignalChoices

UserModel = get_user_model()


class ConfigQuerySet(models.QuerySet):
    """Custom queryset for the Config model."""

    def active(self) -> "ConfigQuerySet":
        """Return only active configurations.

        :return: A queryset of active configurations
        :rtype: ConfigQuerySet
        """
        return self.filter(active=True)

    def for_signal(self, signal: SignalChoices) -> "ConfigQuerySet":
        """Return only configurations for the given signal.

        :param signal: The signal to filter by.
        :type signal: SignalChoices

        :return: A queryset of configurations for the given signal
        :rtype: ConfigQuerySet
        """
        return self.filter(config_signals__signal=signal)

    def for_model(
        self,
        model: _t.Union[models.Model, _t.Type[models.Model]],
    ) -> "ConfigQuerySet":
        """Return only configurations for the given model.

        :param model: The model to filter by.
        :type model: Union[models.Model, Type[models.Model]]

        :return: A queryset of configurations for the given model
        :rtype: ConfigQuerySet
        """

        return self.filter(
            content_types=ContentType.objects.get_for_model(model)
        )


class Config(models.Model):
    """Model to represent the action triggers configuration."""

    def _content_type_limit_choices_to() -> dict:  # type: ignore[misc]
        return {
            "id__in": conf.get_content_type_choices().values_list(
                "id", flat=True
            )
        }

    payload = models.JSONField(_("Payload"), blank=True, null=True)
    created_on = models.DateTimeField(_("Created on"), default=timezone.now)
    created_by = models.ForeignKey(
        UserModel,
        on_delete=models.SET_NULL,
        related_name="created_configs",
        verbose_name=_("Created by"),
        null=True,
        blank=True,
    )
    active = models.BooleanField(_("Active"), default=True)
    content_types = models.ManyToManyField(
        ContentType,
        related_name="configs",
        verbose_name=_("Models"),
        help_text=_("Models to trigger actions on."),
        limit_choices_to=_content_type_limit_choices_to,
    )

    objects = ConfigQuerySet.as_manager()  # type: ignore

    class Meta:
        verbose_name = _("Configuration")
        verbose_name_plural = _("Configurations")
        db_table = conf.DB_TABLE_PREFIX + "config"

    def __str__(self) -> str:
        return f"Config {self.id}"


class Webhook(models.Model):
    """Model to represent the webhook configuration."""

    config = models.ForeignKey(
        Config,
        on_delete=models.CASCADE,
        related_name="webhooks",
        verbose_name=_("Configuration"),
    )
    url = models.URLField(_("URL"))
    http_method = models.CharField(
        _("HTTP Method"),
        max_length=10,
        choices=HTTPMethodChoices.choices,
        default=HTTPMethodChoices.POST,
    )
    headers = models.JSONField(_("Headers"), blank=True, null=True)

    class Meta:
        verbose_name = _("Webhook")
        verbose_name_plural = _("Webhooks")
        db_table = conf.DB_TABLE_PREFIX + "webhook"

    def __str__(self) -> str:
        url_repr = self.url[:25]
        if len(self.url) > 25:
            url_repr += "..."

        return f"(Webhook {self.id}) [{self.http_method}] {url_repr}"

    def is_endpoint_whitelisted(self) -> bool:
        """Check if the webhook endpoint is whitelisted.

        :return: True if the endpoint is whitelisted, False otherwise.
        """

        patterns = settings.ACTION_TRIGGERS.get(
            "whitelisted_webhook_endpoint_patterns",
            [".*"],
        )
        for pattern in patterns:
            if re.match(pattern, self.url):
                return True
        else:
            return False


class MessageBrokerQueue(models.Model):
    """Model to represent a message broker queue configuration."""

    config = models.ForeignKey(
        Config,
        on_delete=models.CASCADE,
        related_name="message_broker_queues",
        verbose_name=_("Configuration"),
    )
    name = models.CharField(
        _("Name"),
        max_length=255,
        help_text=_("Corresponds to a queue config in the settings."),
    )
    conn_details = models.JSONField(
        _("Connection Details"),
        blank=True,
        null=True,
        help_text=_("Connection details for the queue."),
    )
    parameters = models.JSONField(
        _("Parameters"),
        blank=True,
        null=True,
        help_text=_("Additional parameters for the queue."),
    )

    class Meta:
        verbose_name = _("Message Broker Queue")
        verbose_name_plural = _("Message Broker Queues")
        db_table = conf.DB_TABLE_PREFIX + "message_broker_queue"

    def __str__(self) -> str:
        return f"(Queue {self.id}) {self.name}"


class ConfigSignal(models.Model):
    """Model to represent the type of signals to trigger for."""

    config = models.ForeignKey(
        Config,
        on_delete=models.CASCADE,
        related_name="config_signals",
        verbose_name=_("Configuration"),
    )
    signal = models.CharField(
        _("Signal"),
        max_length=50,
        choices=SignalChoices.choices,
    )

    class Meta:
        verbose_name = _("Configuration Signal")
        verbose_name_plural = _("Configuration Signals")
        db_table = conf.DB_TABLE_PREFIX + "config_signal"

    def __str__(self) -> str:
        return f"(ConfigSignal {self.id}) {self.signal}"

    def __repr__(self) -> str:
        return f"ConfigSignal({self.id}, {self.signal})"
