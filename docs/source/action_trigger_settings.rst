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

.. _action_trigger_settings_configuration_options:

Configuration Options (`ACTION_TRIGGERS`)
=========================================

The primary configuration options for Django Action Triggers are contained
within the `ACTION_TRIGGERS` dictionary. The key options include:

- **brokers**: A dictionary of settings related to messaging brokers.
- **webhooks**: A dictionary of settings related to webhooks.
- **whitelisted_content_types**: A tuple of of content types that are allowed to be used in actions. Each content type should be in the format `app_label.model_name`.
- **whitelisted_webhook_endpoint_patterns**: A tuple of regular expressions that define the allowed webhook endpoint patterns.

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
        "actions": {},
        "webhooks": {},
        "whitelisted_content_types": (
            "my_app.MyModel",
        ),
        "whitelisted_webhook_endpoint_patterns": (
            "https?://localhost:[0-9]+/webhook/[0-9]+/?",
            "https://example.com/",
        ),
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
    }

- **my_rabbit_mq_broker**: A unique name for the broker, referenced when creating actions.
- **broker_type**: Specifies the type of broker (`rabbitmq` in this case).
  Refer to :class:`action_triggers.message_broker.enums.BrokerType` for a list of supported brokers.
- **conn_details**: Contains the connection details required for the broker.
- **params**: Additional parameters needed by the broker (e.g., the queue name).

Once configured, this broker can be referenced when creating actions. For more
details, refer to the :ref:`message_brokers` guide.

Configuring Actions (`ACTION_TRIGGERS.actions`)
===============================================

Django Action Triggers supports executing/invoking multiple actions
simultaneously. Each action can be uniquely configured with its own settings.

Configuration Schema
--------------------

The configuration schema for an action is as follows:

.. code-block:: typescript
  
    {
        [name: string]: {
            action_type: string,
            params: dict
        }
    }

- **name**: A unique identifier for the action.
- **action_type**: Specifies the type of action (e.g., `aws_lambda`).
- **conn_details**: A dictionary containing connection details specific to the action.
- **params**: A dictionary containing additional parameters required by the action.

Example: AWS Lambda Configuration
---------------------------------

Below is an example configuration for an AWS Lambda action:

.. code-block:: python

    ACTION_TRIGGERS = {
        "actions": {
            "my_aws_lambda_action": {
                "action_type": "aws_lambda",
                "conn_details": {
                    "endpoint_url": "https://lambda.us-east-1.amazonaws.com",
                    "region_name": "us-east-1",
                "params": {
                    "FunctionName": "my_lambda_function",
                    "InvocationType": "RequestResponse"
                }
            }
        },
    }

- **my_aws_lambda_action**: A unique name for the action, referenced when creating triggers.
- **action_type**: Specifies the type of action (`aws_lambda` in this case).
  Refer to :class:`action_triggers.actions.enums.ActionType` for a list of supported actions.
- **conn_details**: Contains the connection details required for the action.
- **params**: Additional parameters needed by the action (e.g., the function name).

Once configured, this action can be referenced when creating triggers. For more
details, refer to the :ref:`actions` guide.


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

At the very least, this should contain some default settings for the
application.

Defining Default Settings
-------------------------

The following default settings should be defined in the
`ACTION_TRIGGER_SETTINGS` dictionary:

- **MAX_BROKER_TIMEOUT** - (float) The maximum time (in seconds) to wait for a broker to respond.
- **MAX_ACTION_TIMEOUT** - (float) The maximum time (in seconds) to wait for an action to respond.
- **MAX_WEBHOOK_TIMEOUT** - (float) The maximum time (in seconds) to wait for a webhook to respond.

Example Configuration
~~~~~~~~~~~~~~~~~~~~~

A basic configuration for `ACTION_TRIGGER_SETTINGS` might look like this:

.. code-block:: python

    ACTION_TRIGGER_SETTINGS = {
        "MAX_BROKER_TIMEOUT": 10.0,
        "MAX_ACTION_TIMEOUT": 5.0,
        "MAX_WEBHOOK_TIMEOUT": 5.0
    }


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
