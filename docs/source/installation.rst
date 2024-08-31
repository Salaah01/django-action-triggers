.. _installation:

============
Installation
============

This section covers the installation of **Django Action Triggers**. Follow the steps below to get started.

Prerequisites
=============


Before installing Django Action Triggers, ensure you have the following:

- Python 3.8+
- Django 3.2+


Installation via PyPI
=====================

Django Action Triggers can be installed directly from PyPI using pip:

.. code-block:: bash

  pip install django-action-triggers

Optional: Install with Extras
-----------------------------

If you plan to use specific features (e.g., integration with messaging
brokers), you can install the required dependencies at the same time:

- To install with support for Kafka:

  .. code-block:: bash

    pip install django-action-triggers[kafka]

- To install with support for RabbitMQ:

  .. code-block:: bash

    pip install django-action-triggers[rabbitmq]

- To install with support for webhooks:

  .. code-block:: bash

    pip install django-action-triggers[webhooks]

Alternatively, you can install all extras:

.. code-block:: bash

  pip install django-action-triggers[all]

Next Steps
==========

Once you've completed the installation, proceed to the :ref:`setup<setup>` guide to configure Django Action Triggers in your project.
