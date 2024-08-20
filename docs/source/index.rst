====================================
Django Action Triggers Documentation
====================================

Django Action Triggers (django-action-triggers) is a Django application that
allows the user to trigger actions based on changes in the database.

Overview
========

In this application, the term **"trigger"** refers to an event that causes a
corresponding **"action"** to be executed. Triggers are typically database
changes, while actions are pieces of code that execute in response to those
changes.

Supported actions include:

- Sending a request to a webhook
- Sending a message to a messaging broker

Key Features
============

- **Database-Driven Triggers**: Automatically trigger actions based on specific database changes.
- **Flexible Action Handling**: Integrate with various webhooks and messaging brokers.
- **Extensible**: Easily extend to support custom triggers and actions.

Contents
========

.. toctree::
   :maxdepth: 2
   :caption: Guide:
   
   installation
   setup
   action_trigger_settings
   api
   dynamic_loading
   webhooks
   message_brokers

.. toctree::
   :maxdepth: 2
   :caption: Message Brokers:
   
   message_brokers/kafka
   message_brokers/rabbitmq

.. toctree::
   :maxdepth: 1
   :caption: Modules:
   
   modules

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
