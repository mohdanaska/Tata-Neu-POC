# -*- coding: utf-8 -*-
import json
import traceback
import kpi_names

import datetime
import multiprocessing
from hs_api import hsApi
import pytz
import time
from tzwhere import tzwhere
from hs_logger import logger
from tzlocal import get_localzone
#import pendulum
from alerts import SendAlert

def run_record_session_info(self):
    '''
    Save KPI and Description to session
    '''
    logger.info('run_record_session_info')
    run_add_annotation_data(self)
    run_add_session_data(self)
    logger.info("https://ui-dev.headspin.io/sessions/"+str(self.session_id)+"/waterfall")

def run_add_session_data(self):
    '''
    Save KPI Label info to description 
    '''
    logger.info("run add session data")
    
    session_data = get_general_session_data(self)
    print ("######## \n ", )
    print (session_data)
    if not self.debug:
        result = self.hs_api_call.add_session_data(session_data)
        logger.info('result')
        logger.info(result)
    description_string = ""
    for data in session_data['data']:
        description_string += data['key'] + " : " + str(data['value']) + "\n"

    self.hs_api_call.delete_session_tag(self.session_id)
    
    self.hs_api_call.update_session_name_and_description(self.session_id, self.test_name, description_string)

def get_general_session_data(self):
    '''
    General Session Data, include phone os, phone version ....
    '''
    session_status = None
    if self.status != "Pass":
        session_status = "Failed"
    else:
        session_status = "Passed"

    session_data = {}
    session_data['session_id'] = self.session_id
    session_data['test_name'] = self.test_name
    session_data['status'] = session_status
    session_data['data'] = []
    
    # app info
    session_data['data'].append({"key": kpi_names.BUNDLE_ID, "value": self.package})
    session_data['data'].append({"key": 'status', "value": self.status})

    session_data = add_kpi_data_from_labels(self, session_data)
    
    for kpi_name, label_list in self.label_cluster.items():
        session_data = add_kpi_data_label_cluster(self, kpi_name, label_list, session_data)
    
    if self.average_feed_browse_time !=0:
        session_data['data'].append({"key": kpi_names.AVERAGE_FEED_BROWSE_TIME, "value": self.average_feed_browse_time})
        
    session_data['data'].append({"key": kpi_names.FAIL_REASON, "value": self.status})
    session_data['data'].append({"key": kpi_names.PASS_COUNT, "value": self.pass_count})
    session_data['data'].append({"key": kpi_names.FAIL_COUNT, "value": self.fail_count})

    session_data['data'].append({"key": kpi_names.CONNECTION_STATUS, "value": self.connection_status})

    session_data['data'].append({"key": kpi_names.DEVICE_RANGE, "value": self.device_range})

    # if self.app_size_info:
    #     session_data['data'].append({"key": kpi_names.APP_SIZE_ON_DISK, "value": self.app_size_info['app_size']})
    #     session_data['data'].append({"key": kpi_names.USER_DATA_ON_DISK, "value": self.app_size_info['user_data']})
    #     session_data['data'].append({"key": kpi_names.CACHE_ON_DISK, "value": self.app_size_info['cache']})
    #     session_data['data'].append({"key": kpi_names.TOTAL_ON_DISK, "value": self.app_size_info['total']})
    
    if self.apk_version:
        session_data['data'].append({"key": kpi_names.APP_VERSIONS, "value": self.apk_version})

    if self.debug:
        logger.info('session_data')
        logger.info(json.dumps(session_data, indent=2))
    return session_data

def get_video_start_timestamp(self):
    logger.info('get_video_start_timestamp')
    wait_until_capture_complete = True
    if wait_until_capture_complete:
        while True:
            capture_timestamp = self.hs_api_call.get_capture_timestamp(self.session_id)
            logger.info(capture_timestamp)
            self.video_start_timestamp = capture_timestamp['capture-started'] * 1000
            if 'capture-complete' in capture_timestamp:
                break
            time.sleep(1)
    else:
        capture_timestamp = self.hs_api_call.get_capture_timestamp(self.session_id)
        self.video_start_timestamp = capture_timestamp['capture-started'] * 1000

