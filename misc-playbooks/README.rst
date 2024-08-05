=============
misc-playbook
=============

**misc-playbook** is an Ansible playbook designed to manage and deploy
configurations using a collection of in-tree roles. This project is intended to
simplify the automation of various system tasks across multiple environments.

Project Structure
==================

The project is organized as follows:

.. code-block:: shell

    misc-playbook
    ├── README.rst
    ├── <playbook>.yml
    ├── conf
    │   ├── inventory
    │   │   ├── node-000.config.sample
    │   │   └── node-000.ini.sample
    │   ├── justfile.sample
    │   └── vars
    │       └── extra.yml.sample
    ├── justfile
    ├── roles
    │   ├── <role>
    │   │   ├── defaults
    │   │   │   └── main.yml
    │   │   └── tasks
    │   │       ├── debian
    │   │       │   └── main.yml
    │   │       └── main.yml
    │   ├── <role>
    │   │   └── ...
    │   │       └── ...
    │   ├── ...
    │       └── ...
    │           └── ...
    └── scripts
        └── genvars.sh

    23 directories, 24 files

Getting Started
===============

1. **Install Dependencies**:

   .. code-block:: bash

      <dependencies>

   .. code-block:: bash

      # For Debian/Ubuntu
      sudo apt-get install ansible

      # For CentOS/RHEL
      sudo yum install ansible

2. **Start a Control Node Configuration**:

   Run the command:

   .. code-block:: bash

      just init <config>
      cd <config>
      just
