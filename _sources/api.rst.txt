===
API
===

Overview
========

The **Django Action Triggers** API allows users to create, update, and manage
triggers and actions programmatically. This API is designed to provide
flexibility and control over the application's behaviour, enabling integrations
with external systems through webhooks and message brokers.

Setup
=====

To enable the API in your Django project, you need to include the following in
your project's `urls.py` file:

.. code-block:: python

    urlpatterns = [
        ...
        path('api/action-triggers/', include('action_triggers.urls')),
        ...
    ]


Usage
=====

The Django Action Triggers application allows users to create and manage
triggers and actions either through the Django admin interface or via the API.

API Endpoints
-------------

The API provides the following endpoints for interacting with triggers:

- `/api/action-triggers`

  * `GET`: Retrieve a list of all triggers.

  * `POST`: Create a new trigger

  * `PUT`: Update an existing trigger

  * `DELETE`: Delete an existing trigger

- `/api/action-triggers/<trigger_id>`

  * `GET`: Retrieve a single trigger by its ID.

  * `PUT`: Update a single trigger

  * `DELETE`: Delete a single trigger

API Specification
-----------------
Below is an example of the payload structure used when interacting with the API. This structure defines how triggers, webhooks, and message broker actions are configured.

.. code-block:: typescript

  {
    // List of signals objects, e.g., [{"signal": "pre_save"}, {"signal": "post_save"}]
    "config_signals": {"signal": string}[],  // List of signals objects
    "content_types": [
      {
        "app_label": string,  // Django app label, e.g., "myapp"
        "model_name": string  // Model name, e.g., "User"
      }
    ],
    "webhooks"?: [
      {
        "url": string,  // Webhook URL
        "http_method": "GET" | "POST" | "PUT" | "DELETE",  // HTTP method
        "headers"?: {
          [key: string]: string  // Optional headers
        },
        "timeout_secs"?: number  // Optional timeout in seconds
      }
    ],
    "msg_broker_queues"?: [
      {
        "name": string,  // Reference to configured broker
        "conn_details"?: {
          [key: string]: string  // Optional connection details
        },
        "parameters"?: {
          [key: string]: string  // Optional parameters
        }
        "timeout_secs"?: number  // Optional timeout in seconds
      }
    ],
    "active": boolean,  // Whether the trigger is active
    "payload"?: {
      [key: string]: string | dict  // Optional payload for the action
    }
  }

API Constraints
---------------

When interacting with the API, the following constraints apply:

+--------------------------+----------------------------------------------------------------------+
| Field                    | Constraints                                                          |
+==========================+======================================================================+
| `config_signals.signals` | Allowed values: `pre_save`, `post_save`, `pre_delete`, `post_delete` |
+--------------------------+----------------------------------------------------------------------+

Field Descriptions
------------------

The following fields are available for use in the API:

.. include:: api/field_descriptions.rst


Dynamic Value Assignment
========================

Django Action Triggers supports dynamically setting values at runtime. This
feature allows you to define paths to callables or variables that will be
evaluated dynamically when the trigger is executed.

For more details, refer to the :ref:`dynamic-loading` guide.

Examples
========

Below are examples illustrating how to use the API to create and manage
triggers and actions.

For the following examples, we will use the following models:

.. include:: partials/django_models_for_scenarios.rst

Example 1: Trigger a Webhook on Customer Creation, Update, and Deletion
-----------------------------------------------------------------------

.. include:: partials/note_ref_webhooks_guide.rst

In this example, a trigger is created that sends a POST request to a webhook
whenever a `Customer` model instance is created, updated, or deleted.

.. code-block:: json

  {
    "config_signals": [
      {"signal": "post_save"},
      {"signal": "post_delete"}
    ],
    "content_types": [
      {
        "app_label": "myapp",
        "model_name": "Customer"
      }
    ],
    "webhooks": [
      {
        "url": "https://my-webhook.com",
        "http_method": "POST",
        "headers": {
          "Authorization": "Bearer {{ myapp.utils.get_token }}"
        },
        "timeout_secs": 10.0
      }
    ],
    "active": true
  }

Example 2: Trigger Webhooks and Send Messages to a Broker on `Product` and `Sale` Creation or Update
----------------------------------------------------------------------------------------------------

.. include:: partials/note_ref_message_brokers_guide.rst
.. include:: partials/note_ref_webhooks_guide.rst

This example demonstrates how to create a trigger that sends requests to
webhooks and messages to a broker when a `Product` or `Sale` is created or
updated.

.. code-block:: json

  {
    "config_signals": [
      {"signal": "post_save"}
    ],
    "content_types": [
      {
        "app_label": "myapp",
        "model_name": "Product"
      },
      {
        "app_label": "myapp",
        "model_name": "Sale"
      }
    ]
    "webhooks": [
      {
        "url": "https://my-webhook.com",
        "http_method": "POST",
        "headers": {
          "Authorization": "Bearer {{ myapp.utils.get_token }}"
        },
        "timeout_secs": 2.25
      },
      {
        "url": "https://my-other-webhook.com",
        "http_method": "POST",
        "headers": {
          "Authorization": "Bearer {{ myapp.utils.get_token }}"
        }
      }
    ],
    "msg_broker_queues": [
      {
        "name": "my-msg-broker-config",
        "parameters": {
          "product_id": "{{ myapp.utils.get_product_id }}"
        },
        "timeout_secs": 5.75
      },
      {
        "name": "my-other-msg-broker-config",
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
    "config_signals": [
      {"signal": "post_save"}
    ],
    "content_types": [
      {
        "app_label": "myapp",
        "model_name": "Sale"
      }
    ]
    "webhooks": [
      {
        "url": "https://my-webhook.com",
        "http_method": "POST",
        "headers": {
          "Authorization": "Bearer {{ myapp.utils.get_token }}"
        },
        "timeout_secs": 12.25
      }
    ],
    "active": true,
    "payload": {
      "action": "new_sale",
      "customer_name": "{{ instance.customer.name }}",
      "product_name": "{{ instance.product.name }}"
    }
  }
