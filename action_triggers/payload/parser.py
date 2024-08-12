import typing as _t
from django.db.models import Model
from django.template import Context, Template
import json


def parse_payload(instance: Model, payload: str) -> _t.Union[dict, str]:
    """
    Parse a payload dictionary with a model instance and return the parsed
    object. If the parsed object is JSON serializable, it will be returned as
    a dictionary, otherwise it will be returned as a string.

    :param instance: The model instance to parse the payload for.
    :param payload: The payload to parse.
    """

    parsed = Template(payload).render(Context({"instance": instance}))
    try:
        return json.loads(parsed.replace("'", '"'))
    except json.JSONDecodeError:
        return parsed
