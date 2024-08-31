=======
Testing
=======

This library integrates with various services like message brokers and
databases. Setting up a complete test environment for all these services can be
challenging. To simplify testing, we provide a `Dockerfile` and
`docker-compose.tox.yml` file to help you quickly spin up the necessary
services.

To begin testing, start the services with the following command:

.. code-block:: bash

    docker-compose -f docker-compose.tox.yml up -d

You can then run the tests using either `tox` for multi-environment testing or
`pytest` for the current environment.

Testing With `tox`
==================

Use `tox` to run tests across multiple environments, ensuring compatibility
with different Python versions, Django versions, databases, and message
brokers.

Install Dependencies in a Virtual Environment
----------------------------------------------

Linux/MacOS
~~~~~~~~~~~

.. code-block:: bash

    python3 -m venv .venv
    source .venv/bin/activate
    pip install tox

Windows
~~~~~~~

.. code-block:: powershell

    python -m venv .venv
    .venv\Scripts\activate
    pip install tox

Run Tests Across All Environments
----------------------------------

To run tests across all supported environments, use:

.. code-block:: bash

    tox

.. note::
   If you do not have a specific Python version installed on your system, `tox`
   will skip the tests for that environment. Ensure that you have the required
   Python versions installed if you want to run tests across all environments.

Run Tests for a Specific Environment
------------------------------------

To target a specific environment (e.g., Python 3.8), use the `-e` flag:

.. code-block:: bash

    tox -e py38

List All Available Environments
-------------------------------

To view all the environments configured in `tox.ini`, run:

.. code-block:: bash

    tox -l

Testing With `pytest`
=====================

For a quicker, single-environment test run, you can use `pytest`.

Install Dependencies in a Virtual Environment
----------------------------------------------

Linux/MacOS
~~~~~~~~~~~

.. code-block:: bash

    python3 -m venv .venv
    source .venv/bin/activate
    pip install poetry
    poetry install --no-root --all-extras

Windows
~~~~~~~

.. code-block:: powershell

    python -m venv .venv
    .venv\Scripts\activate
    pip install poetry
    poetry install --no-root --all-extras

Run Tests in the Current Environment
------------------------------------

Once the dependencies are installed, run the tests with:

.. code-block:: bash

    pytest

Stopping and Cleaning Up Docker Services
----------------------------------------

After testing, you can stop and remove the Docker containers with:

.. code-block:: bash

    docker-compose -f docker-compose.tox.yml down
