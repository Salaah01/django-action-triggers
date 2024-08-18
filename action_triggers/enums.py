from django.db.models import TextChoices, signals


class HTTPMethodChoices(TextChoices):
    """Represents the supported HTTP methods for webhooks."""

    GET = "GET", "GET"
    POST = "POST", "POST"
    PUT = "PUT", "PUT"
    PATCH = "PATCH", "PATCH"
    DELETE = "DELETE", "DELETE"


class SignalChoices(TextChoices):
    """Represents the supported signals for action triggers."""

    PRE_SAVE = "pre_save", "Pre-save"
    POST_SAVE = "post_save", "Post-save"
    PRE_DELETE = "pre_delete", "Pre-delete"
    POST_DELETE = "post_delete", "Post-delete"

    @classmethod
    def for_signal(cls, signal: signals.ModelSignal) -> "SignalChoices":
        """Return the SignalChoices instance for the given signal.

        :param signal: The signal to map to a SignalChoices instance.
        :type signal: signals.ModelSignal
        :return: The SignalChoices instance for the given signal.
        :rtype: SignalChoices
        """

        signal_map = {
            signals.pre_save: cls.PRE_SAVE,
            signals.post_save: cls.POST_SAVE,
            signals.pre_delete: cls.PRE_DELETE,
            signals.post_delete: cls.POST_DELETE,
        }

        try:
            return signal_map[signal]
        except KeyError:
            raise KeyError("Unsupported signal type")
