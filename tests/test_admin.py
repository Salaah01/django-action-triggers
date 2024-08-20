"""Tests for the `admin` module."""

from django.contrib.admin.sites import AdminSite
from django.test import RequestFactory

from action_triggers import admin as action_triggers_admin
from action_triggers import models as action_triggers_models


class TestConfigAdmin:
    """Tests for the `ConfigAdmin` class."""

    def test_list_view_loads_with_results(self, config, superuser):
        admin = action_triggers_admin.ConfigAdmin(
            action_triggers_models.Config, AdminSite()
        )
        request = RequestFactory().get("/admin/action_triggers/config/")
        request.user = superuser
        response = admin.changelist_view(request)

        assert response.status_code == 200
        assert config in response.context_data["cl"].queryset

    def test_detail_view_loads_successfully(self, config, superuser):
        admin = action_triggers_admin.ConfigAdmin(
            action_triggers_models.Config, AdminSite()
        )
        request = RequestFactory().get(
            f"/admin/action_triggers/config/{config.id}/"
        )
        request.user = superuser
        response = admin.change_view(request, str(config.id))

        assert response.status_code == 200


class TestWebhookAdmin:
    """Tests for the `WebhookAdmin` class."""

    def test_list_view_loads_with_results(self, webhook, superuser):
        admin = action_triggers_admin.WebhookAdmin(
            action_triggers_models.Webhook, AdminSite()
        )
        request = RequestFactory().get("/admin/action_triggers/webhook/")
        request.user = superuser
        response = admin.changelist_view(request)

        assert response.status_code == 200
        assert webhook in response.context_data["cl"].queryset

    def test_detail_view_loads_successfully(self, webhook, superuser):
        admin = action_triggers_admin.WebhookAdmin(
            action_triggers_models.Webhook, AdminSite()
        )
        request = RequestFactory().get(
            f"/admin/action_triggers/webhook/{webhook.id}/"
        )
        request.user = superuser
        response = admin.change_view(request, str(webhook.id))

        assert response.status_code == 200


class TestMessageBrokerQueueAdmin:
    """Tests for the `MessageBrokerQueueAdmin` class."""

    def test_list_view_loads_with_results(self, rabbitmq_1_trigger, superuser):
        admin = action_triggers_admin.MessageBrokerQueueAdmin(
            action_triggers_models.MessageBrokerQueue, AdminSite()
        )
        request = RequestFactory().get(
            "/admin/action_triggers/messagebrokerqueue/"
        )
        request.user = superuser
        response = admin.changelist_view(request)

        assert response.status_code == 200
        assert rabbitmq_1_trigger in response.context_data["cl"].queryset

    def test_detail_view_loads_successfully(
        self,
        rabbitmq_1_trigger,
        superuser,
    ):
        admin = action_triggers_admin.MessageBrokerQueueAdmin(
            action_triggers_models.MessageBrokerQueue, AdminSite()
        )
        request = RequestFactory().get(
            f"/admin/action_triggers/messagebrokerqueue/{rabbitmq_1_trigger.id}/"  # noqa: E501
        )
        request.user = superuser
        response = admin.change_view(request, str(rabbitmq_1_trigger.id))

        assert response.status_code == 200
