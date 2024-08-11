from django.db.model import StringChoices


class HTTPMethodChoices(StringChoices):
    """Represents the supported HTTP methods for webhooks."""

    GET = "GET", "GET"
    POST = "POST", "POST"
    PUT = "PUT", "PUT"
    PATCH = "PATCH", "PATCH"
    DELETE = "DELETE", "DELETE"


class SignalChoices(StringChoices):
    """Represents the supported signals for action triggers."""

    PRE_SAVE = "pre_save", "Pre-save"
    POST_SAVE = "post_save", "Post-save"
    PRE_DELETE = "pre_delete", "Pre-delete"
    POST_DELETE = "post_delete", "Post-delete"
