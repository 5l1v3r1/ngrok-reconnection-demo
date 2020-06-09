#!/usr/bin/env python3
import os
import json
import time
import psutil
import socket
from applicationinsights import TelemetryClient

def get_ngrok_tunnel_port():
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
    tunnels = None
    port = None
    try:
        # check if localhost:4040 result is valid
        tunnels_status = os.popen('curl http://127.0.0.1:4040/api/tunnels').read()
        tunnels = json.loads(tunnels_status)

        # expect public_url to be "tcp://0.tcp.ngrok.io:19277"
        # parse port forcefully and get None if failed
        port = tunnels['tunnels'][0]['public_url'].split(':')[-1]
    except:
        pass
    return tunnels, port

for x in range(60):
    # collect info
    hostname = socket.gethostname()
    cpu_percent = psutil.cpu_percent()
    memory = psutil.virtual_memory()
    disk = psutil.disk_io_counters()
    sensors = psutil.sensors_temperatures()
    cpu_sensors = sensors.get('coretemp', {})
    cpu_temperature = 0
    if len(cpu_sensors) > 0:
        cpu_temperature = cpu_sensors[0].current
    os_disk_temperature = int(os.popen("/usr/sbin/hddtemp /dev/sda2 | awk '{print $NF}' | sed 's/°C//g'").read())
    data_disk_temperature = int(os.popen("/usr/sbin/hddtemp /dev/sda2 | awk '{print $NF}' | sed 's/°C//g'").read())
    tunnels, port = get_ngrok_tunnel_port()

    # send data to app insights
    payload = {
        'hostname': hostname,
        'cpu_percent': cpu_percent,
        'memory_percent': memory.percent,
        'disk_read_count': disk.read_count,
        'disk_write_count': disk.write_count,
        'disk_read_bytes': disk.read_bytes,
        'disk_write_bytes': disk.write_bytes,
        'disk_read_time': disk.read_time,
        'disk_write_time': disk.write_time,
        'cpu_temperature':  cpu_temperature,
        'os_disk_temperature': os_disk_temperature,
        'data_disk_temperature': data_disk_temperature,
        'ngrok_tunnels': tunnels,
        'ngrok_port': port
    }
    print(payload)

    # APP_INSIGHTS_KEY = '8ca53461-97e4-49a4-b0bc-c4d174602aa9' # aicsapi-dev
    APP_INSIGHTS_KEY = 'f0026a78-240d-4ca0-b58a-9ff411fb231c' # FR
    EVENT_TAG = 'smart-retail-sea-monitor'
    tc_client = TelemetryClient(APP_INSIGHTS_KEY)
    tc_client.track_event(EVENT_TAG, payload)
    tc_client.flush()

    time.sleep(1)

