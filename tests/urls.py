from django.urls import include, path

urlpatterns = [
    path("action-triggers/", include("action_triggers.urls")),
]
