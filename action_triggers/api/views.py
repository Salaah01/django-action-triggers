from rest_framework import viewsets  # type: ignore[import-untyped]

from action_triggers.api.serializers import ConfigSerializer
from action_triggers.models import Config


class ConfigViewSet(viewsets.ModelViewSet):
    """A viewset for viewing and editing Config instances, along with related
    instances.
    """

    queryset = Config.objects.all()
    serializer_class = ConfigSerializer
