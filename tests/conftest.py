import django
import pytest
from django.apps import apps
from django.core.management import call_command

django.setup()


from django.contrib.contenttypes.models import ContentType  # noqa: E402
from model_bakery import baker  # noqa: E402

from action_triggers.models import Config, Webhook  # noqa: E402
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
    return baker.make(Config)


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
