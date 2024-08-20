"""Contains collection of models that have been registered to have signals
dispatched for. Also contains helper functions relating to the registry.
"""

import typing as _t

from django.contrib.contenttypes.models import ContentType
from django.db.models import Model, QuerySet
from django.db.models.base import ModelBase

T_ModelOrModelBase = _t.Union[Model, _t.Type[Model]]

registered_models: _t.Dict[str, _t.Type[Model]] = {}


def model_str(model: T_ModelOrModelBase) -> str:
    """Returns a string representation of the model which can be used to
    identify both the app label and the model name.

    :param model: The model to get the string representation of.
    :type model: Union[Model, Type[Model]]
    :return: A string representation of the model.
    :rtype: str
    """
    return f"{model._meta.app_label}.{model._meta.model_name}"


def add_to_registry(model: T_ModelOrModelBase) -> None:
    """Adds a model to the registry.

    :param model: The model to add to the registry.
    :type model: Union[Model, Type[Model]]
    :return: None
    """

    if not isinstance(model, ModelBase):
        model = model.__class__

    registered_models[model_str(model)] = model


def model_in_registry(model: T_ModelOrModelBase) -> bool:
    """Checks if a model is in the registry.

    :param model: The model to check.
    :type model: Union[Model, Type[Model]]
    :return: True if the model is in the registry, False otherwise.
    :rtype: bool
    """
    return model_str(model) in registered_models


def registered_content_types() -> QuerySet[ContentType]:
    """Return a queryset of all the content types registered in the
    registry.

    :return: A queryset of all the content types registered in the registry.
    :rtype: QuerySet[ContentType]
    """
    content_types = []
    for model in registered_models.values():
        content_types.append(ContentType.objects.get_for_model(model))

    content_type_ids = [ct.id for ct in content_types]
    return ContentType.objects.filter(id__in=content_type_ids)
