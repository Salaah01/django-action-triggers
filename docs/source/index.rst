Django Action Triggers Documentation
====================================

Django Action Triggers (django-action-triggers) is a Django application that
allows the user to trigger actions based on changes in the database.

This application uses the term "trigger" to refer to the event that will cause
an "action" to be executed. The triggers are specially changes in the database.
An action is the code that will be executed when the trigger is activated.

The support actions are:

- Hit a webhook
- Send a to a messaging broker

Contents
========

.. toctree::
   :maxdepth: 2
   :caption: Guide:
   
   installation
   setup
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
