#!/usr/bin/bash

cd /Users/mwallraf/dev/flask-base/external_scripts
source ../venv/bin/activate

hostname="$1"
username="$2"
password="$3"
driver="$4"
cmdfile="$5"


python netmiko_test.py --hostname=$hostname --username=$username --password=$password --driver=$driver --cmdfile=$cmdfile

rm -rf $cmdfile

