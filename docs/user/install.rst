.. _install:

************
Installation
************

Recommended Specifications
==========================

 * Windows 64-bit operating system
 * At least 2GHz clock speed CPU
 * At least 8GB RAM

32-bit Windows operating systems are supported; however, the memory capabilities
of such a system may not be sufficient for large simulations using DTOcean.
Currently, Windows is the only supported operating system.

Graphical Application
=====================

The DTOcean graphical application is packaged as a standalone wizard-based 
installer or as an `Anaconda Python Distribution`_ package. The Anaconda 
packages are released most frequently to test bug fixes and new features 
before including them in a standalone installer release. Thus, the standalone 
installer should be considered as more stable than the Anaconda version. 

Installation Wizard
-------------------

The latest version of the DTOcean installation wizard can be downloaded from
`Github <https://github.com/DTOcean/dtocean/releases>`_.

Download the installer for  your system architecture and then double-click the
file. Follow the on-screen prompts to complete the installation.

Note, when using the "All Users" option, uninstallation can only be conducted
using the account that was used to install DTOcean.

Once installed, start DTOcean from the Windows start menu folder appropriate
to your architecture. For instance, for a 64-bit architecture DTOcean is found
in the "DTOcean (64-bit)" folder.

DTOcean can be uninstalled through the link in the Windows start menu folder or
using the control panel.

Anaconda Package
----------------

Alternatively, DTOcean is also available to install using the `Anaconda Python
Distribution`_. Once Anaconda is installed, the following steps can be used to 
install DTOcean:

1. Open the "Anaconda Prompt" program from the "Anaconda" Windows start menu
   folder
2. Create an environment for DTOcean::

    conda create -n _dtocean python=2.7

3. Activate the environment::

    conda activate _dtocean

4. Download the |.condarc|_ file for dtocean-app, save it and copy it to the 
   root of the environment::

    copy .condarc %CONDA_PREFIX%

4. Install the DTOcean application and modules (this step may take some time)::

    conda install dtocean-app ^
                  dtocean-hydrodynamics ^
                  dtocean-electrical ^
                  dtocean-moorings ^
                  dtocean-installation ^
                  dtocean-maintenance ^
                  dtocean-economics ^
                  dtocean-reliability ^
                  dtocean-environment

In the above steps, press enter or answer "y" when prompted.

The DTOcean Hydrodynamics Data package must be installed separately and can
be downloaded from `Github <https://github.com/DTOcean/dtocean/releases>`__.
Download the installer and double-click the file. Follow the on-screen prompts
to complete the installation.

DTOcean can now be started using the following steps:

1. Open the "Anaconda Prompt" program from the "Anaconda" Windows start menu
   folder
2. Activate the \_dtocean environment::

    conda activate _dtocean

3. Start the dtocean application::

    dtocean-app

4. Optionally, start dtocean in debug mode::

    dtocean-app --debug

DTOcean can be uninstalled with the following process:

1. Open the "Anaconda Prompt" program from the "Anaconda" Windows start menu
   folder
2. Remove the \_dtocean environment::

    conda remove -n _dtocean --all

3. Uninstall the DTOcean Hydrodynamic Data through the Windows start menu or
   control panel.

.. _database_installation:

Database
========

The use of DTOcean is supported by a persistent PostgreSQL database. The
latest version of the database package can be downloaded from `Github
<https://github.com/DTOcean/dtocean-database/releases>`__ and installation
instructions are included within the package.

.. _configuration_files:

Configuration Files
===================

Updating
--------

When upgrading DTOcean, it may be necessary to update its configuration files. 
This is particularly important for users of DTOcean version 1.*, moving to 
version 2.*. Options for updating the database and logging configuration files 
are: 

    * overwriting old files with the new default settings (which requires no 
      further user interaction) or,
    * copying the new configuration files alongside the old, so that the user 
      can manually merge them.

The method for updating the configuration files varies depending on how DTOcean
was installed.

Installation Wizard
-------------------

If DTOcean was installed using the installation wizard, then utility functions
are included in the DTOcean start menu folder alongside the main executable
(and in the **Config** folder for Windows versions prior to Windows 8).

The utilities are named as follows:

Database:
    * Overwrite Database Config
    * Copy Database Config (Safe)

Logging:
    * Overwrite Logger Config
    * Copy Logger Config (Safe)

Anaconda Package
----------------

If DTOcean is installed as an Anaconda package then the configuration files
are updated using specific command line utilities.

.. rubric:: Database:

To update the database configuration files:

1. Open the "Anaconda Prompt" program from the "Anaconda" Windows start menu
   folder
2. Activate the \_dtocean environment::

    conda activate _dtocean

3. Copy the new configuration files next to the old::

    dtocean-core-config database

4. Or, overwrite the old files::

    dtocean-core-config database --overwrite

.. rubric:: Logging:

To update the logger configuration files:

1. Open the "Anaconda Prompt" program from the "Anaconda" Windows start menu
   folder
2. Activate the \_dtocean environment::

    conda activate _dtocean

3. Copy the new configuration files next to the old::

    dtocean-app-config logging

4. Or, overwrite the old files::

    dtocean-app-config logging --overwrite

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

.. _Anaconda Python Distribution: https://www.anaconda.com/download/

.. |.condarc| replace:: ``.condarc``
.. _.condarc: https://raw.githubusercontent.com/DTOcean/dtocean-app/master/.condarc
