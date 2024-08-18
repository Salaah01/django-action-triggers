"""Tests for the `message_broker.base` module."""

from action_triggers.message_broker.base import BrokerBase, ConnectionBase


class MockConnectionBase(ConnectionBase):
    """Mock class for testing the `ConnectionBase` class."""

    def validate(self):
        pass

    def connect(self):
        pass


class MockBrokerBase(BrokerBase):
    """Mock class for testing the `BrokerBase` class."""

    conn_class = MockConnectionBase

    def _send_message_impl(self, message: str):
        pass


class TestBrokerBase:
    """Tests for the `BrokerBase` class."""

    def test_init_conn_details_dynamically_updated(self):
        conn_details = {
            "host": "localhost",
            "port": 5672,
            "username": "guest",
            "api": "Bearer: {{ tests.test_dynamic_loading.get_api_token }}",
        }
        broker = MockBrokerBase("kafka_1", conn_details, {})

        assert broker.conn_details["host"] == "localhost"
        assert broker.conn_details["port"] == 5672
        assert broker.conn_details["username"] == "guest"
        assert broker.conn_details["api"] == "Bearer: test_token"

    def test_init_param_dynamically_updated(self):
        params = {
            "queue": "test_queue",
            "api": "Bearer: {{ tests.test_dynamic_loading.get_api_token }}",
        }
        broker = MockBrokerBase("kafka_1", {}, params)

        assert broker.params["queue"] == "test_queue"
        assert broker.params["api"] == "Bearer: test_token"
