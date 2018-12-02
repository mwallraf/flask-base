#########################
MES server inventory
#########################

Version
=================

:Version: 1.0
:Last updated: 20-sep-2017
:Author: Maarten Wallraf


Description
======================

A list of all the servers used by MES in the datacenters.
We have to identify the server, hardware, applications and ownership.


Server list
===============

==============  =========================================
Servername      Function
==============  =========================================
stst01bru_      primary SSH stepstone server
stst01ant_      backup SSH stepstone server
syslog01bru_    syslog server
syslog01ant_    syslog server
tacacs01ant_    primary tacacs server
tacacs01bru_    backup tacacs server
script01bru_    script server
script02bru_    script server
nsm01bru_       primary SSG management server
nsm02bru_       backup SSG management server
nm5620bru-1_    primary ATM Newbridge server
nm5620ant-1_    backup ATM Newbridge server
isc01           primary ISC server
isc02           backup ISC server
testisc         test ISC and general dev server
oribi           Splunk server
boar            ``UNKNOWN``
boron           ``UNKNOWN``
grwclu01ant     groundwork cluster server
grwclu02ant     groundwork cluster server
grwclu03ant     groundwork cluster server
grwclu04ant     groundwork cluster server
grwclu05ant     groundwork cluster server
grwclu06ant     groundwork cluster server
grwclu07ant     groundwork cluster server
grwclu08nos     groundwork cluster servere
grwmon01ant     groundwork poller server
grwmon02ant     groundwork poller server
omeap1          OME servers
ntp01bru        NTP server
ntp01ant        NTP server
bdell101        ``UNKNOWN``
bdell102        ``UNKNOWN``
bdell103        ``UNKNOWN``
bdell104        ``UNKNOWN``
bdell106        ``UNKNOWN``
bdell107        prod/dev server for MES tools (duty, ..)
bdell108        prod server for MES tools (duty, ..)
bdell109        WEB server for MES tools (duty, ..)
==============  =========================================




Server details
================

stst01bru
---------------

primary SSH stepstone server

  ========================  ============
  **hostname**              stst01bru
  **dns name**              stst01bru.dcn.as47377.net
  **function**              PRIMARY MES stepping stone server to access all network equipment
  **applications**          SSH gateway, tftp server, inventory scripts under /opt (findhost, backups, configs, ...)
  **ip address(es)**        10.0.96.16/24, 91.208.220.16/25, 91.208.220.30/25, 62.58.62.158/32, 62.58.126.101/32
  **os**                    CentOS release 5.3 (Final)
  **location**              Nossegem
  **team**                  DOPS
  **backup**                ``UNKNOWN``
  **apps managed by**       DOPS
  **server managed by**     Tech Mahindra
  **appliance/virtual**     appliance
  **support contract**      ``UNKNOWN``
  **remarks**       
  ========================  ============


stst01ant
---------------

backup SSH stepstone server

  ========================  ============
  **hostname**              stst01ant
  **dns name**              stst01ant.dcn.as47377.net
  **function**              BACKUP MES stepping stone server to access all network equipment
  **applications**          SSH gateway, tftp server
  **ip address(es)**        10.0.32.16/24, 91.208.220.134/25
  **os**                    CentOS release 5.3 (Final)
  **location**              Antwerp
  **team**                  DOPS
  **backup**                ``UNKNOWN``
  **apps managed by**       DOPS
  **server managed by**     Tech Mahindra
  **appliance/virtual**     appliance
  **support contract**      ``UNKNOWN``
  **remarks**       
  ========================  ============


syslog01bru
---------------

syslog server

  ========================  ============
  **hostname**              syslog01bru
  **dns name**              syslog01bru
  **function**              syslog server for MES CPE + PE
  **applications**          syslog-ng
  **ip address(es)**        10.0.96.15/24
  **os**                    
  **location**              Nossegem
  **team**                  
  **backup**                
  **apps managed by**       
  **server managed by**     
  **appliance/virtual**     appliance
  **support contract**      
  **remarks**               ``The server is not present anymore in the rack, no replacement available``
  ========================  ============


syslog01ant
---------------

syslog server

  ========================  ============
  **hostname**              syslog01ant
  **dns name**              syslog01ant.dcn.as47377.net
  **function**              syslog collector for MES CPE + PE
  **applications**          syslog-ng
  **ip address(es)**        10.0.32.15/24, 91.208.220.143/25
  **os**                    debian 4.0
  **location**              Antwerp
  **team**                  DOPS
  **backup**                ``UNKNOWN``
  **apps managed by**       DOPS
  **server managed by**     Tech Mahindra
  **appliance/virtual**     appliance
  **support contract**      ``UNKNOWN``
  **remarks**       
  ========================  ============


tacacs01ant
---------------

primary tacacs server

  ========================  ============
  **hostname**              tacacs01ant
  **dns name**              tacacs01ant.dcn.as47377.net
  **function**              primary tacacs server for all MES equipment
  **applications**          Radiator
  **ip address(es)**        10.0.32.14/24, 91.208.220.142/25, 91.208.220.132/25, 91.208.220.133/25, 62.58.143.150/32, 62.58.157.150/32
  **os**                    debian 4.0
  **location**              Antwerp
  **team**                  DOPS
  **backup**                ``UNKNOWN``
  **apps managed by**       DOPS
  **server managed by**     Tech Mahindra
  **appliance/virtual**     appliance
  **support contract**      ``UNKNOWN``
  **remarks**       
  ========================  ============


