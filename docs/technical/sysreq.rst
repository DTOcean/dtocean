.. _tech_sysreq:

System Requirements
===================

The DTOcean software, tools, scripts, manual and tutorial developed by the
project consortium are available through the DTOcean project repository. The
project repository is the developed to host the final and official version of
the DTOcean tool.

The latest version of the DTOcean tool can be downloaded at the following
address: https://setis.ec.europa.eu/dt-ocean/

A search functionality allows user to look for specific modules of the tool, to
access manuals and tutorials available.


Software
--------

The following established systems were chosen to provide the underpinning
software architecture of the system:

 * Python 2.7: The programming language of the software
 * PostgreSQL 9.4: The database management system (including PostGIS
   extensions)
 * Qt4: The graphical user interface framework

Target Deployment System
------------------------

A typical mid-range Windows system was chosen as the target deployment system.
Such a system would have the following specifications:

 * Windows 64-bit operating system
 * CPU cores with at least 2 GHz clock speed each
 * 8GB RAM

Note that it should be possible to support 32-bit Windows operating systems;
however, the memory capabilities of such a system may not be sufficient for the
DTOcean software. It is also anticipated that the database manager (PostgreSQL)
will be installed on the same machine as the Python based software.
