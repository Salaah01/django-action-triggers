"""Root URL configuration for the action_triggers app."""

from django.urls import include, path

app_name = "action_triggers"

urlpatterns = [
    path("", include("action_triggers.api.urls")),
]
