"""Tests for the `dynamic_loading` module."""

import pytest
from action_triggers.dynamic_loading import restricted_import_string
from django.test import override_settings


def get_webhook_headers() -> dict:
    """A mocked function that will return the headers for a webhook
    request.
    """

    return {
        "Content-Type": "application/json",
        "Authorization": "Bearer test_token",
    }


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
