from django.conf import settings
from django.utils.module_loading import import_string


def restricted_import_string(path: str):
    """A restricted version of import_string that only allows importing from
    any path that has been defined in
    `settings.ACTION_TRIGGER_SETTINGS.ALLOWED_DYNAMIC_IMPORT_PATHS`.

    This is to prevent arbitrary code execution via dynamic imports.

    :param path: The path to import from in the format `module.submodule.attr`.
    """

    ACTION_TRIGGER_SETTINGS = getattr(settings, "ACTION_TRIGGER_SETTINGS", {})
    allowed_paths = ACTION_TRIGGER_SETTINGS.get("ALLOWED_DYNAMIC_IMPORT_PATHS")

    if allowed_paths is None:
        raise RuntimeError(
            "No allowed paths defined in settings. Please define "
            "`ACTION_TRIGGER_SETTINGS.ALLOWED_DYNAMIC_IMPORT_PATHS`."
        )

    if path not in allowed_paths:
        raise ValueError(
            f"Path '{path}' not allowed. Please add it to "
            "`ACTION_TRIGGER_SETTINGS.ALLOWED_DYNAMIC_IMPORT_PATHS`."
        )

    return import_string(path)