def run_add_annotation_data(self):   
    '''
    Add annotation from kpi_labels
    '''
    logger.info("run add annotation to session")
    get_video_start_timestamp(self)   
    add_kpi_labels(self, self.kpi_labels, self.KPI_LABEL_CATEGORY)
    
    #Add labels for label_clusters
    for kpi_name, label_list in self.label_cluster.items():
        add_label_cluster_annotation(self, kpi_name, label_list, self.KPI_LABEL_CATEGORY)
    
def add_kpi_data_from_labels(self, session_data):
    '''
    Merge kpi labels and interval time
    '''
    for label_key in self.kpi_labels.keys():
        if self.kpi_labels[label_key] and 'start' in self.kpi_labels[label_key] and 'end' in self.kpi_labels[label_key]:
            data = {}
            data['key'] = label_key
            start_time = self.kpi_labels[label_key]['start']
            end_time = self.kpi_labels[label_key]['end']
            if start_time and end_time:
                data['value'] = end_time - start_time
                session_data['data'].append(data)
    return session_data

def add_kpi_data_label_cluster(self, kpi_name, label_list, session_data):
    '''
    Merge kpi labels and interval time
    '''
    data = {}
    data['value'] = 0
    data['key'] = "average_" + kpi_name
    avg_tot= len(label_list)
    if avg_tot == 8:
    # if avg_tot == 5 or avg_tot == 15:
        for label in label_list:
            start_time = None
            end_time = None
            if 'start' in label.keys() and 'end' in label.keys():
                start_time = label['start']
                end_time = label['end']
                if start_time and end_time:
                    data['value'] = data['value'] + (end_time - start_time)
        data['value'] = round(float(data['value']/avg_tot), 3)
        session_data['data'].append(data)
    return session_data

def get_screenchange_list_divide(self, label_key, label_start_time, label_end_time,
                                 start_sensitivity=None, end_sensitivity=None):
    """
        Given a visual page load of the region
        If there are start and end, there is only 1 region in the middle that might have more screen changes.
        If start and end are the same we are done
    """
    screen_change_list = []
    sn = 0
    sn_limit = 10
    segment_time_step = 100
    try:
        segment_time_step = self.segment_time_step
    except AttributeError:
        pass
    pageload = self.hs_api_call.get_pageloadtime(self.session_id, str(label_key) + str(sn), label_start_time, label_end_time, 
                                                    start_sensitivity=start_sensitivity, end_sensitivity=end_sensitivity)
    logger.debug(pageload)
    if 'page_load_regions' in pageload.keys() and 'message' not in pageload['page_load_regions']:
        while True:
            screen_change_list.append(pageload['page_load_regions'][0]['start_time'])
            screen_change_list.append(pageload['page_load_regions'][0]['end_time'])
            sn += 1
            if sn_limit < sn:
                break
            new_label_start_time = float(pageload['page_load_regions'][0]['start_time']) + segment_time_step
            new_label_end_time = float(pageload['page_load_regions'][0]['end_time']) - segment_time_step
            if new_label_start_time > new_label_end_time:
                break
            logger.debug('new_label_start_time:' + str(new_label_start_time))
            logger.debug('new_label_end_time:' + str(new_label_end_time))
            pageload = self.hs_api_call.get_pageloadtime(self.session_id, str(label_key) + str(sn), new_label_start_time, new_label_end_time, 
                                                            start_sensitivity=start_sensitivity, end_sensitivity=end_sensitivity)
            if 'page_load_regions' not in pageload.keys() or 'error_msg' in pageload['page_load_regions'][0]:
                logger.debug(pageload)
                if 'status' in pageload:
                    # Prevent bad data to get into the database
                    self.status = 'Page Load Error'
                break
    else:
        # Prevent bad data to get into the database
        self.status = 'Page Load Error'
        logger.debug(pageload)

    screen_change_list = sorted(list(set(screen_change_list)))
    logger.info(label_key + str(screen_change_list))
    print(label_key + ' ' + str(screen_change_list))
    return screen_change_list

