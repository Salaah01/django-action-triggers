===
API
===

.. warning::
  
    The API is currently under development and is not yet ready for use.


Setup
=====

If you would like to use the API, you will need to add the following to your
project's ``urls.py`` file:

.. code-block:: python

    urlpatterns = [
        ...
        path('api/action-triggers', include('action_triggers.urls')),
        ...
    ]


Usage
=====

The application will allow users to create triggers and actions in the Django
admin or via the API.

API Endpoints
-------------

A single API endpoint is available for interacting with the application. The
endpoint is as follows:

- ``/api/action-triggers``
  - ``GET``: Retrieve all triggers
  - ``POST``: Create a new trigger
  - ``PUT``: Update an existing trigger
  - ``DELETE``: Delete an existing trigger

- ``/api/action-triggers/<trigger_id>``
  - ``GET``: Retrieve a single trigger
  - ``PUT``: Update a single trigger
  - ``DELETE``: Delete a single trigger

API Specification
-----------------

The API specifications are below illustrate how to interact with the API and
how webhook and queue actions are defined.

.. code-block:: typescript

  {
    "trigger": {
      "signals": string[]
      "models": {
        "app_label": string,
        "model_name": string,
      }[],
    }
    "webhooks"?: {
      "url": string,
      "method": "GET" | "POST" | "PUT" | "DELETE",
      "headers"?: {
        [key: string]: string
      },
    }[],
    "msg_broker_queues"?: {
      "broker_config_name": string,
      "connection_details"?: {
        [key: string]: string
      },
      "parameters"?: {
        [key: string]: string
      }
    }[],
    "active": boolean,
    "payload"?: {
      [key: string]: string
    }
  }

API Constraints
---------------

The following constraints apply when sending an API request:

+-------------------+----------------------------------------------------------------------+
| Field             | Constraints                                                          |
+===================+======================================================================+
| `trigger.signals` | Allowed values: `pre_save`, `post_save`, `pre_delete`, `post_delete` |
+-------------------+----------------------------------------------------------------------+

Field Descriptions
------------------

The following fields are available for use in the API:

.. include:: api/field_descriptions.rst


Dynamically Settings Values at Runtime
======================================

Django Action Triggers supports dynamically setting values at runtime. This
feature allows you to specify a path to a callable or variable that will be
evaluated at runtime to fetch the value.

For information on how to use this feature, see the :ref:`dynamic-loading`
guide.

Examples
========

The following examples illustrate how to use the API to create triggers and
actions.

For the following examples, we will use the following models:

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


Example 1: Trigger a Webhook on Customer Creation, Update, and Deletion
-----------------------------------------------------------------------

.. include:: partials/note_ref_webhooks_guide.rst

The following example illustrates how to create a trigger that will hit a
webhook when a new customer is created, updated, or deleted.

.. code-block:: json

  {
    "trigger": {
      "signals": ["post_save", "post_delete"],
      "models": [
        {
          "app_label": "myapp",
          "model_name": "User"
        }
      ]
    },
    "webhooks": [
      {
        "url": "https://my-webhook.com",
        "method": "POST",
        "headers": {
          "Authorization": "Bearer {{ myapp.utils.get_token }}"
        }
      }
    ],
    "active": true
  }

Example 2: Trigger Webhooks and Send Messages to a Broker on `Product` and `Sale` Creation or Update
----------------------------------------------------------------------------------------------------

.. include:: partials/note_ref_message_brokers_guide.rst
.. include:: partials/note_ref_webhooks_guide.rst

The following example illustrates how to create a trigger that will hit a
webhook and send a message to a broker when a new product or sale is created or
updated.

.. code-block:: json

  {
    "trigger": {
      "signals": ["post_save"],
      "models": [
        {
          "app_label": "myapp",
          "model_name": "Product"
        },
        {
          "app_label": "myapp",
          "model_name": "Sale"
        }
      ]
    },
    "webhooks": [
      {
        "url": "https://my-webhook.com",
        "method": "POST",
        "headers": {
          "Authorization": "Bearer {{ myapp.utils.get_token }}"
        }
      },
      {
        "url": "https://my-other-webhook.com",
        "method": "POST",
        "headers": {
          "Authorization": "Bearer {{ myapp.utils.get_token }}"
        }
      }
    ],
    "msg_broker_queues": [
      {
        "broker_config_name": "my-queue",
        "parameters": {
          "product_id": "{{ myapp.utils.get_product_id }}"
        }
      },
      {
        "broker_config_name": "my-other-queue",
        "parameters": {
          "sale_id": "{{ myapp.utils.get_sale_id }}"
        }
      }
    ],
    "active": true
  }

Example 3: Trigger a Webhook When a `Sale` is Created/Updated Sending Customer and Product Information
------------------------------------------------------------------------------------------------------

.. include:: partials/note_ref_message_brokers_guide.rst
.. include:: partials/note_ref_webhooks_guide.rst

The following example illustrates how to create a trigger that will hit a
webhook when a new sale is created or updated. The webhook will send the
customer name and product name along with a static action.

.. code-block:: json

  {
    "trigger": {
      "signals": ["post_save"],
      "models": [
        {
          "app_label": "myapp",
          "model_name": "Sale"
        }
      ]
    },
    "webhooks": [
      {
        "url": "https://my-webhook.com",
        "method": "POST",
        "headers": {
          "Authorization": "Bearer {{ myapp.utils.get_token }}"
        }
      }
    ],
    "active": true,
    "payload": {
      "action": "new_sale",
      "customer_name": "{{ instance.customer.name }}",
      "product_name": "{{ instance.product.name }}"
    }
  }
