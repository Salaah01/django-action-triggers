"""Tests for the `dynamic_loading` module."""

import pytest
from django.test import override_settings

from action_triggers.dynamic_loading import (
    get_path_result,
    replace_dict_values_with_results,
    replace_string_with_result,
    restricted_import_string,
)


def get_webhook_headers() -> dict:
    """A mocked function that will return the headers for a webhook
    request.
    """

    return {
        "Content-Type": "application/json",
        "Authorization": "Bearer test_token",
    }


def get_api_token() -> str:
    """A mocked function that will return the API token for a webhook
    request.
    """

    return "test_token"


# A mocked value to test if the variable can be loaded using dynamic imports.
WEBHOOK_API_TOKEN = "test_token"


class TestRestrictedImportString:
    """Tests for the `restricted_import_string` function."""

    @override_settings(
        ACTION_TRIGGER_SETTINGS={"ALLOWED_DYNAMIC_IMPORT_PATHS": None}
    )
    def test_if_paths_not_defined_raises_runtime_error(self):
        with pytest.raises(RuntimeError) as exc:
            restricted_import_string("module.submodule.attr")

        assert str(exc.value) == (
            "No allowed paths defined in settings. Please define "
            "`ACTION_TRIGGER_SETTINGS.ALLOWED_DYNAMIC_IMPORT_PATHS`."
        )

    @override_settings(
        ACTION_TRIGGER_SETTINGS={"ALLOWED_DYNAMIC_IMPORT_PATHS": ("abc")}
    )
    def test_if_path_not_allowed_raises_value_error(self):
        with pytest.raises(ValueError) as exc:
            restricted_import_string("module.submodule.attr")

        assert str(exc.value) == (
            "Path 'module.submodule.attr' not allowed. Please add it to "
            "`ACTION_TRIGGER_SETTINGS.ALLOWED_DYNAMIC_IMPORT_PATHS`."
        )

    @pytest.mark.parametrize(
        "path,expected",
        [
            (
                "tests.test_dynamic_loading.get_webhook_headers",
                get_webhook_headers,
            ),
            (
                "tests.test_dynamic_loading.WEBHOOK_API_TOKEN",
                WEBHOOK_API_TOKEN,
            ),
        ],
    )
    def test_returns_path_to_import(self, path, expected):
        result = restricted_import_string(path)
        assert result is expected


class TestGetPathResult:
    """Tests for the `get_path_result` function."""

    @pytest.mark.parametrize(
        "path,expected",
        (
            (
                "tests.test_dynamic_loading.get_webhook_headers",
                get_webhook_headers(),
            ),
            (
                "tests.test_dynamic_loading.WEBHOOK_API_TOKEN",
                WEBHOOK_API_TOKEN,
            ),
        ),
    )
    def test_returns_correctly(self, path, expected):
        result = get_path_result(path)
        assert result == expected


class TestReplaceStringWithResult:
    """Tests for the `replace_string_with_result` function."""

    def test_can_replace_a_with_a_callable_result(self):
        string = (
            "The headers are "
            "{{ tests.test_dynamic_loading.get_webhook_headers }}"
        )
        result = replace_string_with_result(string)
        expected = (
            "The headers are {'Content-Type': 'application/json', "
            "'Authorization': 'Bearer test_token'}"
        )

        assert result == expected

    def test_can_replace_a_with_a_non_callable_result(self):
        string = (
            "The API token is "
            "{{ tests.test_dynamic_loading.WEBHOOK_API_TOKEN }}"
        )
        result = replace_string_with_result(string)
        expected = "The API token is test_token"

        assert result == expected

    def test_can_replace_multiple_paths(self):
        string = (
            "The headers are "
            "{{ tests.test_dynamic_loading.get_webhook_headers }}"
            " and the API token is "
            "{{ tests.test_dynamic_loading.WEBHOOK_API_TOKEN }}"
        )
        result = replace_string_with_result(string)
        expected = (
            "The headers are {'Content-Type': 'application/json', "
            "'Authorization': 'Bearer test_token'} and the API token is "
            "test_token"
        )

        assert result == expected


class TestReplaceDictValuesWithResults:
    """Tests for the `replace_dict_values_with_results` function."""

    def test_can_replace_a_with_a_callable_result(self):
        dictionary = {
            "headers": {
                "content_type": "application/json",
                "Auth": "Bearer: {{ tests.test_dynamic_loading.get_api_token }}",  # noqa: E501
            }
        }
        result = replace_dict_values_with_results(dictionary)
        expected = {
            "headers": {
                "content_type": "application/json",
                "Auth": "Bearer: test_token",
            }
        }

        assert result == expected