def add_kpi_labels(self, labels, label_category):
    '''
        Find all the screen change using different increments
        From the screen changes, pick the desired region
        1. Make sure we can produce the regions that we want to work with 100%
        2. Pick the regions in the code to be inserted for labels kpi

        If there is segment_start and segment_end, find all the candidate regions, and use segment_start and segment_end to pick
        segment_start 
        segment_end 
        0 => Pick the first segment from the start
        1 => Pick the second segmenet from the start
        -1 => Pick the last segment from the end
        -2 => Pick the second to last segmene from the end
    '''
    logger.info("add_kpi_labels")
    print(labels)
    for label_key in labels.keys():
        label = labels[label_key]
        logger.debug(label)
        if label['start'] and label['end']:
            label_start_time = label['start'] - self.video_start_timestamp - self.delta_time * 1000
            if(label_start_time < 0):
                label_start_time = 0.0
            label_end_time = label['end'] - self.video_start_timestamp
            # if label_key == kpi_names.DOWNLOAD_TIME:
            #     label_end_time += self.delta_time * 1000
            logger.info("Add Desired Region " + str(label_key)+" "+str(label_start_time)+" "+str(label_end_time))
            self.hs_api_call.add_label(self.session_id, label_key, 'desired region', (label_start_time)/1000, (label_end_time)/1000)

            start_sensitivity = None
            end_sensitivity = None
            if 'start_sensitivity' in label:
                start_sensitivity = label['start_sensitivity']
            if 'end_sensitivity' in label:
                end_sensitivity = label['end_sensitivity']

            new_label_start_time = None
            new_label_end_time = None

            if 'segment_start' in labels[label_key] and 'segment_end' in labels[label_key]:
                # Get candidate screen change list, example [2960, 4360, 8040, 9480, 9960, 11560, 13560, 13800, 17720, 18040]
                screen_change_list = get_screenchange_list_divide(self, label_key, label_start_time, label_end_time, start_sensitivity, end_sensitivity)
                try:
                    if screen_change_list:
                        new_label_start_time = float(screen_change_list[labels[label_key]['segment_start']])
                        new_label_end_time = float(screen_change_list[labels[label_key]['segment_end']])
                except:
                    self.status = 'Page Load Segement Error'
            else:
                if label['start'] and label['end'] : 
                    pageload = self.hs_api_call.get_pageloadtime(self.session_id, label_key, label_start_time, label_end_time, start_sensitivity=start_sensitivity, end_sensitivity=end_sensitivity)
                    if 'page_load_regions' in pageload.keys() and 'error_msg' not in pageload['page_load_regions'][0]:
                        new_label_start_time = float(pageload['page_load_regions'][0]['start_time'])
                        new_label_end_time = float(pageload['page_load_regions'][0]['end_time'])
            if new_label_start_time and new_label_end_time:
                self.kpi_labels[label_key]['start'] = new_label_start_time
                self.kpi_labels[label_key]['end'] = new_label_end_time
                self.hs_api_call.add_label(self.session_id, label_key, label_category, (new_label_start_time)/1000, (new_label_end_time)/1000)
        else:
            logger.debug('Label not found for:' + str(label_key) + ' ' + label_category)

