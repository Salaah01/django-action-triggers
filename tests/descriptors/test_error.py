"""Tests for the `descriptors.errors` module."""

from action_triggers.descriptors.error import ErrorField


class MockClass:
    field_1 = ErrorField()
    field_2 = ErrorField()


class TestErrorField:
    """Tests for the `ErrorField` class."""

    def test_adding_errors_by_field(self):
        instance = MockClass()
        instance_class = instance.__class__
        instance_class.field_1.add_error(instance, "key_1", "error_1")
        instance_class.field_2.add_error(instance, "key_2", "error_2")

        assert instance.field_1 == {"key_1": ["error_1"]}
        assert instance.field_2 == {"key_2": ["error_2"]}

    def test_can_add_multiple_errors(self):
        instance = MockClass()
        instance_class = instance.__class__
        instance_class.field_1.add_error(instance, "key_1", "error_1")
        instance_class.field_1.add_error(instance, "key_1", "error_2")
        instance_class.field_1.add_error(instance, "key_2", "error_3")

        assert instance.field_1 == {
            "key_1": ["error_1", "error_2"],
            "key_2": ["error_3"],
        }

    def test_does_not_mutate_other_instances(self):
        instance_1 = MockClass()
        instance_2 = MockClass()
        instance_1_class = instance_1.__class__
        instance_2_class = instance_2.__class__

        instance_1_class.field_1.add_error(instance_1, "key_1", "error_1")
        instance_2_class.field_1.add_error(instance_2, "key_2", "error_2")
        instance_1_class.field_2.add_error(instance_1, "key_3", "error_3")
        instance_2_class.field_2.add_error(instance_2, "key_4", "error_4")

        assert instance_1.field_1 == {"key_1": ["error_1"]}
        assert instance_2.field_1 == {"key_2": ["error_2"]}
        assert instance_1.field_2 == {"key_3": ["error_3"]}
        assert instance_2.field_2 == {"key_4": ["error_4"]}
