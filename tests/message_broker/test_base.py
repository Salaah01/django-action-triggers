"""Tests for `action_triggers.message_broker.base` module."""

from types import SimpleNamespace

import pytest
from django.conf import settings

from action_triggers.message_broker.base import BrokerBase, ConnectionBase
from action_triggers.exceptions import ConnectionValidationError


class MockConnection(ConnectionBase):
    required_conn_detail_fields = []
    required_params_fields = []

    async def connect(self):
        pass

    async def close(self):
        pass


class MockBroker(BrokerBase):
    conn_class = MockConnection
    sent_message = None

    async def _send_message_impl(self, conn, message):
        self.sent_message = message


@pytest.mark.django_db
class TestConnectionBase:
    """Tests for the `ConnectionBase` class."""

    def test_on_init_validation_is_run(self):
        class TestConnection(MockConnection):
            i = 1

            def validate(self):
                self.i += 1

        conn = TestConnection({}, {}, {})

        assert conn.i == 2

    @pytest.mark.asyncio
    async def test_can_be_used_as_a_context_manager(self):
        class TestConnection(MockConnection):
            connected = False
            closed = False

            def __init__(self, config, conn_details, params):
                super().__init__(config, conn_details, params)
                self._conn = SimpleNamespace(
                    close=lambda: setattr(self, "closed", True)
                )

            async def connect(self):
                self.connected = True

            async def close(self):
                self.closed = True

            def validate(self):
                pass

        async with TestConnection({}, {}, {}) as conn:
            assert conn.connected is True

        assert conn.closed is True

    def test_validate_connection_details_cannot_be_overwritten(self):
        with pytest.raises(ConnectionValidationError) as exc:
            MockConnection(
                {"conn_details": {"host": "localhost"}},
                {"host": "new_localhost"},
                {},
            )

        assert exc.value.as_dict() == {
            "connection_params": {
                "host": ["Connection details for host cannot be overwritten."]
            },
            "params": {},
        }

    def test_validate_params_cannot_be_overwritten(self):
        with pytest.raises(ConnectionValidationError) as exc:
            MockConnection(
                {"params": {"queue": "test_queue"}},
                {},
                {"queue": "new_queue"},
            )

        assert exc.value.as_dict() == {
            "connection_params": {},
            "params": {"queue": ["queue cannot be overwritten."]},
        }


@pytest.mark.django_db
class TestBrokerBase:
    """Tests for the `BrokerBase` class."""

    @pytest.mark.parametrize(
        (
            "override_conn_details",
            "override_params",
            "expected_conn_details",
            "expected_params",
        ),
        (
            (
                {},
                {},
                settings.DEFAULT_RABBIT_MQ_CONN_DETAILS,
                {"queue": "test_queue_1"},
            ),
            (
                {"host": "hijacked-host", "name": "rabbitmq"},
                {"queue": "quirky-queue", "exchange": "test_exchange"},
                {
                    **settings.DEFAULT_RABBIT_MQ_CONN_DETAILS,
                    "name": "rabbitmq",
                },
                {"queue": "test_queue_1", "exchange": "test_exchange"},
            ),
        ),
    )
    def test_conn_detail_and_params_cannot_be_overridden(
        self,
        override_conn_details,
        override_params,
        expected_conn_details,
        expected_params,
    ):
        broker = MockBroker(
            "rabbitmq_1",
            override_conn_details,
            override_params,
        )

        assert broker.conn_details == expected_conn_details
        assert broker.params == expected_params

    @pytest.mark.asyncio
    async def test_send_message_calls_send_msg_impl(self):
        broker = MockBroker("rabbitmq_1", {}, {})
        await broker.send_message("test_message")

        assert broker.sent_message == "test_message"

    def test_init_conn_details_dynamically_updated(self):
        conn_details = {
            "host": "localhost",
            "port": 5672,
            "username": "guest",
            "api": "Bearer: {{ tests.test_dynamic_loading.get_api_token }}",
        }
        broker = MockBroker("kafka_1", conn_details, {})

        assert broker.conn_details["host"] == "localhost"
        assert broker.conn_details["port"] == 5672
        assert broker.conn_details["username"] == "guest"
        assert broker.conn_details["api"] == "Bearer: test_token"

    def test_init_param_dynamically_updated(self):
        params = {
            "queue": "test_queue",
            "api": "Bearer: {{ tests.test_dynamic_loading.get_api_token }}",
        }
        broker = MockBroker("kafka_1", {}, params)

        assert broker.params["queue"] == "test_queue"
        assert broker.params["api"] == "Bearer: test_token"
