import json
import typing as _t
from functools import partial

from django.core import serializers
from django.db.models import Model
from django.template import Context, Template

from action_triggers.models import Config


def parse_payload(instance: Model, payload: str) -> _t.Union[dict, str]:
    """Parse a payload dictionary with a model instance and return the parsed
    object. If the parsed object is JSON serializable, it will be returned as
    a dictionary, otherwise it will be returned as a string.

    :param instance: The model instance to parse the payload for.
    :param payload: The payload to parse.
    :return: The parsed payload - either a dictionary or a string depending on
        whether the parsed object is JSON serializable.
    """

    parsed = Template(payload).render(Context({"instance": instance}))
    try:
        return json.loads(parsed.replace("'", '"'))
    except json.JSONDecodeError:
        return parsed


def payload_from_instance(instance: Model) -> dict:
    """Generates a payload from a model instance.

    :param instance: The model instance to generate the payload from.
    :return: A dictionary representing the payload derived from the model
        instance.
    """

    data = json.loads(
        serializers.serialize(
            "json",
            [instance],
            use_natural_primary_keys=True,
        )
    )[0]
    return data["fields"]


def get_payload_generator(
    config: Config,
) -> _t.Callable[[Model], _t.Union[dict, str]]:
    """Returns a function that generates a payload from a model instance and
    config.

    :param config: The configuration object to use for generating the payload.
    :return: If the config has a payload, the function will return a callable
        that generates the payload using the provided payload in the config
        object. Otherwise, it will return a callable that generates the payload
        from the model instance
    """

    if config.payload:
        return partial(parse_payload, payload=config.payload)
    return payload_from_instance
