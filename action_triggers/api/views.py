from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.decorators import action
from django.shortcuts import get_object_or_404

from action_triggers.models import Config
from action_triggers.api.serializers import ConfigSerializer


class ConfigViewSet(viewsets.ModelViewSet):
    """A viewset for viewing and editing Config instances, along with related
    instances.
    """

    queryset = Config.objects.all()
    serializer_class = ConfigSerializer
