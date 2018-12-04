
from netmiko import ConnectHandler
from datetime import datetime
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("--hostname", help="Hostname")
parser.add_argument("--username", help="Username")
parser.add_argument("--password", help="Password")
parser.add_argument("--driver", help="Driver")
parser.add_argument("--cmdfile", help="Command file")
args = parser.parse_args()

start_time = datetime.now()

device = {
	'device_type': args.driver,
	'ip': args.hostname,
	'username': args.username,
	'password': args.password,
	'secret': args.password,
	'verbose': False
}

remote_conn = ConnectHandler(**device)
print()
print('#' * 80)
remote_conn.enable()
with open(args.cmdfile) as fd:
	lines = fd.read().splitlines()
for l in lines:
	print(remote_conn.send_command(l))
#print(remote_conn.send_command("show run"))
#print(remote_conn.send_command("show version"))
print('#' * 80)
print()

print("\nElapsed time: " + str(datetime.now() - start_time))

