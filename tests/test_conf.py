"""Tests for the `conf` module."""

import pytest
from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.test import override_settings

from action_triggers.conf import get_content_type_choices


@pytest.mark.django_db
class TestGetContentTypeChoices:
    """Tests for the `get_content_type_choices` function."""

    @pytest.fixture(autouse=True)
    def clear_cache(self):
        get_content_type_choices.cache_clear()

    def test_get_correct_content_type_choices(self):
        ct_choices = get_content_type_choices()

        assert ct_choices.count() == 4
        expected = {
            tuple(opt.split("."))
            for opt in settings.ACTION_TRIGGERS["whitelisted_content_types"]
        }
        assert set(ct_choices.values_list("app_label", "model")) == expected

    @override_settings(ACTION_TRIGGERS={"whitelisted_content_types": ()})
    def test_gets_all_content_types_if_no_whitelisted_content_types(self):
        ct_choices = get_content_type_choices()

        assert ct_choices.count() == ContentType.objects.all().count()

    @override_settings(ACTION_TRIGGERS={"whitelisted_content_types": ("foo.bar",)})
    def test_meaningful_error_if_invalid_model_specified(self):
        with pytest.raises(ContentType.DoesNotExist) as exc:
            get_content_type_choices()

        assert "Content type not found for app_label=foo and model=bar" in str(
            exc.value
        )

    @override_settings(ACTION_TRIGGERS={"whitelisted_content_types": ("foo",)})
    def test_meaningful_error_if_invalid_model_specified_format(self):
        with pytest.raises(ValueError) as exc:
            get_content_type_choices()

        assert "Invalid option provided for whitelisted_content_types: foo" in str(
            exc.value
        )
        assert "Expected format is app_label.model" in str(exc.value)
