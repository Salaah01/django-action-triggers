.. _action_trigger_settings:

=======================
Action Trigger Settings
=======================

Overview
========

**Django Action Triggers** provides a flexible way to configure settings
related to triggers and actions. These settings can be customized within your
Django project's `settings.py` file to fine-tune the behaviour of the
application.

Configuration Options (`ACTION_TRIGGERS`)
=========================================

The primary configuration options for Django Action Triggers are contained
within the `ACTION_TRIGGERS` dictionary. The key options include:

- **brokers**: A dictionary of settings related to messaging brokers.
- **webhooks**: A dictionary of settings related to webhooks.
- **whitelisted_content_types**: A tuple of of content types that are allowed to be used in actions. Each content type should be in the format `app_label.model_name`.

In addition, there is a separate dictionary for behavioural settings:

- **ACTION_TRIGGER_SETTINGS**: A dictionary for configuring the behaviour of triggers and actions.

Each of these options allows you to customise the way Django Action Triggers
operates within your application.

Example Configuration
---------------------

A basic configuration for Django Action Triggers might look like this:

.. code-block:: python

    ACTION_TRIGGERS = {
        "brokers": {},
        "webhooks": {},
        "whitelisted_content_types": (
            "my_app.MyModel",
        )
    }

This configuration can be expanded with specific settings for brokers and
webhooks, as described below.



Configuring Message Brokers (`ACTION_TRIGGERS.brokers`)
=======================================================

Django Action Triggers supports sending messages to multiple messaging brokers
simultaneously. Each broker can be uniquely configured with its own settings.

Configuration Schema
--------------------

The configuration schema for a message broker is as follows:

.. code-block:: typescript
  
    {
        [name: string]: {
            broker_type: string,
            conn_details: dict,
            params: dict
        }
    }


- **name**: A unique identifier for the broker.
- **broker_type**: Specifies the type of broker (e.g., `rabbitmq`, `kafka`).
- **conn_details**: A dictionary containing connection details specific to the broker.
- **params**: A dictionary containing additional parameters required by the broker.

Example: RabbitMQ Configuration
-------------------------------


Below is an example configuration for a RabbitMQ broker:

.. code-block:: python

    ACTION_TRIGGERS = {
        "brokers": {
            "my_rabbit_mq_broker": {
                "broker_type": "rabbitmq",
                "conn_details": {
                    "host": "localhost",
                    "port": 5672,
                },
                "params": {
                    "queue": "my_queue"
                }
            }
        },
        "webhooks": {}
    }

- **my_rabbit_mq_broker**: A unique name for the broker, referenced when creating actions.
- **broker_type**: Specifies the type of broker (`rabbitmq` in this case). Refer to :class:`action_triggers.enums.BrokerType` for a list of supported brokers.
- **conn_details**: Contains the connection details required for the broker.
- **params**: Additional parameters needed by the broker (e.g., the queue name).

Once configured, this broker can be referenced when creating actions. For more
details, refer to the :ref:`message_brokers` guide.




Configuring Webhooks (`ACTION_TRIGGERS.webhooks`)
=================================================

Django Action Triggers also supports sending messages to multiple webhooks.
The `webhooks` dictionary can be configured with settings specific to each
webhook.

For more detailed instructions on configuring webhooks, refer to the
:ref:`webhooks` guide.



Behavioural Settings (`ACTION_TRIGGER_SETTINGS`)
================================================

The `ACTION_TRIGGER_SETTINGS` dictionary allows you to configure various
behavioural aspects of triggers and actions. These settings control how
triggers and actions are executed.



An empty configuration for `ACTION_TRIGGER_SETTINGS` might look like this:

.. code-block:: python

    ACTION_TRIGGER_SETTINGS = {}


This dictionary can be populated with various settings, including those that
govern dynamic loading.

Defining Allowed Dynamic Loading 
--------------------------------

.. note::

    Visit the :ref:`dynamic-loading` guide for more information on dynamic
    loading.

The `ACTION_TRIGGER_SETTINGS.ALLOWED_DYNAMIC_IMPORT_PATHS` setting can be used
to define a list of allowed import paths for dynamic loading/execution of a
variable or callable.

Add the paths to the callables or variables that are allowed to be dynamically
loaded at runtime.

Let's explore an example:

.. code-block:: python

    ACTION_TRIGGER_SETTINGS = {
        "ALLOWED_DYNAMIC_IMPORT_PATHS": [
            "my_project.my_module.fetch_api_key"
            "my_project.app.constants.RESOURCE_NAME"
        ]
    }

In this example, the `fetch_api_key` function and `RESOURCE_NAME` variable are
allowed to be dynamically loaded at runtime.
