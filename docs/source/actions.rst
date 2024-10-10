.. _actions:

=======
Actions
=======

Actions in **Django Action Triggers** allow you to execute/invoke certain
actions whenever a trigger is activated. This is useful for integrating with
external services such as AWS Lambda.

Navigate to the :ref:`actions_configuration_guides` section to learn how to
configure specific actions in your Django settings.

Support for other actions are planned for future releases. If you would like to
see support for a specific action, please open an issue on the
`GitHub repository <https://github.com/Salaah01/django-action-triggers>`_.

.. _actions_configuration:

Configuration
=============

Before you can execute/invoke an action, you must configure the action in your
Django settings. This involves specifying the action type, connection details,
and any necessary parameters for the action.

For more information, refer to the :ref:`action_trigger_settings` guide.

Configuring Actions
-------------------

Actions are configured in the `ACTION_TRIGGERS.actions` dictionary in your
`settings.py` file. Each action configuration includes the action type,
connection details, and any additional parameters required.

**Example Configuration in `settings.py`**

Here is the structure of a basic action configuration:

.. code-block:: python

    ACTION_TRIGGERS = {
        "actions": {
            "<action_config_name>": {
                "action_type": "<action_type>",  # e.g., "aws_lambda"
                "conn_details": {
                    "<key>": "<value>"  # Key-value pairs of connection details (e.g., endpoint_url, region_name)
                },
                "params": {
                    "<key>": "<value>"  # Key-value pairs of action-specific parameters (e.g., FunctionName, InvocationType)
                }
            }
        }
    }


**Configuration Options**

.. include:: actions/config_options.rst

Example Configuration
=====================

Below is an example configuration for setting up an AWS Lambda action:

.. code-block:: python

    ACTION_TRIGGERS = {
        "actions": {
            "my_aws_lambda_action": {
                "action_type": "aws_lambda",
                "conn_details": {
                    "endpoint_url": "https://lambda.us-east-1.amazonaws.com",
                    "region_name": "us-east-1",
                },
                "params": {
                    "FunctionName": "my_lambda_function",
                    "InvocationType": "RequestResponse"
                }
            }
        }
    }

Best Practices for Configuration
================================

- **Security**: Avoid hardcoding sensitive information, such as passwords in
  your Django settings. Use environment variables or a secret management tool
  to store sensitive information securely.
- **Testing**: Before deploying to production, thoroughly test your action
  configurations to ensure they work as expected.
- **Set Timeout Limits**: Define a maximum timeout for actions to prevent
  long-running actions from blocking the system. This can be achieved by
  setting `ACTION_TRIGGER_SETTINGS.MAX_ACTION_TIMEOUT` in your Django settings.

.. _actions_configuration_guides:

Action Configuration Guides
===========================

The following guides will help you configure specific actions within your
Django project using **Django Action Triggers**:

.. toctree::
    :maxdepth: 1

    actions/aws_lambda