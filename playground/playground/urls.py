"""URL configuration for playground project."""

from django.contrib import admin
from django.urls import include, path
from sample_app.views import sns_listener

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/action-triggers/", include("action_triggers.urls")),
    path("sns/", sns_listener),
]
