from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.contrib.auth import get_user_model

from . import conf
from .enums import HTTPMethodChoices, SignalChoices

UserModel = get_user_model()


class Config(models.Model):
    """Model to represent the action triggers configuration."""

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
    models = models.ManyToManyField(
        ContentType,
        related_name="configs",
        verbose_name=_("Models"),
        help_text=_("Models to trigger actions on."),
    )

    class Meta:
        verbose_name = _("Configuration")
        verbose_name_plural = _("Configurations")
        db_table = conf.DB_TABLE_PREFIX + "config"

    def __str__(self) -> str:
        return f"Config {self.id}"


class Webhook(models.Model):
    """Model to represent the webhook configuration."""

    config_id = models.ForeignKey(
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


class MessageBrokerQueue(models.Model):
    """Model to represent a message broker queue configuration."""

    config_id = models.ForeignKey(
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

    config_id = models.ForeignKey(
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
