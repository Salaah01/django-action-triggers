.. _webhooks:

========
Webhooks
========

Webhook actions in **Django Action Triggers** allow you to send a request to a
specified URL whenever a trigger is activated. This can be useful for
integrating your Django application with external services, such as notifying
other systems when certain events occur.

Installation
============

To use the webhooks integration, you will need to install an additional
package. This can be done by running the following command:

.. code-block:: bash

  pip install django-action-triggers[webhooks]

Creating a Webhook Action
=========================

To create a webhook action, you need to follow these steps:

1. **Create a :class:`Config` model instance** (defines the base action).
2. **Create a :class:`Webhook` model instance** (defines the webhook-specific action).
3. **Create a :class:`ConfigSignal` model instance** (defines the trigger).

Scenario
--------
Suppose you have the following Django models:

.. code-block:: python

    from django.db import models

    class Customer(models.Model):
        name = models.CharField(max_length=255)
        email = models.EmailField()

    class Product(models.Model):
        name = models.CharField(max_length=255)
        description = models.TextField()


    class Sale(models.Model):
        customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
        product = models.ForeignKey(Product, on_delete=models.CASCADE)
        quantity = models.IntegerField()

Now , suppose you want to trigger a webhook whenever a new sale is created.
Here's how you can set that up:


Step 1: Whitelist the Content Types and Endpoint Patterns
---------------------------------------------------------

Before you can get started with webhooks, you must whitelist the content types
and endpoint patterns in the `whitelisted_content_types` and
`whitelisted_webhook_endpoint_patterns` settings in your Django project's
`settings.py` file.

Visit the :ref:`Action Trigger Configuration Options<action_trigger_settings_configuration_options>`
guide for more information on whitelisting content types and endpoint patterns.

Step 2: Create a `Config` Model Instance
----------------------------------------

The `Config` model forms the basis of any action. It defines the payload that
will be sent when the action is triggered. The payload can use Django template
syntax to include dynamic data.

.. code-block:: python

    from django.contrib.contenttypes.models import ContentType
    from action_triggers.models import Config

    config = Config.objects.create(
        payload={
            "customer_name": "{{ customer.name }}",
            "product_name": "{{ product.name }}",
            "quantity": "{{ quantity }}"
        },
        active=True,
        content_types=[
            ContentType.objects.get_for_model(Sale)
        ]
    )


Step 3: Create a `Webhook` Model Instance
-----------------------------------------

The :class:`Webhook` model defines the URL and method used to send the request
when the trigger is activated.


.. warning::

  In the example below, the API key is hardcoded. This is not recommended
  because storing sensitive information in plaintext in the database is
  insecure. Instead, use a callable to fetch the API key at runtime (explained
  in the next section).


.. code-block:: python

  from action_triggers.models import Webhook
  from action-triggers.enums import HTTPMethod

  webhook = Webhook.objects.create(
    config=config,
    url="https://example.com/webhook",
    method=HTTPMethod.POST,
    headers={
      "Content-Type": "application/json",
      "Authorization": "Bearer my-api-key"
    },
    timeout_secs=10.0
  )


Step 4: Create a `ConfigSignal` Model Instance
----------------------------------------------

ally, the :class:`ConfigSignal` model links the action to a specific trigger
event, such as saving a model instance.

.. code-block:: python

    from action_triggers.models import ConfigSignal
    from action_triggers.enums import SignalChoices

    config_signal = ConfigSignal.objects.create(
        config=config,
        signal=SignalChoices.POST_SAVE,
    )

Now, whenever a new sale is created (or updated, if using `POST_SAVE`), the
webhook will be triggered.


Dynamically Setting Headers
===========================

In the previous example, the API key was hardcoded in the `webhooks.headers`
field. This is insecure because the key is stored in plaintext. Instead, you
can dynamically set the header values at runtime by using a callable.


Replacing Hardcoded Headers
---------------------------

Suppose you have a function `myproject.my_module.fetch_api_key` that retrieves
the API key securely. You can specify the path to this function in the
`webhooks.headers` field:

.. code-block:: python

    from action_triggers.models import Webhook
    from action-triggers.enums import HTTPMethod

    webhook = Webhook.objects.create(
        url="https://example.com/webhook",
        method=HTTPMethod.POST,
        config=config,
        headers={
            "Content-Type": "application/json",
            "Authorization": "Bearer {{ myproject.my_module.fetch_api_key }}"
        }
    )

Adding Dynamic Import Paths to Settings
---------------------------------------

To use dynamic imports for headers (or any other fields), you must allow the
specific callable or variable in your settings.

Add the following to your `settings.py` file:

.. code-block:: python

    ACTION_TRIGGER_SETTINGS = {
        'ALLOWED_DYNAMIC_IMPORT_PATHS': (
            'myproject.my_module.fetch_api_key',
        ),
    }

This configuration ensures that the specified callable can be safely evaluated
at runtime.

For more information on dynamically setting headers, refer to the
:ref:`dynamic-loading` guide.

Best Practices
==============

- **Avoid Hardcoding Sensitive Information**: Use dynamic imports to manage
  sensitive information such as API keys.
- **Test Your Webhooks**: Ensure that your webhook is functioning correctly by
  testing it with different scenarios.
- **Monitor Webhook Responses**: Keep track of webhook responses to ensure that
  your external systems are receiving and processing the requests correctly.
- **Set Timeout Limits**: Define a maximum timeout for webhooks to prevent 
  long-running requests from blocking your application. This can be done by
  setting `ACTION_TRIGGER_SETTINGS.MAX_WEBHOOK_TIMEOUT` in your settings.

---

By following these steps and best practices, you can effectively integrate
webhooks into your Django project using Django Action Triggers. For more
advanced configurations, refer to other sections of this documentation.
