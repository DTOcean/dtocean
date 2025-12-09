.. _user_reliability:

Reliability Assessment Module
-----------------------------

Reliability assessment module aims at assessing the reliability of the array
configuration determined by the design modules (Electrical Sub-Systems and
Moorings and Foundations). RAM conducts reliability calculations for i) the
user and ii) to inform operations and maintenance requirements of the O&M
module. 

The purpose of the RAM is then to:

 * Generate a system-level reliability equation based on the
   inter-relationships between sub-systems and components (as specified by the
   Electrical Sub-Systems and Moorings and Foundations component hierarchies
   and by the user)
 * Provide the user with the opportunity to populate sub-systems not covered
   by the DTOcean software (e.g. power take-off, control system) using a
   GUI-based Reliability Block Diagram
 * Consider multiple failure severity classes (i.e. critical and
   non-critical) to inform repair action maintenance scheduling. This will
   represent a simplified approach to Failure Mode and Effects Analysis (FMEA)
 * Carry out normal, optimistic an d pessimistic reliability calculations to
   determine estimation sensitivity to failure rate variability and quality
   analysis
 * Provide the time-dependent failure estimation model (in the O&M module)
   with the Time to failure (TTF) of components within the system

RAM produces:

 * A pass/fail Boolean compared to user-defined threshold
 * Distribution of system reliability (%) from mission start to mission end
   (0≤t≤T). 
 * Mean time to failure (MTTF) of the system, sub-systems and components
   presented to the user in a tree format 
 * Risk Priority Numbers (RPNs)

 
Architecture
^^^^^^^^^^^^

The RAM comprises two Python modules (figure below). RAM_Main.py acts as an
interface between the user and the module and also calls the functions within
the RAM. RAM_Core.py comprises the classes and functions required to carry out
statistical analysis of the system. As can be seen from the interactions
diagram with RAM_Core.py there is interaction between the functions within the
Syshier class.


.. _fig-ram-user:

.. figure:: /images/user/ram.png

   Interaction between the various classes and methods of the Reliability Assessment sub-module


Functional specifications
^^^^^^^^^^^^^^^^^^^^^^^^^

Inputs
''''''

Inputs to the Reliability assessment module are provided by the electrical
module, the moorings and foundations module, the database and the user.  A list
of the inputs required are as follows:


.. _fig-ram-inputs:

.. figure:: /images/user/ram_inputs.png

   Inputs to the Reliability assessment module

