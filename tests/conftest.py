from collections import namedtuple

import django
import pytest
from django.apps import apps
from django.core.management import call_command

django.setup()


from django.contrib.auth.models import User  # noqa: E402
from django.contrib.contenttypes.models import ContentType  # noqa: E402
from model_bakery import baker  # noqa: E402

from action_triggers.enums import SignalChoices  # noqa: E402
from action_triggers.models import (  # noqa: E402
    Config,
    ConfigSignal,
    MessageBrokerQueue,
    Webhook,
)
from tests.models import (  # noqa: E402
    CustomerModel,
    CustomerOrderModel,
    M2MModel,
    One2OneModel,
)


@pytest.fixture(autouse=True, scope="session")
def setup():
    """Set up the test module.
    Note: This is using an in-memory SQLite database and so the data will not
    persist between sessions. Therefore, we don't need to worry about cleaning
    up the database.
    """
    call_command("migrate")

    CustomerModel.create_table()
    CustomerOrderModel.create_table()
    M2MModel.create_table()
    One2OneModel.create_table()
    yield


@pytest.fixture(autouse=True, scope="function")
def setup_each():
    """Set up the test."""

    yield
    for model in apps.get_models():
        if model != ContentType:
            model.objects.all().delete()


@pytest.fixture
def config():
    return baker.make(Config, payload={"message": "Hello, World!"})


@pytest.fixture
def webhook(config):
    return baker.make(
        Webhook,
        url="https://example.com/",
        config=config,
    )


@pytest.fixture
def webhook_with_headers(config):
    return baker.make(
        Webhook,
        url="https://example-with-headers.com/",
        config=config,
        headers={"Authorization": "Bearer 123"},
    )


@pytest.fixture
def config_add_customer_ct(config):
    config.content_types.add(ContentType.objects.get_for_model(CustomerModel))


@pytest.fixture
def rabbitmq_1_trigger(config):
    return baker.make(
        MessageBrokerQueue,
        name="rabbitmq_1",
        config=config,
    )


@pytest.fixture
def kafka_1_trigger(config):
    return baker.make(
        MessageBrokerQueue,
        name="kafka_1",
        config=config,
    )


@pytest.fixture
def customer_post_save_signal(config):
    return baker.make(
        ConfigSignal,
        config=config,
        signal=SignalChoices.POST_SAVE,
    )


@pytest.fixture
def customer_rabbitmq_post_save_signal(
    config,
    config_add_customer_ct,
    customer_post_save_signal,
    rabbitmq_1_trigger,
):
    return namedtuple("ConfigContext", ["config", "signal", "trigger"])(
        config,
        customer_post_save_signal,
        rabbitmq_1_trigger,
    )


@pytest.fixture
def customer_kafka_post_save_signal(
    config,
    config_add_customer_ct,
    customer_post_save_signal,
    kafka_1_trigger,
):
    return namedtuple("ConfigContext", ["config", "signal", "trigger"])(
        config,
        customer_post_save_signal,
        kafka_1_trigger,
    )


@pytest.fixture
def customer_webhook_post_save_signal(
    config,
    config_add_customer_ct,
    customer_post_save_signal,
    webhook,
):
    return namedtuple("ConfigContext", ["config", "signal", "trigger"])(
        config,
        customer_post_save_signal,
        webhook,
    )


@pytest.fixture
def full_loaded_config(config):
    config.payload = {"key": "value"}
    config.save()
    
    config.content_types.set(
        [
            ContentType.objects.get_for_model(CustomerModel),
            ContentType.objects.get_for_model(CustomerOrderModel),
        ]
    )

    webhook_1, webhook_2 = baker.make(
        Webhook,
        config=config,
        headers={
            "Content-Type": "application/json",
            "Authorization": "Bearer {{ path.to.token }}",
        },
        _quantity=2,
    )
    message_broker_queue_1, message_broker_queue_2 = baker.make(
        MessageBrokerQueue,
        config=config,
        conn_details={"host": "localhost", "port": 5672},
        parameters={"queue": "test_queue_1"},
        _quantity=2,
    )
    config_signal_1, config_signal_2 = baker.make(
        ConfigSignal,
        config=config,
        _quantity=2,
    )

    return namedtuple(
        "ConfigContext",
        ["config", "webhooks", "mesage_broker_queues", "config_signals"],
    )(
        config,
        [webhook_1, webhook_2],
        [message_broker_queue_1, message_broker_queue_2],
        [config_signal_1, config_signal_2],
    )


@pytest.fixture
def superuser():
    return baker.make(User, is_staff=True, is_superuser=True)
