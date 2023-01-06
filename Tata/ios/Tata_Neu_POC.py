# -*- coding: utf-8 -*-
#!/usr/bin/python
import time
from time import sleep
import os
import unittest
import sys
import json
import traceback
import logging
from appium import webdriver
import urllib3
urllib3.disable_warnings()
#Needed as the app name is non-ASIC value
if sys.version_info[0] >= 3:
    from importlib import reload
reload(sys)  # Reload does the trick!
if sys.version_info[0] < 3:
    sys.setdefaultencoding('UTF8')
import codecs
# UTF8Writer = codecs.getwriter('utf8')
# sys.stdout = UTF8Writer(sys.stdout)
from appium.webdriver.common.mobileby import MobileBy
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from appium.webdriver.common.touch_action import TouchAction
from selenium.webdriver.common.actions.action_builder import ActionBuilder
from selenium.webdriver.common.actions.interaction import POINTER_TOUCH
from selenium.webdriver.common.actions.mouse_button import MouseButton
# Custom Libs
script_dir = os.path.dirname(os.path.abspath(__file__))
app_dir = os.path.dirname(script_dir)
root_dir = os.path.dirname(app_dir)
py_modules_dir = os.path.join(root_dir, 'setup/py_modules' )
google_play_folder = os.path.join(root_dir, 'google_play_store')
sys.path.append(script_dir)
sys.path.append(root_dir)
# sys.path.append(google_play_folder)
sys.path.append(app_dir)
sys.path.append(py_modules_dir)
from alerts import SendAlert
import tata_lib
from hs_logger import logger, setup_logger
from hs_api import hsApi
import session_visual_lib as session_visual_lib
import label_categories as label_categories
import kpi_names as kpi_names
import args_lib as args_lib
from action_lib import HeadSpinAndroidAction
class TataPoc(unittest.TestCase):
    debug = False
    use_capture = True
    video_only = True
    no_reset = True
    app_size_info = False
    autoLaunch = False
    app_name = "Tata"
    package = "com.tatadigital.tcp.dev"  
    test_name = "Tata Neu POC test"  
    implicitly_wait_time_long = 10000
    implicitly_wait_time = 60
    delta_time = 5
    def init_vars(self):
        self.reference = str(int(round(time.time() * 1000)))
        self.KPI_COUNT = 1
        self.pass_count = 0
        self.working_dir = None
        self.private_key_file = None
        self.os = 'ios'
        self.valid_start = False
        self.running_on_pbox = False
    def init_workflow(self, video_only=False):
        args, parser = args_lib.get_args(__file__)
        args_lib.init_args(args, self)
        args_lib.init_caps(self, video_only=video_only, auto_launch = self.autoLaunch)
        tata_lib.init_timing(self)
        args_lib.device_state_var(self)
    
    def setUp(self):
        setup_logger(logger, logging.DEBUG)
        self.init_vars()
        self.init_workflow(video_only=self.video_only )
        logger.info("launching app".format(self.package))
         # launching app
         # CAREFUL there is api call being made in hsApi init
         #logger.info("launching app".format(self.package)
        self.desired_caps['headspin.controlLock'] = True
        self.desired_caps["autoLaunch"] = False
        self.hs_api_call = hsApi(self.udid, self.access_token)
        self.driver = webdriver.Remote(self.url, self.desired_caps)
        args_lib.device_range_var(self)
        self.wait = WebDriverWait(self.driver, 60)
         
         # Log Desired Capability for debugging
        debug_caps = self.desired_caps
        logger.debug('debug_caps:\n'+json.dumps(debug_caps))
        self.session_id = self.driver.session_id
        self.status = "Fail"
        logger.info(self.session_id)
    def test_search(self):
        self.driver.terminate_app("com.tatadigital.tcp.dev")
        sleep(4)
        self.driver.activate_app("com.tatadigital.tcp.dev")
        self.driver.implicitly_wait(30)
        self.add_to_cart()
    def add_to_cart(self): 
        #launch app
        self.status="Fail_add_to_cart"
        sleep(10)
        self.wait.until( EC.presence_of_element_located((MobileBy.ACCESSIBILITY_ID, 'Not Now'))).click()
        try:
            self.wait.until( EC.presence_of_element_located((MobileBy.ACCESSIBILITY_ID, 'Not Now'))).click()
        except:
            pass
        sleep(5)
        self.wait.until( EC.presence_of_element_located((MobileBy.ACCESSIBILITY_ID, 'crossWhite'))).click()
        sleep(5)
        screen_size = self.driver.get_window_size()
        width = screen_size['width']
        height = screen_size['height']
        swipe_start_x = width/2
        swipe_start_y = height*0.75
        swipe_end_x = width/2
        swipe_end_y = height*0.25
        self.driver.swipe(swipe_start_x, swipe_start_y,swipe_end_x, swipe_end_y,1000)
        sleep(5)
        self.wait.until( EC.presence_of_element_located((MobileBy.ACCESSIBILITY_ID, 'Jewellery'))).click()
        sleep(5)
        self.kpi_labels[kpi_names.JEWELLERY_PAGE_LOAD]['start'] = int(round(time.time() * 1000)) 
        self.wait.until( EC.presence_of_element_located((MobileBy.ACCESSIBILITY_ID, 'Gold'))).click()
        self.kpi_labels[kpi_names.JEWELLERY_PAGE_LOAD]['end'] = int(round(time.time() * 1000)) 
        sleep(5)
        screen_size = self.driver.get_window_size()
        width = screen_size['width']
        height = screen_size['height']
        swipe_start_x = width/2
        swipe_start_y = height*0.5
        swipe_end_x = width/2
        swipe_end_y = height*0.25
        self.driver.swipe(swipe_start_x, swipe_start_y,swipe_end_x, swipe_end_y,1000)
        sleep(5)
        self.wait.until( EC.presence_of_element_located((MobileBy.XPATH, '//XCUIElementTypeStaticText[@name="1 gram 22 Karat Gold Coin with Lakshmi Ganesha Motif"]'))).click()
        sleep(5)
        self.driver.contexts[-1]
        print(self.driver.contexts)
        self.driver.switch_to.context(self.driver.contexts[-1])
        self.driver.find_elements(By.CLASS_NAME, 'primary-btn')[1].click()
        sleep(5)
        self.driver.find_element(By.XPATH,'//*[text()="Proceed to Checkout"]').click()
        sleep(5)
        self.driver.find_element(By.XPATH,'//*[text()="Continue"]').click()
        sleep(5)
        self.driver.find_element(By.XPATH,'//*[text()="Continue"]').click()
        sleep(5)
        self.driver.find_element(By.XPATH,'//*[text()="Continue"]').click()
        self.pass_count += 1
        self.status= 'Pass'
        
    def tearDown(self):
        if self.status != "Pass":
            self.fail_count = self.KPI_COUNT - self.pass_count
            logger.exception("got exception in main handler")
        time.sleep(3)
        self.session_end = int(round(time.time() * 1000))
        
        try:
            self.session_id = self.driver.session_id
        except:
            print((traceback.print_exc()))
        finally:
            self.driver.quit()
        time.sleep(50)

        if self.use_capture:
            session_visual_lib.run_record_session_info(self)

if __name__ == '__main__':
    suite = unittest.TestLoader().loadTestsFromTestCase(TataPoc)
    unittest.TextTestRunner(verbosity=2).run(suite)
