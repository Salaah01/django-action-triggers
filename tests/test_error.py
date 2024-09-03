"""Tests for the `message_broker.error` module."""


from action_triggers.message_broker.error import MessageBrokerError


class TestErrorField:
    """Tests for the `ErrorField` class."""

    def test_add_error_adds_errors(self):
        instance = MessageBrokerError()
        instance.add_params_error("key_1", "message_1")
        instance.add_params_error("key_1", "message_2")
        instance.add_params_error("key_2", "message_3")
        instance.add_connection_params_error("key_1", "message_4")

        assert instance.as_dict() == {
            "connection_params": {"key_1": ["message_4"]},
            "params": {
                "key_1": ["message_1", "message_2"],
                "key_2": ["message_3"],
            },
        }

    def test_cant_be_mutated_across_instances(self):
        instance_1 = MessageBrokerError()
        instance_2 = MessageBrokerError()

        instance_1.add_params_error("key_1", "message_1")

        assert instance_2.as_dict() == {
            "connection_params": {},
            "params": {},
        }
