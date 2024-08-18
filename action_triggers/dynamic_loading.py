import re
import typing as _t

from django.conf import settings
from django.utils.module_loading import import_string


def restricted_import_string(path: str) -> _t.Any:
    """A restricted version of import_string that only allows importing from
    any path that has been defined in
    `settings.ACTION_TRIGGER_SETTINGS.ALLOWED_DYNAMIC_IMPORT_PATHS`.

    This is to prevent arbitrary code execution via dynamic imports.

    :param path: The path to import from in the format `module.submodule.attr`.
    :raises RuntimeError: If no allowed paths are defined in settings.
    :raises ValueError: If the path is not allowed.
    :return: The imported object.
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


def get_path_result(path: str) -> _t.Any:
    """Get the result of a path.

    :param path: The path to import from in the format `module.submodule.attr`.
    :return: The imported object.
    """

    obj = restricted_import_string(path)
    if callable(obj):
        return obj()
    return obj


def replace_string_with_result(
    string: str,
    opener: str = "{{",
    closer: str = "}}",
) -> str:
    """Replace all instances of `{{ path }}` in a string with the result of
    the path.

    :param string: The string to replace the paths in.
    :param opener: The opener of the path.
    :param closer: The closer of the path.
    :return: The string with the paths replaced.
    """

    return re.sub(
        rf"{re.escape(opener)}(.*?){re.escape(closer)}",
        lambda m: str(get_path_result(m.group(1).strip())),
        string,
    )


def replace_dict_values_with_results(
    dictionary: dict,
    opener: str = "{{",
    closer: str = "}}",
) -> dict:
    """Recursively all instances of `{{ path }}` in the values of a dictionary
    with the result of the path.

    :param dictionary: The dictionary to replace the paths in.
    :param opener: The opener of the path.
    :param closer: The closer of the path.
    :return: The dictionary with the paths replaced.
    """

    new_dict: _t.Dict[str, _t.Any] = {}

    for k, v in dictionary.items():
        if isinstance(v, str):
            new_dict[k] = replace_string_with_result(v, opener, closer)
        elif isinstance(v, dict):
            new_dict[k] = replace_dict_values_with_results(v, opener, closer)
        else:
            new_dict[k] = v

    return new_dict
