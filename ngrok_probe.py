import os
import requests
import json

from paramiko import SSHClient, AutoAddPolicy
from paramiko.ssh_exception import NoValidConnectionsError, AuthenticationException

def get_ngrok_host_port():
    '''
    an example would be
    {
    "tunnels": [
        {
        "name": "ssh",
        "uri": "/api/tunnels/ssh",
        "public_url": "tcp://0.tcp.ngrok.io:19277",
        "proto": "tcp",
        "config": {
            "addr": "localhost:22",
            "inspect": false
        },
        "metrics": {...}
        }
    ],
    "uri": "/api/tunnels"
    }
    '''
    host, port = None, None
    try:
        # check if localhost:4040 result is valid
        response = requests.get("http://127.0.0.1:4040/api/tunnels")
        if response.status_code != 200:
            return host, port
        tunnels = json.loads(response.text)
        print(tunnels)

        # expect public_url to be "tcp://0.tcp.ngrok.io:19277"
        # parse port forcefully and get None if failed
        host = tunnels['tunnels'][0]['public_url'].split(':')[1].lstrip("/")
        port = tunnels['tunnels'][0]['public_url'].split(':')[-1]
    except:
        pass
    return host, port


host, port = get_ngrok_host_port()

if not host and not port:
    print("restart ngrok")
    exit()

client = SSHClient()
client.set_missing_host_key_policy(AutoAddPolicy())

try:
    print("try connect to {}:{}".format(host, port))
    client.connect(host, port=port, username="jonas")
    print("ngrok is working")
except NoValidConnectionsError:
    print("NoValidConnectionsError restart ngrok")
except AuthenticationException:
    print("AuthenticationException restart ngrok")
except Exception:
    print("Exception network is disconnected")
