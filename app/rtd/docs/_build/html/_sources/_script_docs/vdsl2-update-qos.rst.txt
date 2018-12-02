==========
VDSL2 UPDATE QOS 
==========

*******
Version
*******

Current version = ``v1.0``

***************
Description
***************

Compares the configured bandwidth and QOS settings for VDSL2 Shared Vlan VT's with the settings in Orange Frontix for the latest Proximus TBF lineprofile result. If there is a mismatch then the CPE is updated.

Actions done by the script:

    * download the VDSL bandwidth report from Splunk and generate a list of hostnames that should be upgraded
    * login to the hostname and remove all QOS settings
    * configure QOS and change the Dialer interface bandwidth
    * re-apply QOS and set a description with the current date + line profile


************
Restrictions
************

Following restrictions are in place, VT's not matching the criteria will be skipped

    * The maximum download bandwidth is 70 MB
    * The minimum upload bandwidth is 1 MB
    * A VT will never be updated 2 days in a row, this is to avoid that the router will be updated unnecessarily due to a delay in the inventory reporting

***************
Usage
***************

To run the script for all VT's that need to be updated:

    ``./run.sh``


Run the script on a filtered set of VT's:

    ``./run.sh --filter VT12345``

The filter will ONLY work if the line profile of the VT is not correct. If the VT already has a correct line profile then nothing will be done.

If no filter is applied and the script should run on all available VT's then you have to add the option --all

    ``./run.sh --all``

Run the script so that the PPP session will be reset after updating QOS, this will create an outage but it will ensure that the PE router will receive the correct QOS as well. The default value is NO PPP reset.

    ``./run.sh --pppreset``




