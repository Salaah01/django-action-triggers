.. _webhooks:

========
Webhooks
========

Webhook actions can be used to send a request to a specified URL when a trigger
is activated.

Creating a Webhook Action
=========================

To create a webhook action, a :class:`Config` model instance must be created
with at least one content type provided, a :class:`Webhook` model instance must
be created, and a :class:`ConfigSignal` model instance must be created.

Let's start with a scenario. Suppose we have the following Django models:

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

Suppose we want a webhook to be triggered when a new sale is created. We can
create a webhook action by following these steps:

1. Create a :class:`Config` model instance (base action):

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


This forms the basis of any action. The `payload` is designed to behave like a
Django template. If the resulting value after any parsing is JSON-serializable,
then the returning payload will be JSON, otherwise, it'll be just plain text.

2. Create a :class:`Webhook` model instance (webhook action):

.. warning::

  In the example below, the API key is hardcoded. This means that the database
  will store the API key in plaintext. This is not recommended. Instead, you
  should use a callable to fetch the API key at runtime. See the following
  section to see how we implement this.

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
    }
  )

Now we have a webhook action. But we still don't have a trigger.

3. Create a :class:`ConfigSignal` model instance (trigger):

.. code-block:: python

  from action_triggers.models import ConfigSignal
  from action_triggers.enums import SignalChoices

  config_signal = ConfigSignal.objects.create(
    config=config,
    signal=SignalChoices.POST_SAVE,
  )

Now we have a webhook action that will be triggered when a new sale is created.


Dynamically Setting Headers
===========================

In the example above, we hardcoded the API key in the `webhooks.headers` field.
This is not recommended as the API key will be stored in plaintext in the
database. Instead, we can use a callable to fetch the API key at runtime.

Replacing Hardcoding
--------------------

Let's suppose we have a the function `myproject.my_module.fetch_api_key` that
fetches the API key for us. We can specify the path to this function in the
`webhooks.headers` field like so:


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

In order to use this feature, you must ensure that the callable or variable
that you are specifying in the field must be defined in the settings file.

Any callable or variable that you wish to be evaluated at runtime must be
defined in `ACTION_TRIGGER_SETTINGS.ALLOWED_DYNAMIC_IMPORT_PATHS`.

Using the example above, you would need to add the following to your settings
file:

.. code-block:: python

  ACTION_TRIGGER_SETTINGS = {
      ...
      'ALLOWED_DYNAMIC_IMPORT_PATHS': (
          'myproject.my_module.fetch_api_key',
      ),
  }

More information on dynamically setting headers can be found in :ref:`dynamic-loading`.