def add_label_cluster_annotation(self, kpi_name, label_list, label_category):
    '''
        Find all the screen change using different increments
        From the screen changes, pick the desired region
        1. Make sure we can produce the regions that we want to work with 100%
        2. Pick the regions in the code to be inserted for labels kpi

        If there is segment_start and segment_end, find all the candidate regions, and use segment_start and segment_end to pick
        segment_start 
        segment_end 
        0 => Pick the first segment from the start
        1 => Pick the second segmenet from the start
        -1 => Pick the last segment from the end
        -2 => Pick the second to last segmene from the end
        
        label_list is an array of dic, each with all parameters needed for annotation like, start, end, sensitivity etc
    '''
    logger.info("add_label_cluster_annotation")
    print(kpi_name)
    
    #Label 
    for label in label_list:
    # for label_key in labels.keys():
        # label = labels[label_key]
        logger.debug(label)
        if label['start'] and label['end']:
            label_start_time = label['start'] - self.video_start_timestamp - self.delta_time * 1000
            if(label_start_time < 0):
                label_start_time = 0.0
            label_end_time = label['end'] - self.video_start_timestamp
            # if kpi_name == kpi_names.DOWNLOAD_TIME:
            #     label_end_time += self.delta_time * 1000
            logger.info("Add Desired Region " + str(kpi_name)+" "+str(label_start_time)+" "+str(label_end_time))
            self.hs_api_call.add_label(self.session_id, kpi_name, 'desired region', (label_start_time)/1000, (label_end_time)/1000)

            start_sensitivity = None
            end_sensitivity = None
            if 'start_sensitivity' in label:
                start_sensitivity = label['start_sensitivity']
            if 'end_sensitivity' in label:
                end_sensitivity = label['end_sensitivity']

            new_label_start_time = None
            new_label_end_time = None

            if 'segment_start' in label.keys() and 'segment_end' in label.keys():
                # Get candidate screen change list, example [2960, 4360, 8040, 9480, 9960, 11560, 13560, 13800, 17720, 18040]
                screen_change_list = get_screenchange_list_divide(self, kpi_name, label_start_time, label_end_time, start_sensitivity, end_sensitivity)
                try:
                    if screen_change_list:
                        new_label_start_time = float(screen_change_list[label['segment_start']])
                        new_label_end_time = float(screen_change_list[label['segment_end']])
                except:
                    self.status = 'Page Load Segement Error'
            else:
                if label['start'] and label['end'] : 
                    pageload = self.hs_api_call.get_pageloadtime(self.session_id, kpi_name, label_start_time, label_end_time, start_sensitivity=start_sensitivity, end_sensitivity=end_sensitivity)
                    if 'page_load_regions' in pageload.keys() and 'error_msg' not in pageload['page_load_regions'][0]:
                        new_label_start_time = float(pageload['page_load_regions'][0]['start_time'])
                        new_label_end_time = float(pageload['page_load_regions'][0]['end_time'])
            if new_label_start_time and new_label_end_time:
                label['start'] = new_label_start_time
                label['end'] = new_label_end_time
                self.hs_api_call.add_label(self.session_id, kpi_name, label_category, (new_label_start_time)/1000, (new_label_end_time)/1000)
        else:
            logger.debug('Label not found for:' + str(kpi_name) + ' ' + label_category)

def check_kpi_value_under_threshold(self,kpi_name,threshold,session_data,email_message):
    for data in session_data['data']:
        if data['key'] == kpi_name:
            value=data['value']
            if value>threshold:
                by_how_much=value-threshold
                email_message+=kpi_name + " KPI crossed the threshold(" + str(threshold) + "ms) value by " + str(by_how_much) + " ms or " + str(by_how_much/1000) + " s. \n"
    return email_message
    # description_string = ""
    # for data in session_data['data']:
    #     description_string += data['key'] + " : " + str(data['value']) + "\n"

def email_message_formation(self,session_data):
    email_message=''
    if session_data['status']=="Passed":
        email_message=check_kpi_value_under_threshold(self,kpi_names.HOME_PAGE_LOAD_TIME,7000,session_data,email_message)
        email_message=check_kpi_value_under_threshold(self,kpi_names.PROFILE_CARD_LOAD_TIME,2000,session_data,email_message)
        email_message=check_kpi_value_under_threshold(self,kpi_names.BESPOKE_PROFILE_LOAD_TIME,4000,session_data,email_message)
        email_message=check_kpi_value_under_threshold(self,kpi_names.WALLET_LOAD_TIME,4000,session_data,email_message)
        email_message=check_kpi_value_under_threshold(self,kpi_names.DEMO_REWARD_LOAD_TIME,2000,session_data,email_message)
        email_message=check_kpi_value_under_threshold(self,kpi_names.QR_CODE_LOAD_TIME,2000,session_data,email_message)

    # elif session_data['status']=="Failed":
    #     email_message=' Run with session id ' + self.session_id + " with test name " + self.test_name + " failed as a result of " + self.status +"\n SESSION lINK: https://ui-dev.headspin.io/sessions/"+self.session_id+"/waterfall \n"
    return email_message

def email_subject_creation(self,session_data,email_message):
    email_subject=''
    if len(email_message)>0:
        # if session_data['status']=="Failed":
        #     email_subject="HKLAND RUN FAILURE ALERT"
        # else:
        email_subject="HKLAND RUN THRESHOLD CROSSED ALERT"
    return email_subject

        
    


