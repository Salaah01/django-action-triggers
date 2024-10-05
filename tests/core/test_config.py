"""Tests for `action_triggers.core.config` module."""

from unittest.mock import Mock, patch

import pytest

from action_triggers.core.config import (
    ConnectionCore,
    validate_required_keys,
    validate_context_not_overwritten,
)
from action_triggers.message_broker.error import MessageBrokerError
from action_triggers.exceptions import ConnectionValidationError
from action_triggers.config_required_fields import HasField


class MockConnection(ConnectionCore):
    error_class = MessageBrokerError
    required_conn_detail_fields = []
    required_params_fields = []

    async def connect(self):
        pass

    async def close(self):
        pass


class TestValidateRequiredKeys:
    """Tests for the `validate_required_keys` function."""

    @pytest.mark.parametrize(
        "required_fields,context,has_error",
        [
            ([HasField("host", str)], {"host": "value_1"}, False),
            ([HasField("host", str)], {"host": 7879}, True),
            (
                [HasField("host", str), HasField("port", int)],
                {"host": "value_1", "port": 7879},
                False,
            ),
            (
                [HasField("host", str), HasField("port", int)],
                {"host": 7879, "port": "port_value"},
                True,
            ),
        ],
    )
    def test_validate_required_keys(self, required_fields, context, has_error):
        mock = Mock()
        validate_required_keys(required_fields, context, mock)

        assert mock.called is has_error


class TestValidateContextNotOverwritten:
    """Tests for the `validate_context_not_overwritten` function."""

    @pytest.mark.parametrize(
        "context,user_context,has_error",
        [
            ({"host": "localhost"}, {"host": "new_localhost"}, True),
            ({"host": "localhost"}, {"host": "localhost"}, False),
            ({}, {"host": "localhost"}, False),
        ],
    )
    def test_validate_context_not_overwritten(
        self,
        context,
        user_context,
        has_error,
    ):
        mock = Mock()
        validate_context_not_overwritten(context, user_context, mock)

        assert mock.called is has_error


@pytest.mark.django_db
class TestConnectionCore:
    """Tests for the `ConnectionCore` class."""

    def test_on_init_validation_is_run(self):
        class TestConnection(MockConnection):
            i = 1

            def validate(self):
                self.i += 1

        conn = TestConnection({}, {}, {})

        assert conn.i == 2

    def test_validate_connection_details_cannot_be_overwritten(self):
        with pytest.raises(ConnectionValidationError) as exc:
            MockConnection(
                {"conn_details": {"host": "localhost"}},
                {"host": "new_localhost"},
                {},
            )

        assert exc.value.as_dict() == {
            "connection_params": {"host": ["host cannot be overwritten."]},
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

    @pytest.mark.parametrize(
        "conn_details,context,has_error",
        [
            ([HasField("host", str)], {"host": "value_1"}, False),
            ([HasField("host", str)], {"host": 7879}, True),
            (
                [HasField("host", str), HasField("port", int)],
                {"host": "value_1", "port": 7879},
                False,
            ),
            (
                [HasField("host", str), HasField("port", int)],
                {"host": 7879, "port": "port_value"},
                True,
            ),
        ],
    )
    def test_validate_required_conn_details_checks_connection_details(
        self,
        conn_details,
        context,
        has_error,
    ):
        class MockValidation(ConnectionCore):
            error_class = MessageBrokerError
            required_conn_detail_fields = conn_details
            required_params_fields = (HasField("queue", str),)

            def validate(self):
                pass

            async def connect(self):
                pass

            async def close(self):
                pass

        instance = MockValidation({}, context, {})
        instance.validate_required_conn_details()

        assert instance._errors.is_valid() is not has_error

    @pytest.mark.parametrize(
        "params,context,has_error",
        [
            ([HasField("queue", str)], {"queue": "value_1"}, False),
            ([HasField("queue", str)], {"queue": 7879}, True),
            (
                [HasField("queue", str), HasField("exchange", str)],
                {"queue": "value_1", "exchange": "exchange_value"},
                False,
            ),
            (
                [HasField("queue", str), HasField("exchange", str)],
                {"queue": 7879, "exchange": "exchange_value"},
                True,
            ),
        ],
    )
    def test_validate_required_params_checks_params(
        self,
        params,
        context,
        has_error,
    ):
        class MockValidation(ConnectionCore):
            error_class = MessageBrokerError
            required_conn_detail_fields = (HasField("host", str),)
            required_params_fields = params

            def validate(self):
                pass

            async def connect(self):
                pass

            async def close(self):
                pass

        instance = MockValidation({}, {}, context)
        instance.validate_required_params()

        assert instance._errors.is_valid() is not has_error

    @patch.object(ConnectionCore, "validate_required_conn_details")
    @patch.object(ConnectionCore, "validate_required_params")
    @patch.object(
        ConnectionCore, "validate_connection_details_not_overwritten"
    )
    @patch.object(ConnectionCore, "validate_params_not_overwritten")
    def test_validate_does_not_raises_exception_if_valid(self, *mocks):
        MockConnection({}, {}, {})

        for mock in mocks:
            assert mock.called is True

    def test_validate_raises_exception_if_invalid(self):
        class MockValidation(MockConnection):
            error_class = MessageBrokerError
            required_conn_detail_fields = (HasField("host", str),)
            required_params_fields = (HasField("queue", str),)

        with pytest.raises(ConnectionValidationError):
            MockValidation({}, {}, {})
