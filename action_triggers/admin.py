from django.contrib import admin

from action_triggers import models as action_triggers_models


class WebhookInline(admin.StackedInline):
    model = action_triggers_models.Webhook
    extra = 0


class MessageBrokerQueueInline(admin.StackedInline):
    model = action_triggers_models.MessageBrokerQueue
    extra = 0


class ConfigSignalInline(admin.TabularInline):
    model = action_triggers_models.ConfigSignal
    extra = 0


@admin.register(action_triggers_models.Config)
class ConfigAdmin(admin.ModelAdmin):
    list_display = ("id", "created_on", "created_by", "active")
    list_filter = ("active", "created_on", "content_types")
    search_fields = ("id", "created_by__username")
    readonly_fields = ("created_on",)
    ordering = ("-created_on",)
    date_hierarchy = "created_on"
    autocomplete_fields = ("created_by",)
    inlines = (ConfigSignalInline, WebhookInline, MessageBrokerQueueInline)


@admin.register(action_triggers_models.Webhook)
class WebhookAdmin(admin.ModelAdmin):
    list_display = ("id", "config", "url", "http_method")
    list_filter = ("http_method",)
    search_fields = ("config__id",)
    autocomplete_fields = ("config",)


@admin.register(action_triggers_models.MessageBrokerQueue)
class MessageBrokerQueueAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "config")
    search_fields = ("config__id",)
    autocomplete_fields = ("config",)


@admin.register(action_triggers_models.ConfigSignal)
class ConfigSignalAdmin(admin.ModelAdmin):
    list_display = ("id", "config", "signal")
    list_filter = ("signal",)
    search_fields = ("config__id",)
    autocomplete_fields = ("config",)
