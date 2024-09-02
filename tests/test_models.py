"""Tests for the `models` module."""

import itertools

import pytest
from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.test import override_settings
from model_bakery import baker

from action_triggers.enums import SignalChoices
from action_triggers.models import (
    BaseAction,
    Config,
    ConfigSignal,
    MessageBrokerQueue,
    Webhook,
)
from tests.models import CustomerModel, CustomerOrderModel


@pytest.mark.django_db
class TestBaseAction:
    """Tests for the `BaseAction` abstract model."""

    @override_settings(ACTION_TRIGGER_SETTINGS={})
    @pytest.mark.parametrize(
        "model_class,timeout_secs",
        itertools.product(BaseAction.__subclasses__(), [0.0, 10.5, None]),
    )
    def test_timeout_returns_instance_timeout_when_no_default_max_timeout(
        self,
        model_class,
        timeout_secs,
    ):
        instance = baker.make(model_class, timeout_secs=timeout_secs)
        assert instance.timeout_respecting_max == timeout_secs

    @override_settings(
        ACTION_TRIGGER_SETTINGS={
            "MAX_BROKER_TIMEOUT": 10.0,
            "MAX_WEBHOOK_TIMEOUT": 20.0,
        }
    )
    @pytest.mark.parametrize("model_class", BaseAction.__subclasses__())
    def test_timeout_respecting_max_returns_default_max_when_timeout_is_none(
        self,
        model_class,
    ):
        instance = baker.make(model_class, timeout_secs=None)
        assert (
            instance.timeout_respecting_max
            == settings.ACTION_TRIGGER_SETTINGS[
                model_class.TIMEOUT_SETTING_KEY
            ]
        )

    @override_settings(ACTION_TRIGGER_SETTINGS={"MAX_BROKER_TIMEOUT": 10.0})
    @pytest.mark.parametrize(
        "timeout_secs,exp_timeout",
        [(5.0, 5.0), (15.0, 10.0)],
    )
    def test_timeout_respecting_max_returns_correct_timeout(
        self,
        timeout_secs,
        exp_timeout,
    ):
        instance = baker.make(MessageBrokerQueue, timeout_secs=timeout_secs)
        assert instance.timeout_respecting_max == exp_timeout


@pytest.mark.django_db
class TestConfigQuerySet:
    """Tests for the `ConfigQuerySet` custom queryset."""

    @pytest.mark.parametrize("active,num_results", [(True, 1), (False, 0)])
    def test_active_returns_only_active_records(self, active, num_results):
        baker.make(Config, active=active)
        assert Config.objects.active().count() == num_results

    @pytest.mark.parametrize(
        "record_signals,num_results",
        (
            ((SignalChoices.PRE_SAVE, SignalChoices.POST_SAVE), 1),
            (
                (
                    SignalChoices.PRE_SAVE,
                    SignalChoices.POST_SAVE,
                    SignalChoices.POST_SAVE,
                ),
                2,
            ),
            ((SignalChoices.PRE_DELETE, SignalChoices.POST_DELETE), 0),
            ((SignalChoices.POST_SAVE,), 1),
        ),
    )
    def test_for_signal_returns_only_records_for_the_given_signal(
        self,
        record_signals,
        num_results,
    ):
        config = baker.make(Config)
        for signal in record_signals:
            baker.make(ConfigSignal, config=config, signal=signal)

        assert (
            Config.objects.for_signal(SignalChoices.POST_SAVE).count()
            == num_results
        )

    def test_model_returns_records_when_using_model_base(self):
        ct = ContentType.objects.get_for_model(CustomerModel)
        baker.make(Config, content_types=[ct])

        assert Config.objects.for_model(CustomerModel).count() == 1
        assert Config.objects.for_model(CustomerOrderModel).count() == 0

    def test_model_returns_records_when_using_model_instance(self):
        ct = ContentType.objects.get_for_model(CustomerModel)
        baker.make(Config, content_types=[ct])

        customer = CustomerModel.create_record()
        customer_order = CustomerOrderModel.create_record(customer)

        assert Config.objects.for_model(customer).count() == 1
        assert Config.objects.for_model(customer_order).count() == 0


@pytest.mark.django_db
class TestConfig:
    """Tests for the `Config` model."""

    def test_str_returns_a_string_representation_of_the_instance(self):
        assert isinstance(str(baker.make(Config)), str)


@pytest.mark.django_db
class TestWebhook:
    """Tests for the `Webhook` model."""

    def test_str_returns_a_string_representation_of_the_instance(self):
        assert isinstance(str(baker.make(Webhook)), str)

    @pytest.mark.parametrize(
        "url,expected",
        [
            ("http://localhost:8000/webhook/1/", True),
            ("https://localhost:9090/webhook/2", True),
            ("https://example.com/", True),
            ("http://not-allowed.com/", False),
        ],
    )
    def test_is_endpoint_whitelisted_returns_correct_bool(self, url, expected):
        webhook = baker.make(Webhook, url=url)
        assert webhook.is_endpoint_whitelisted() is expected


@pytest.mark.django_db
class TestMessageBrokerQueue:
    """Tests for the `MessageBrokerQueue` model."""

    def test_str_returns_a_string_representation_of_the_instance(self):
        assert isinstance(str(baker.make(MessageBrokerQueue)), str)


@pytest.mark.django_db
class TestConfigSignal:
    """Tests for the `ConfigSignal` model."""

    def test_str_returns_a_string_representation_of_the_instance(self):
        assert isinstance(str(baker.make(ConfigSignal)), str)

    def test_repr_returns_a_string_representation_of_the_instance(self):
        assert isinstance(repr(baker.make(ConfigSignal)), str)
