class MissingDependenciesError(ImportError):
    """Exception raised when required dependencies are missing.

    :param broker_name: The name of the broker that requires the extra.
    :param extra_name: The name of the extra installable that is missing.
    :param package_name: The name of the package that is missing.
    """

    def __init__(self, broker_name: str, extra_name: str, package_name: str):
        super().__init__(
            f"The `{extra_name}` extra must be installed to use the "
            f"{broker_name} broker. Please install the `{extra_name}` extra "
            f"by running `pip install action-triggers[{extra_name}]`. "
            f"Alternatively, you can install the required packages by running "
            f"`pip install {package_name}`."
        )
