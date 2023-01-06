import kpi_names
import label_categories
import time
import os
import json

def init_timing(self):
	# initialising variables
	self.status = "Fail_launch"
	self.pass_count = 0
	self.fail_count = 0
	self.ADD_KPI_ANNOTATION = True
	self.delta_time = 5
	self.connection_status= ""
	self.launched = None
	self.device_range = ""
	self.average_feed_browse_time=0
	# Categories
	self.KPI_LABEL_CATEGORY = label_categories.TATA_NEU

	# KPIs
	self.app_launch_time = None
	self.first_command_end = None

	# KPI Labels
	self.kpi_labels = {} 
	self.kpi_labels[kpi_names.APP_LAUNCH_TIME] = {'start': None, 'end': None}
	self.kpi_labels[kpi_names.JEWELLERY_PAGE_LOAD] = {'start': None, 'end': None}
	
	# Action Labels
	self.session_start = None
	self.appium_timestamps = {}
	self.label_cluster = {}
	self.action_labels = {}

	return self

def pop_dismiss(self, x, y, _sleep):
	t_end = time.time() + _sleep
	while time.time() < t_end:
		if self.running_on_pbox :
			os.system('adb -s {} shell input tap {} {}'.format(self.udid, x, y))
		else:
			self.hs_api_call.run_adb_command("input tap {} {}".format(x, y))
		time.sleep(0.2)
		print(x,y) 
		if self.launched:
			break

def get_screen_size(self):
	# screensize of the device
	screen_size = self.driver.get_window_size()
	self.screen_width = screen_size['width']
	self.screen_height = screen_size['height']
