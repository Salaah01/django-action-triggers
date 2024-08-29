from functools import lru_cache

from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.db.models import QuerySet

DB_TABLE_PREFIX = getattr(settings, "DB_TABLE_PREFIX", "action_triggers_")


@lru_cache
def get_content_type_choices() -> QuerySet[ContentType]:
    """Return the content types available for the configuration. This is
    driven by `settings.ACTION_TRIGGERS.whitelisted_content_types` where the
    user can specify a set of models (content_type app_label.model) that they
    want to be able to configure action triggers for.

    :return: A queryset of content types
    """
    choices = settings.ACTION_TRIGGERS.get("whitelisted_content_types", ())
    if not choices:
        return ContentType.objects.all()

    opts = []
    for choice in choices:
        try:
            app_label, model = choice.split(".")
        except ValueError:
            raise ValueError(
                f"Invalid option provided for whitelisted_content_types: {choice}"
                "Expected format is app_label.model"
            )

        try:
            content_type = ContentType.objects.get(
                app_label=app_label,
                model=model,
            )
        except ContentType.DoesNotExist:
            raise ContentType.DoesNotExist(
                f"Content type not found for app_label={app_label} "
                f"and model={model}"
            )
        opts.append(content_type)
    return ContentType.objects.filter(pk__in=[option.pk for option in opts])
