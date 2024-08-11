import django
import pytest
from django.core.management import call_command

django.setup()

from tests.models import (CustomerModel, CustomerOrderModel,  # noqa: E402
                          M2MModel, One2OneModel)


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


@pytest.fixture(autouse=True)
def setup_each():
    """Set up the test."""
    yield
    CustomerModel.delete_all()
    CustomerOrderModel.delete_all()
    M2MModel.delete_all()
    One2OneModel.delete_all()
