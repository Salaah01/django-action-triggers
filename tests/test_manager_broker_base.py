"""Tests for `action_triggers.message_broker.base` module."""

from types import SimpleNamespace

import pytest

from action_triggers.message_broker.base import BrokerBase, ConnectionBase


class TestConnectionBase:
    """Tests for the `ConnectionBase` class."""

    def test_on_init_validation_is_run(self):
        class TestConnection(ConnectionBase):
            i = 1

            def validate(self):
                self.i += 1

            def connect(self):
                pass

        conn = TestConnection({}, {})

        assert conn.i == 2

    def test_can_be_used_as_a_context_manager(self):
        class TestConnection(ConnectionBase):
            connected = False
            exited = False
            closed = False

            def __init__(self, conn_details, params):
                super().__init__(conn_details, params)
                self._conn = SimpleNamespace(
                    close=lambda: setattr(self, "closed", True)
                )

            def connect(self):
                self.connected = True

            def close(self):
                super().close()
                self.exited = True

            def validate(self):
                pass

        with TestConnection({}, {}) as conn:
            assert conn.connected is True

        assert conn.exited is True
        assert conn.closed is True


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
                {"host": "localhost", "port": 5672},
                {"queue": "test_queue_1"},
            ),
            (
                {"host": "localhost2", "name": "rabbitmq"},
                {"queue": "test_queue_2", "exchange": "test_exchange"},
                {"host": "localhost2", "port": 5672, "name": "rabbitmq"},
                {"queue": "test_queue_2", "exchange": "test_exchange"},
            ),
        ),
    )
    def test_params_can_be_overridden(
        self,
        override_conn_details,
        override_params,
        expected_conn_details,
        expected_params,
    ):
        class MockConnection(ConnectionBase):
            def validate(self):
                pass

            def connect(self):
                pass

        class NockBroker(BrokerBase):
            conn_class = MockConnection

            def _send_message_impl(self, conn, message):
                pass

        broker = NockBroker(
            "rabbitmq_1",
            override_conn_details,
            override_params,
        )

        assert broker.conn_details == expected_conn_details
        assert broker.params == expected_params

    def test_send_message_calls_send_msg_impl(self):
        class MockConnection(ConnectionBase):
            def validate(self):
                pass

            def connect(self):
                pass

        class NockBroker(BrokerBase):
            conn_class = MockConnection
            sent_message = None

            def _send_message_impl(self, conn, message):
                self.sent_message = message

        broker = NockBroker("rabbitmq_1", {}, {})
        broker.send_message("test_message")

        assert broker.sent_message == "test_message"