# -*- coding: utf-8 -*-
#!/usr/bin/python
import sys
import json
if sys.version_info[0] >= 3:
    from importlib import reload
reload(sys)  # Reload does the trick!
if sys.version_info[0] < 3:
    sys.setdefaultencoding('UTF8')
import codecs
# UTF8Writer = codecs.getwriter('utf8')
# sys.stdout = UTF8Writer(sys.stdout)

import time
import subprocess
import shlex

if sys.version_info[0] < 3:
    import ConfigParser
else:
    import configparser
import os
from sys import platform
if platform == "win32":
    import pbs
else:
    import sh
from os.path import exists
from time import sleep
from hs_api import hsApi

class deviceInfo:
    debug = False
    def __init__(self, UDID, access_token):
        self.hs_api_call = hsApi(UDID, access_token)
        self.UDID = UDID
        self.ACCESS_TOKEN = access_token 

    def get_hostname(self):
        return self.hs_api_call.device_details['hostname']

    def get_os_version(self):
        return self.hs_api_call.device_details['os_version']

    def get_owner(self):
        return self.hs_api_call.device_details['device']['owner']

    def get_device_model(self, udid):
        try:
            return self.hs_api_call.device_details['device_skus'][0]
        except:
            if platform == "win32":
                adb_comm = pbs.Command('adb')
            else:
                adb_comm = sh.Command('adb')
            return adb_comm('-s', udid, 'shell', 'getprop', 'ro.product.model').strip()

    def get_network_name(self):
        return self.hs_api_call.device_details['operator']


    def get_package_list(self):
        package_list = self.hs_api_call.run_adb_command("pm list package")
        return package_list

    def get_app_version(self, app_package):
        app_version = None
        if self.hs_api_call.device_os == "android":
            version_details = str(self.hs_api_call.run_adb_command("dumpsys package {}| grep versionName".format(app_package)))
            app_version = version_details.split('=')[1].strip()
            if "\n" in app_version:
                app_version = app_version.split("\n")[0]
            app_version = app_version.replace("'","")
        elif self.hs_api_call.device_os == "ios":
            apps = self.hs_api_call.get_app_list_ios()
            for app in apps['data']:
                if app['CFBundleIdentifier'] == app_package:
                    app_version = app['CFBundleShortVersionString']
                    break
        return app_version

    # See if connection is on WIFI or MOBILE
    def get_connection_type(self):
        connection = self.hs_api_call.device_details['network_type']
        print("Connected to " + str(connection))
        return connection

            
