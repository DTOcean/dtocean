.. _install:

************
Installation
************

Recommended Specifications
==========================

 * Windows or Linux 64-bit operating system
 * At least 2GHz clock speed CPU
 * At least 8GB RAM

Application
===========

The DTOcean suite, including the desktop application, can be installed from
`PyPI <https://pypi.org/>`_. Standalone wizard-based installers and `Conda`_
packages are currently not available, but may be reimplemented in the future.

PyPI
----

Ensure that a compatible Python version (see the :ref:`Index <index>` page) is
available on the command line [#f1]_. Use pip to install the dtocean suite::

    pip install dtocean

Once the dtocean packages are installed, an initialization step is required
to download large files and add a desktop shortcut::

    dtocean init

Once this command has completed, as shortcut called "DTOcean" should be
available in the OS start menu, which will open the DTOcean desktop
application.

.. _database_installation:

Database
========

The use of DTOcean is supported by a persistent PostgreSQL database. The latest
version of the database package can be downloaded from `Github
<https://github.com/DTOcean/dtocean-database/releases>`__ and installation
instructions are included within the package.

.. _configuration_files:

Configuration Files
===================

Updating
--------

When upgrading DTOcean, it may be necessary to update its configuration files. 
Options for updating the database and logging configuration files are: 

    * overwriting old files with the new default settings (which requires no 
      further user interaction) or,
    * copying the new configuration files alongside the old, so that the user 
      can manually merge them.

The configuration files are updated using specific command line utilities.

.. rubric:: Database:

To update the database configuration files:

1. Copy the new configuration files next to the old::

    dtocean core config database

2. Or, overwrite the old files::

    dtocean core config database --overwrite

.. rubric:: Logging:

To update the logger configuration files:

1. Copy the new configuration files next to the old::

    dtocean core config logging

2. Or, overwrite the old files::

    dtocean core config logging --overwrite

File Locations
--------------

The location of the configuration files, if the user chooses to merge their old
settings into the new configuration file, are:

Database:
    ``C:\Users\<USERNAME>\AppData\Roaming\DTOcean\dtocean_core\config\database.yaml``
    ``C:\Users\<USERNAME>\AppData\Roaming\DTOcean\dtocean_core\config\database.yaml.new``

Logging:
    ``C:\Users\<USERNAME>\AppData\Roaming\DTOcean\dtocean_app\config\logging.yaml``
    ``C:\Users\<USERNAME>\AppData\Roaming\DTOcean\dtocean_app\config\logging.yaml.new``

.. rubric:: Footnotes

.. [#f1] it is recommended to also use an isolated Python virtual environment
    (e.g. see `Virtual Environments and Packages
    <https://docs.python.org/3/tutorial/venv.html>`_)

.. _Conda: https://conda-forge.org/

.. |.condarc| replace:: ``.condarc``
.. _.condarc: https://raw.githubusercontent.com/DTOcean/dtocean-app/master/.condarc
