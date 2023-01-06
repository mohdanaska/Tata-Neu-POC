# -*- coding: utf-8 -*-
from __future__ import print_function
import os
import time
import traceback
from device_info import deviceInfo
from hs_api import hsApi

def add_addiational_args(parser, addiational_args):
    for key in addiational_args:
        args_spec = addiational_args[key]
        if args_spec['type'] == 'FLAG':
            parser.add_argument('--' + key, '--' + key,
                                dest=key,
                                action='store_true',
                                default=None,
                                required=False,
                                help=key)
        else:
            parser.add_argument('--' + key, '--' + key, dest=key,
                                type=str, nargs='?',
                                default=None,
                                required=False,
                                help=key)


def get_args(script_location, addiational_args=None):
    # print("get_args")
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--udid', '--udid', dest='udid',
                        type=str, nargs='?',
                        default=None,
                        required=False,
                        help="udid")

    parser.add_argument('--appium_input', '--appium_input', dest='appium_input', 
                        type=str, nargs='?',
                        default=None,
                        required=False,
                        help="appium_input")

    parser.add_argument('--working_dir', '--working_dir', dest='working_dir',
                        type=str, nargs='?',
                        default=None,
                        required=False,
                        help="working_dir")

    parser.add_argument('--private_key_file', '--private_key_file', dest='private_key_file',
                        type=str, nargs='?',
                        default=None,
                        required=False,
                        help="private_key_file")

    parser.add_argument('--network_type', '--network_type', dest='network_type',
                        type=str, nargs='?',
                        default="MOBILE",
                        required=False,
                        help="network_type")   

    parser.add_argument('--selector','--selector', dest='selector',
                        type=str,nargs='?',
                        default=None,
                        required=False,
                        help="selector")

    parser.add_argument('--selector2','--selector2', dest='selector2',
                        type=str,nargs='?',
                        default=None,
                        required=False,
                        help="selector2") 

    parser.add_argument('--app_package_name', '--app_package_name', dest='app_package_name',
                        type=str, nargs='?',
                        default=None,
                        required=False,
                        help="app_package_name")

    if addiational_args:
        add_addiational_args(parser, addiational_args)
    args = parser.parse_args()
    return args, parser

def init_args(args, self):
    self.verify_kpi_with_log = False
    self.valid_start = False
    self.udid = args.udid
    self.appium_input = args.appium_input
    self.working_dir = args.working_dir
    self.private_key_file = args.private_key_file
    self.url = self.appium_input
    self.network_type = args.network_type
    self.selector= args.selector
    self.selector2= args.selector2
    self.app_package_name=args.app_package_name
    self.access_token = self.url.split('/')[4]
    if 'localhost' in self.url or '0.0.0.0' in self.url or  not self.private_key_file:
        self.running_on_pbox = True
    self.valid_start = True

    #For cases where driver is not used to launch app
    self.relaunch_start = None
    self.control_lock = False

    if self.udid:
        self.hs_api_call = hsApi(self.udid, self.access_token)
        self.device_country = self.hs_api_call.device_country()
        print("Country: ",self.device_country)
    else:
        self.selector = self.selector + ":" + self.selector2
        self.device_country = self.selector2
        print("Country: ",self.device_country)

def init_caps(self, video_only=False, auto_launch = True):
    # desired caps for the app
    self.desired_caps = {}
    self.desired_caps['platformName'] = self.os
    self.desired_caps['udid'] = self.udid
    self.desired_caps['deviceName'] = self.udid

    try:
        self.desired_caps['headspin:selector'] = self.selector
        self.desired_caps['headspin:deviceStrategy'] = "random"
        self.desired_caps['headspin:waitForDeviceOnlineTimeout'] = 5900
        self.desired_caps['newCommandTimeout'] = 320
        self.desired_caps['headspin:ignoreFailedDevices'] = False
    except:
        self.desired_caps['udid'] = self.udid
        self.desired_caps['deviceName'] = self.udid

    if self.os.lower() == "android":
        self.desired_caps['appPackage'] = self.package
        self.desired_caps['appActivity'] = self.activity
        self.desired_caps['automationName'] = "UiAutomator2"
        self.desired_caps['autoGrantPermissions'] = True
        self.desired_caps['disableWindowAnimation']= True

    elif self.os.lower() == "ios":
        self.desired_caps['automationName'] = "XCUITest"
        self.desired_caps['bundleId'] = self.package
        self.desired_caps['autoAcceptAlerts'] = True
    if self.no_reset:
        self.desired_caps['noReset'] = self.no_reset
    self.desired_caps['autoLaunch'] = auto_launch
    self.desired_caps['newCommandTimeout'] = 3000    
    
    if self.use_capture:
        if video_only:
            self.desired_caps['headspin:capture.video'] = True
            self.desired_caps['headspin:capture.network'] = False
        else:
            self.desired_caps['headspin:capture'] = True
    
    if self.control_lock:
        self.desired_caps['headspin:controlLock'] = True
    
    return self

def device_state_var(self):

    self.device_info = deviceInfo(self.udid, self.access_token)
    self.hostname = self.device_info.get_hostname()
    self.connection_status = self.device_info.get_connection_type()

    self.hs_api_call = hsApi(self.udid, self.access_token)
    self.network_name = ""
    self.network_name = self.device_info.get_network_name()
    
    if self.os.lower() == "android":
        if self.connection_status:
            if self.network_type not in self.connection_status :
                if 'WIFI' in self.network_type:
                    self.hs_api_call.run_adb_command("svc wifi enable")
                    self.hs_api_call.run_adb_command("svc data disable")
                    print("changing to WIFI")
                    self.connection_status = "WIFI"
                else:
                    self.hs_api_call.run_adb_command("svc wifi disable")
                    self.hs_api_call.run_adb_command("svc data enable")
                    print("changing to MOBILE")
                    self.connection_status = "MOBILE"
                time.sleep (3)
        else:
            if 'WIFI' in self.network_type:
                self.hs_api_call.run_adb_command("svc wifi enable")
                self.hs_api_call.run_adb_command("svc data disable")
                print("changing to WIFI")
                self.connection_status = "WIFI"
            else:
                self.hs_api_call.run_adb_command("svc wifi disable")
                self.hs_api_call.run_adb_command("svc data enable")
                print("changing to MOBILE")
                self.connection_status = "MOBILE"
            time.sleep (3)
        
    try:
        self.apk_version = self.device_info.get_app_version(self.package)
        print("App Version: ", self.apk_version)
    except Exception as error:
        print (error)
        self.apk_version = None
        print('Get apk_version Failed', self.package)

def device_range_var(self):
    low=["D638017310193078","0123456789ABCDEF","056053109C110350","056053109Q143127","0586624M3T007195","05678310AM030742","ZH33L3NCN7","SKY97PSO9PZH4HTW","KNPVGATSMVPZKJ4P","RZ8R11WLGNE","R9ZN8036EHR","958599OVINMZXKFA","145117a40706","96f0f41e","5de7d0727d2b"]
    mid=["062453112K025282","5e6e8046d920f90a4818f250c37a47ecad22fa02","RCK7D6F6AACU8H69","9018da89","L7ROC64T7H6TPBYH","R9BN6002VKJ","1367666921002T1"]
    high=["00008101-001939DE0C00001E", "36072b93", "8483a21c"]
    if self.udid in low:
        self.device_range="LOW_RANGE"
        print('Device is low range')
    elif self.udid in mid:
        self.device_range="MID_RANGE"
        print('Device is mid range')
    elif self.udid in high:
        self.device_range="HIGH_RANGE"
        print('Device is high range')
    else:
        print('Range not specified')


