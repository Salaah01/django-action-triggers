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

    def __init__(self, message: str):
        super().__init__(message)
