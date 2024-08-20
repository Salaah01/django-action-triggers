"""Root URL configuration for the action_triggers app."""

from django.urls import include, path

urlpatterns = [
    path("", include("action_triggers.api.urls")),
]
