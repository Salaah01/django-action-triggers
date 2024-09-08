"""Tests for the `config_required_fields` module."""

from unittest.mock import patch

import pytest

from action_triggers.config_required_fields import (
    HasAtLeastOneOffField,
    HasField,
)


class TestRequiredFieldBase:
    """Tests for the `RequiredFieldBase` class."""

    def test_str_is_a_string(self):
        assert isinstance(str(HasField("field", str)), str)

    def test_repr_is_a_string(self):
        assert isinstance(repr(HasField("field", str)), str)

    def test_key_repr_is_a_string(self):
        assert isinstance(HasField("field", str).key_repr, str)


class TestHasField:
    """Tests for the `HasField` class."""

    @pytest.mark.parametrize(
        "context, expected",
        [
            ({"field": "value", "another_field": "value_2"}, True),
            ({"another_field": "value"}, False),
        ],
    )
    def test_check_exists(self, context, expected):
        assert HasField("field").check_exists(context) is expected

    @pytest.mark.parametrize(
        "context, args, expected",
        [
            ({"field": "value"}, (str,), True),
            ({"field": 1}, (str,), False),
            ({"field": 1}, (), True),
        ],
    )
    def test_check_type_from_args(self, context, args, expected):
        assert (
            HasField("field", *args).check_type_from_args(context) is expected
        )

    @pytest.mark.parametrize(
        "context, kwargs, expected",
        [
            ({"field": "value"}, {"type": str}, True),
            ({"field": 1}, {"type": str}, False),
            ({"field": 1}, {}, True),
        ],
    )
    def test_check_type_from_kwargs(self, context, kwargs, expected):
        assert (
            HasField("field", **kwargs).check_type_from_kwargs(context)
            is expected
        )

    @patch.object(HasField, "check_exists", return_value=True)
    @patch.object(HasField, "check_type_from_args", return_value=True)
    @patch.object(HasField, "check_type_from_kwargs", return_value=True)
    def test_check_runs_all_checks(self, *args):
        HasField("field").check({})
        for arg in args:
            arg.assert_called_once()
        assert len(args) == 3

    @pytest.mark.parametrize(
        "args,kwargs,context,expected_error",
        [
            (("my_field",), {}, {}, "The field 'my_field' must be provided."),
            (
                ("my_field", str),
                {},
                {"my_field": 1},
                "The field 'my_field' must be of type str.",
            ),
            (
                ("my_field",),
                {"type": str},
                {"my_field": 1},
                "The field 'my_field' must be of type str.",
            ),
        ],
    )
    def test_produces_correct_error_on_failure(
        self, args, kwargs, context, expected_error
    ):
        field = HasField(*args, **kwargs)
        assert not field.check(context)
        assert field.error_msg == expected_error


class TestHasAtLeastOneOffField:
    """Tests for the `HasAtLeastOneOffField` class."""

    def test_raises_error_if_field_provided(self):
        with pytest.raises(ValueError) as exc:
            HasAtLeastOneOffField("field")

        assert str(exc.value) == (
            "'field' parameter not supported for this class. Use "
            "'fields' keyword argument instead."
        )

    @pytest.mark.parametrize("kwargs", ({}, {"fields": []}))
    def test_raises_error_if_fields_not_provided(self, kwargs):
        with pytest.raises(ValueError) as exc:
            HasAtLeastOneOffField(**kwargs)

        assert (
            str(exc.value)
            == "'fields' keyword argument must be a non-empty sequence."
        )

    @pytest.mark.parametrize(
        "context, expected",
        [
            ({"field_1": "a", "other_fields": "c"}, True),
            ({"field_2": "b", "other_fields": "c"}, True),
            ({"field_1": "a", "field_2": "b", "other_fields": "c"}, True),
            ({"other_fields": "c"}, False),
        ],
    )
    def test_check_returns_correct_result(self, context, expected):
        assert (
            HasAtLeastOneOffField(fields=["field_1", "field_2"]).check(context)
            is expected
        )

    @pytest.mark.parametrize("fields", (["field_1"], ["field_1", "field_2"]))
    def test_repr_is_a_string(self, fields):
        assert isinstance(repr(HasAtLeastOneOffField(fields=fields)), str)
