from collections import namedtuple

import django
import pytest
from django.apps import apps
from django.core.management import call_command

django.setup()


from django.contrib.contenttypes.models import ContentType  # noqa: E402
from model_bakery import baker  # noqa: E402

from action_triggers.enums import SignalChoices  # noqa: E402
from action_triggers.registry import add_to_registry  # noqa: E402
from action_triggers.models import (  # noqa: E402
    Config,
    Webhook,
    ConfigSignal,
    MessageBrokerQueue,
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
    # add_to_registry(CustomerModel)
    # add_to_registry(CustomerOrderModel)
    # add_to_registry(M2MModel)
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
def rabbitmq_message_plain_payload(config):
    return baker.make(
        MessageBrokerQueue,
        name="rabbitmq_1",
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
    rabbitmq_message_plain_payload,
):
    return namedtuple("ConfigContext", ["config", "signal", "payload"])(
        config,
        customer_post_save_signal,
        rabbitmq_message_plain_payload,
    )
