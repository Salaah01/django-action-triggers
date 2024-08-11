"""Contains collection of models that have been registered to have signals
dispatched for. Also contains helper functions relating to the registry.
"""

import typing as _t
from django.db.models import Model, QuerySet
from django.contrib.contenttypes.models import ContentType


registered_models: _t.Dict[str, Model] = {}


def model_str(model: Model) -> str:
    """Returns a string representation of the model which can be used to
    identify both the app label and the model name.

    Args:
        model: The model to get the string representation of.

    Returns:
        A string representation of the model.
    """
    return f"{model._meta.app_label}.{model._meta.model_name}"


def add_to_registry(model: Model) -> None:
    """Adds a model to the registry.

    Args:
        model: The model to add to the registry.
    """
    registered_models[model_str(model)] = model


def model_in_registry(model: Model) -> bool:
    """Checks if a model is in the registry.

    Args:
        model: The model to check.

    Returns:
        True if the model is in the registry, False otherwise.
    """
    return model_str(model) in registered_models


def registered_content_types() -> QuerySet[ContentType]:
    """Return a queryset of all the content types registered in the
    registry.

    Returns:
        A queryset of all the content types registered in the registry.
    """
    content_types = []
    for model in registered_models.values():
        content_types.append(ContentType.objects.get_for_model(model))

    content_type_ids = [ct.id for ct in content_types]
    return ContentType.objects.filter(id__in=content_type_ids)
