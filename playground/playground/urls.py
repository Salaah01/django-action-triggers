"""URL configuration for playground project."""
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/action-triggers/', include('action_triggers.urls')),
]
