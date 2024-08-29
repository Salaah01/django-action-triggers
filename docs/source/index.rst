====================================
Django Action Triggers Documentation
====================================

.. image:: https://img.shields.io/badge/license-MIT-blue
   :alt: License MIT

.. image:: https://badge.fury.io/py/django-action-triggers.svg
   :target: https://badge.fury.io/py/django-action-triggers

.. image:: https://img.shields.io/pypi/pyversions/django-action-triggers
   :alt: PyPI - Supported Python Versions

.. image:: https://img.shields.io/badge/django-3.2%20%7C%204.2-blue
   :alt: Supported Django Versions

.. image:: https://codecov.io/github/Salaah01/django-action-triggers/graph/badge.svg?token=ROHNEE9D4X 
   :target: https://codecov.io/github/Salaah01/django-action-triggers

Welcome to the documentation for
**Django Action Triggers (django-action-triggers)**, a flexible Django
application that allows you to trigger actions based on changes in the
database.

Overview
========

In **Django Action Triggers**, a **"trigger"** refers to an event that
initiates a corresponding **"action"**. Triggers are typically associated with
database changes, such as creating, updating, or deleting records,
while actions define the code that is executed in response to those changes.

Supported Actions
-----------------

- **Webhook Actions**: Send HTTP requests to specified URLs when triggers are activated.
- **Message Broker Actions**: Send messages to messaging brokers like Kafka and RabbitMQ.

Key Features
============

- **Database-Driven Triggers**: Automatically trigger actions based on specific database changes, such as model save events.
- **Flexible Action Handling**: Integrate with a variety of external systems via webhooks and messaging brokers.
- **Extensible**: Easily extend to support custom triggers, actions, and integration points.
- **Dynamic Configuration**: Dynamically set values at runtime, allowing for secure and flexible handling of sensitive information.

Contents
========

This documentation is organised into the following sections:

.. toctree::
   :maxdepth: 2
   
   installation
   setup
   action_trigger_settings
   api
   dynamic_loading
   webhooks
   message_brokers

Message Broker Integrations
===========================

For detailed guidance on configuring and using specific message brokers, refer
to:

.. toctree::
   :maxdepth: 2
   
   message_brokers/kafka
   message_brokers/rabbitmq

Modules
=======

For an in-depth look at the modules used in Django Action Triggers, see:

.. toctree::
   :maxdepth: 1
   
   modules

Indices and tables
==================

Use the following resources to quickly find what you're looking for:

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

Additional Resources
====================

For more information on specific topics, refer to the relevant sections of this
documentation. If you encounter any issues or have questions, please raise an
issue on the
`GitHub repository <https://github.com/Salaah01/django-action-triggers>`_.