tacacs01bru
---------------

backup tacacs server

  ========================  ============
  **hostname**              tacacs01bru
  **dns name**              tacacs01bru.dcn.as47377.net
  **function**              backup tacacs server for all MES equipment
  **applications**          Radiator
  **ip address(es)**        10.0.96.14/24, 91.208.220.14/25, 91.208.220.4/25, 91.208.220.5/25, 62.58.62.158/32, 62.58.126.101/32
  **os**                    debian 4.0
  **location**              Nossegem
  **team**                  DOPS
  **backup**                ``UNKNOWN``
  **apps managed by**       DOPS
  **server managed by**     Tech Mahindra
  **appliance/virtual**     appliance
  **support contract**      ``UNKNOWN``
  **remarks**       
  ========================  ============


script01bru
---------------

script server

  ========================  ============
  **hostname**              script01bru
  **dns name**              script01bru.dcn.as47377.net
  **function**              script server, MES tools like line migration, Harris tester, ...
  **applications**          apache, python, perl
  **ip address(es)**        10.0.96.101/24
  **os**                    debian 4.0
  **location**              Nossegem
  **team**                  DOPS
  **backup**                ``UNKNOWN``
  **apps managed by**       DOPS
  **server managed by**     Tech Mahindra
  **appliance/virtual**     appliance
  **support contract**      ``UNKNOWN``
  **remarks**       
  ========================  ============


script02bru
---------------

script server (staging)

  ========================  ============
  **hostname**              script02bru
  **dns name**              script02bru.dcn.as47377.net
  **function**              staging server for scripts
  **applications**          no dedicated applications
  **ip address(es)**        10.0.96.102/24
  **os**                    CentOS release 5.3 (Final)
  **location**              Nossegem
  **team**                  DOPS
  **backup**                ``UNKNOWN``
  **apps managed by**       DOPS
  **server managed by**     Tech Mahindra
  **appliance/virtual**     appliance
  **support contract**      ``UNKNOWN``
  **remarks**       
  ========================  ============


nsm01bru
---------------

primary SSG management server

  ========================  ============
  **hostname**              nsm01bru
  **dns name**              nsm01bru.dcn.as47377.net
  **function**              primary SSG management server
  **applications**          NSM firewall manager
  **ip address(es)**        10.0.96.191/24, 91.208.220.91/25
  **os**                    Juniper NSMXPress OS build 4.130764, NSM 2008.2r2
  **location**              Nossegem
  **team**                  DOPS
  **backup**                ``UNKNOWN``
  **apps managed by**       DOPS
  **server managed by**     Tech Mahindra
  **appliance/virtual**     appliance
  **support contract**      Infradata
  **remarks**       
  ========================  ============


nsm02bru
---------------

backup SSG management server

  ========================  ============
  **hostname**              nsm02bru
  **dns name**              nsm02bru.dcn.as47377.net
  **function**              backup SSG management server
  **applications**          NSM firewall manager
  **ip address(es)**        10.0.96.192/24, 91.208.220.92/25
  **os**                    Juniper NSMXPress OS build 4.130764, NSM 2008.2r2
  **location**              Nossegem
  **team**                  DOPS
  **backup**                ``UNKNOWN``
  **apps managed by**       DOPS
  **server managed by**     Tech Mahindra
  **appliance/virtual**     appliance
  **support contract**      Infradata
  **remarks**       
  ========================  ============


nm5620bru-1
---------------

primary ATM Newbridge server

  ========================  ============
  **hostname**              nm5620bru-1
  **dns name**              nm5620bru-1.dcn.as47377.net
  **function**              Primary Newbridge management server
  **applications**          Go-Global, Newbridge NM
  **ip address(es)**        10.0.96.205/24, 14.1.99.205/24
  **os**                    SunOS 5.10, Netra-T2000
  **location**              Nossegem
  **team**                  DOPS
  **backup**                ``UNKNOWN``
  **apps managed by**       DOPS
  **server managed by**     Tech Mahindra
  **appliance/virtual**     appliance
  **support contract**      Alcatel
  **remarks**               Currently in disabled state to make Antwerp the primary server.
                            Check/stop/start services with ``sh /opt/netmgt/bin/RED_comms``
  ========================  ============


nm5620ant-1
---------------

backup ATM Newbridge server

  ========================  ==================================================================================================================
  **hostname**              nm5620ant-1
  **dns name**              nm5620ant-1.dcn.as47377.net
  **function**              Backup Newbridge management server
  **applications**          Go-Global, Newbridge NM
  **ip address(es)**        10.0.96.205/24, 14.1.99.205/24
  **os**                    SunOS 5.10, Netra-T2000
  **location**              Antwerp
  **team**                  DOPS
  **backup**                ``UNKNOWN``
  **apps managed by**       DOPS
  **server managed by**     Tech Mahindra
  **appliance/virtual**     appliance
  **support contract**      Alcatel
  **remarks**               Currently in forced to be the primary server.
                            Check/stop/start services with ``sh /opt/netmgt/bin/RED_comms``
  ========================  ==================================================================================================================


TEMPLATE
---------------

description

  ========================  ============
  **hostname**              
  **dns name**              
  **function**              
  **applications**          
  **ip address(es)**        
  **os**                    
  **location**              
  **team**                  
  **backup**                ``UNKNOWN``
  **apps managed by**       
  **server managed by**     
  **appliance/virtual**     
  **support contract**      ``UNKNOWN``
  **remarks**       
  ========================  ============

