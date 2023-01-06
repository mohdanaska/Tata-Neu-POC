
from appium.webdriver.common.touch_action import TouchAction
# https://developer.android.com/reference/android/view/KeyEvent#KEYCODE_ENTER
ANDROID_KEYCODE_ENTER = 66
ANDROID_KEYCODE_SEARCH = 84
import time
import traceback
try:
    from appium.webdriver.extensions.android.nativekey import AndroidKey
    ANDROID_KEYCODE_ENTER = AndroidKey.ENTER
except:
    print('running py2')

from hs_logger import logger
class HeadSpinAndroidAction:
    def __init__(self, testCase, driver):
        self.testCase = testCase
        self.driver = driver
        # get_screen_size will make an call
        self.get_screen_size()
        '''
        try:
            if self.clear_cache:
                self.clear_cache()
        except AttributeError:
            logger.info(traceback.print_exc())
            pass
        '''
    def find_element_by_label(self, label, match=False):
        uiStr= 'new UiSelector().'
        if(match==True):
            uiStr = uiStr+'textMatches'
        else:
            uiStr = uiStr+'textContains'
        
        uiStr = uiStr+'("'+label+'")'

        try:
            el = self.driver.find_element_by_android_uiautomator(uiStr)
        except:
            el = None
        finally:
            return el

    def find_elements_by_label(self, label, match=False):
        uiStr= 'new UiSelector().'
        if(match==True):
            uiStr = uiStr+'textMatches'
        else:
            uiStr = uiStr+'textContains'
        
        uiStr = uiStr+'("'+label+'")'

        try:
            el = self.driver.find_elements_by_android_uiautomator(uiStr)
        except:
            el = None
        finally:
            return el

    def click_element_by_label(self, label, match=False):
        ele = self.find_element_by_label(label, match)
        ele.click()

    def short_click(self, start_x, start_y):
        action = TouchAction(self.driver)
        action \
            .press(x=start_x, y=start_y) \
            .release()
        action.perform()
        return self

    def press_android_key_enter(self):
        logger.debug('press_android_key_enter:' + str(ANDROID_KEYCODE_ENTER))
        self.driver.press_keycode(ANDROID_KEYCODE_ENTER)

    def press_android_key_search(self):
        logger.debug('press_android_key_search:' + str(ANDROID_KEYCODE_SEARCH))
        self.driver.press_keycode(ANDROID_KEYCODE_SEARCH)

    def wait_enabled_until_click(self, btn, timeout=5):
        logger.debug("wait_enabled_until_click")
        wait_start = int(round(time.time() * 1000))
        while int(round(time.time() * 1000)) < wait_start + timeout * 1000:
            if btn.is_enabled():
                logger.debug("btn ready to click")
                break
            logger.info("btn not enabled again checking again")
        btn.click()

    def swipe_up_until_element(self, find_function, timeout=5):
        wait_start = int(round(time.time() * 1000))
        while int(round(time.time() * 1000)) < wait_start + timeout * 1000:
            try:
                self.swipe_up()
                el = find_function(self)
                return el
            except:
                logger.debug("find_function failed retry")
                logger.info(traceback.print_exc())
        raise Exception('element not found' + str(find_function))

    def swipe_up(self, duration=None):
        swipe_start_x = self.half_width
        swipe_end_x = self.half_width
        swipe_start_y = self.half_height
        swipe_end_y = self.top_quarter_height
        if duration:
            self.driver.swipe(swipe_start_x, swipe_start_y, swipe_end_x, swipe_end_y, duration)
        else:
            self.driver.swipe(swipe_start_x, swipe_start_y, swipe_end_x, swipe_end_y)

    def get_screen_size(self):
        # screensize of the device
        screen_size = self.driver.get_window_size()
        self.width = screen_size['width']
        self.height = screen_size['height']
        self.half_width = self.width/2
        self.half_height = self.height/2
        self.top_quarter_height = self.height/4
    
    def find_element_by_description(self, label):
        uiStr = 'new UiSelector().'
        uiStr = uiStr+'description'        
        uiStr = uiStr+'("'+label+'")'       
        
        try:
            el = self.driver.find_element_by_android_uiautomator(uiStr)
        except:
            el = None
        finally:
            return el

    def long_click(self, start_x, start_y, click_time):
        '''
        long time click
        '''
        logger.info("long click:"+str(start_x)+" "+str(start_y))
        action = TouchAction(self.driver)
        action \
            .press(x=start_x, y=start_y) \
            .wait(ms=click_time*1000) \
            .release()
        action.perform()
        return self


    def clear_cache(self):
        logger.debug('clear_cache started')
        #Clear cache
        self.testCase.device_info.clear_app_cache(self.driver, self.testCase.app_name)
        logger.info("Cache cleared")

        #Kill app from background
        self.driver.terminate_app(self.testCase.package)
        time.sleep(3)
        logger.debug('clear_cache completed')

    def get_element_rect(self, element):
        logger.info("get element rect")
        rect = {}
        rect['x'] = element.location['x']
        rect['y'] = element.location['y']
        rect['width'] = element.size['width']
        rect['height'] = element.size['height']
        return rect
        