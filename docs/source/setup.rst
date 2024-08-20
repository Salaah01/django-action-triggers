.. _setup:

=====
Setup
=====

This guide walks you through the steps to set up **Django Action Triggers** in
your Django project after installation.


.. note::

    If you have not yet installed the application, please refer to the
    :ref:`installation` guide.


Configuration
=============

1. Add to Installed Apps
------------------------

To start using Django Action Triggers, you need to add the application to your
Django project's `INSTALLED_APPS` setting. Open your `settings.py` file and add
the following line:


.. code-block:: python

    INSTALLED_APPS = [
        ...
        'django_action_triggers',
        ...
    ]

2. Configure Trigger and Action Settings (Optional)
---------------------------------------------------

You may want to customise some settings related to triggers and actions. For
example, setting default messaging broker configurations or webhook endpoints.
Add any relevant settings in your `settings.py` file:

More information on configuring triggers and actions can be found later in the
the :ref:`action_trigger_settings` guide.

.. code-block:: python
    
    # Example settings for action triggers
    ACTION_TRIGGER_SETTINGS = {
        "default_webhook": {
            "url": "https://example.com/webhook",
            "method": "POST",
            "headers": {
                "Content-Type": "application/json"
            }
        }
    }

Migrations
==========

Once you have added the application to `INSTALLED_APPS`, you need to apply
migrations to set up the necessary database tables. Run the following command
in your terminal:

.. code-block:: bash

    python manage.py migrate

This will create the required tables in your database for storing triggers and
actions.