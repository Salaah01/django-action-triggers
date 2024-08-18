import json


class MissingDependenciesError(ImportError):
    """Exception raised when required dependencies are missing."""

    def __init__(self, broker_name: str, extra_name: str, package_name: str):
        super().__init__(
            f"The `{extra_name}` extra must be installed to use the "
            f"{broker_name} broker. Please install the `{extra_name}` extra "
            f"by running `pip install action-triggers[{extra_name}]`. "
            f"Alternatively, you can install the required packages by running "
            f"`pip install {package_name}`."
        )


class ConnectionValidationError(RuntimeError):
    """Exception raised when connection parameters are invalid."""

    def __init__(self, message: dict):
        super().__init__(message)

    def as_dict(self) -> dict:
        """Return the error message as a dictionary."""
        return dict(self.args[0])

    def as_json(self) -> str:
        """Return the error message as a JSON string."""
        return json.dumps(self.as_dict())
