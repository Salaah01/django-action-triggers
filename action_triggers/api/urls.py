"""API URLs for the action_triggers app."""

from rest_framework.routers import DefaultRouter
from action_triggers.api.views import ConfigViewSet

router = DefaultRouter()
router.register(r"configs", ConfigViewSet)

urlpatterns = router.urls
