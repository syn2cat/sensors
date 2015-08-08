#!/usr/bin/env python3
import os
import time
import yaml
import mongoengine
import datetime
import requests

base_url = "https://api.particle.io/v1/devices/"

config = None
with open("/etc/l2-sensors/conf.yml", 'r') as f:
    config = yaml.load(f.read())
if config is None:
    raise ValueError("Failed to load configuration.")

mongoengine.connect(
    'particule',
    host=os.environ['DB_PORT_27017_TCP_ADDR'],
    port=int(os.environ['DB_PORT_27017_TCP_PORT']),
    username=config['db']['mongo']['username'],
    password=config['db']['mongo']['password']
)


class Measure(mongoengine.DynamicDocument):
    _date = mongoengine.DateTimeField(default=datetime.datetime.now)
    meta = {
        'indexes': [
            {'fields': ['name', '_date']}
        ],
    }

while True:
    try:
        for device in config['devices']:
            for variable in device['variables']:
                res = requests.get("%s%s/%s?access_token=%s" %
                    (
                        base_url,
                        device['id'],
                        variable,
                        config['token']
                    )
                )
                Measure(**res.json()).save()
    except (KeyboardInterrupt, SystemExit):
        break
    except Exception as e:
        print(e)
    finally:
        time.sleep(600)
