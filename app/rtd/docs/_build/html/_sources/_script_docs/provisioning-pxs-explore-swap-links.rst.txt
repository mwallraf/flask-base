########################################
Proximus Explore - Swap main-backup
########################################

Version
=================

:Version: 1.0
:Last updated: 05-oct-2017
:Author: Maarten Wallraf


Description
======================

This script will enable the Proximus Explore links in Antwerp and disable them in Nossegem (or vice versa)

Due to the issues with Proximus Explore in the past we only keep a single path active at the same time. Manual intervention is required to swap the lines from primary to backup and vice versa.


Usage
===============

``cd /opt/SCRIPTS/provisioning-scripts/pxs-explore-swap-links``

``./pxs-explore-swap.sh``

The script will ask some user input:

    Select the primary site: Antwerp or Nossegem

    Simulation or production


Change types
================

Simulation
---------------

In simulated mode all the config changes are generated and saved to the details output file.

No changes are made to network devices.


Production
----------------

Changes are directly written to the network devices


Logging
==============

result.txt
----------------

This file will contain a summary of the changes done.

result-details.txt
--------------------

This file contains all the changes that are executed on the network devices.

log folder
-------------------

The log folder contains debug connection log files for each device


Security
================

The script can only be accessed by members of the "scriptdev" group. Currently only the DOPS team is a member of this group.

Once the script is executed an extra confirmation is asked but no extra username + password is required.

