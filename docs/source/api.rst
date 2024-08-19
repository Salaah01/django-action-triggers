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

