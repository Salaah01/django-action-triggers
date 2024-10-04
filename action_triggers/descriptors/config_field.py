"""Module for defining descriptors related to defining the fields that appear
for a given config in `settings.ACTION_TRIGGERS`.

Note: This is not used in the current implementation. It is a work in progress
and a placeholder for future work.
"""


class ConfigField:  # pragma: no cover
    """Descriptor representing a particular config element that appears in the
    Action Triggers settings (`settings.ACTION_TRIGGERS`).

    :param required: Whether or not the field defined is required.
        (default: True)
    :param kwargs: Additional keyword arguments to be passed to the field
    """

    def __init__(self, required: bool = True, **kwargs):
        self.required = required
        self.kwargs = kwargs

    def __set_name__(self, owner: type, name: str) -> None:
        self.name = name

    def __set__(self, instance: object, value: dict) -> None:
        if not isinstance(value, dict):
            raise TypeError(f"{self.name} must be a dictionary")
        instance.__dict__[self.name] = value
