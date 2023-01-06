import sys
from time import sleep
import subprocess
import shlex
import os
# import sh
import requests
import traceback
import json


DEFAULT_TIMEOUT = 60
LONG_TIMOUT = 4 * 60
class hsApi:
    #API for getting all devices and its details present in  an org
    device_list_url = "https://api-dev.headspin.io/v0/devices"
    get_auto_config = "https://api-dev.headspin.io/v0/devices/automation-config"
    url_root = "https://api-dev.headspin.io/v0/"
    #API for getting all devices and its details present in  an org
    def __init__(self, UDID, access_token):
        self.UDID = UDID
        self.access_token = access_token
        self.headers = {'Authorization': 'Bearer {}'.format(self.access_token)}
        #Get the deivce details
        r = requests.get(self.device_list_url, headers=self.headers)
        r = r.json()
        self.devices = r['devices']
        is_desired_device = False
        for device in self.devices:
            self.device_os = device['device_type']
            if self.device_os == "android" and device['serial'] == self.UDID:
                is_desired_device = True
            if self.device_os == "ios" and device['device_id'] == self.UDID:
                is_desired_device = True
            if is_desired_device:
                self.device_details = device
                self.device_hostname = device['hostname']
                #self.device_address = "{}@{}".format(self.UDID, self.device_hostname)			
                self.device_address = self.UDID
                self.device_os = device['device_type']
                break
        
#		current_file_dir = os.path.dirname(os.path.abspath(__file__))
#		setup_folder = os.path.abspath(os.path.join(current_file_dir, '..'))
#		print "Path to set up folder",setup_folder
#		device_details = setup_folder+"/device_details.json"
#
#		with open(device_details, 'w') as f:
#			json.dump(r, f)

#		return devices

    def device_country(self):
        device_country = self.device_details['country']
        return device_country

    def get_automation_config(self):

        capabilities = {}
        r = requests.get(self.get_auto_config, headers={'Authorization': 'Bearer {}'.format(self.access_token)})
        appium_config = r.json()
        self.capabilities = appium_config[self.device_address]["capabilities"]
        return self.capabilities

    def parse_response(self, response):
        try:
            if response.ok:
                # print(response.content)
                try:
                    return response.json()
                except:
                    return response.text
            else:
                print(response.status_code)
                print('something went wrong')
                print(response.text)
        except:
            print(traceback.print_exc())

    def get_capture_timestamp(self, session_id):
        request_url = self.url_root + 'sessions/' + session_id+'/timestamps'
        response = requests.get(request_url, headers=self.headers)
        response.raise_for_status()
        #print self.parse_response(response)
        return self.parse_response(response)

    #Adb devices
    def get_android_device_list(self):
        request_url = "https://api-dev.headspin.io/v0/adb/devices".format(self.UDID)
        r = requests.get(request_url, headers=self.headers)
        data = r.json()
        print(data)
        return data
    
    def add_label(self, session_id, name, category, start_time, end_time, data=None):
        '''
        add annotations to session_id with name, category, start_time, end_time
        '''
        request_url = self.url_root + 'sessions/' + session_id + '/label/add'
        data_payload={}
        data_payload['name']=name
        data_payload['category']=category
        data_payload['start_time']=str(start_time)
        data_payload['end_time']=str(end_time)
        data_payload['data']=data
        data_payload['pinned']=False
        response = requests.post(request_url, headers=self.headers, json=data_payload)
        response.raise_for_status()
        return self.parse_response(response)

    #List of ios devices
    def get_ios_device_list(self):
        request_url = "https://api-dev.headspin.io/v0/idevice/{}/installer/list?json".format(self.UDID)
        r = requests.get(request_url, headers = self.headers)
        data = r.json()
        print(data)
        return data

    def get_pageloadtime_regions(self, session_id, regions):
        request_url = self.url_root + 'sessions/analysis/pageloadtime/'+session_id
        data_payload = {}
        data_payload['regions'] = regions
        response = requests.post(request_url, headers=self.headers, json=data_payload)
        response.raise_for_status()
        results = self.parse_response(response)
        return results

    def delete_label(self, label_id):
        request_url = self.url_root + 'sessions/label/'+label_id
        response = requests.delete(request_url, headers=self.headers)
        response.raise_for_status()

    def delete_session_tag(self,session_id):
        request_url = self.url_root + 'sessions/tags/'+session_id
        response = requests.delete(request_url, headers=self.headers)
        response.raise_for_status()

    def get_pageloadtime(self, session_id, name, start_time, end_time, start_sensitivity=None, end_sensitivity=None):
        request_url = self.url_root + 'sessions/analysis/pageloadtime/'+session_id
        data_payload = {}
        region_times = []
        start_end = {}
        start_end['start_time'] = str(start_time/1000)
        start_end['end_time'] = str(end_time/1000)
        start_end['name'] = name
        region_times.append(start_end)
        data_payload['regions']=region_times
        if(start_sensitivity is not None):
            data_payload['start_sensitivity'] = start_sensitivity
        if(end_sensitivity is not None):
            data_payload['end_sensitivity']=end_sensitivity
        
        response = requests.post(request_url, headers=self.headers, json=data_payload)
        response.raise_for_status()
        results = self.parse_response(response)
        return results

    #Install app
    def install_apk(self, filename):
        data = open(filename, 'rb').read()
        request_url = 'https://api-dev.headspin.io/v0/adb/{}/install'.format(self.UDID)
        response = requests.post(request_url, data=data, headers=self.headers)
        print(response.text)

    #Install app for iOS
    def install_ipa(self, filename):
        data = open(filename, 'rb').read()
        request_url = 'https://api-dev.headspin.io/v0/idevice/{}/installer/install'.format(self.UDID)
        response = requests.post(request_url, data=data, headers=self.headers)
        print(response.text)


    #uninstall app Androd
    def uninstall_app_android(self, package_name):
        request_url = "https://api-dev.headspin.io/v0/adb/{}/uninstall?package={}".format(self.UDID, package_name)
        r = requests.post(url=request_url, headers=self.headers)
        print(r.text)


    #uninstall ios app
    def uninstall_app_ios(self, bundle_id):
        request_url = "https://api-dev.headspin.io/v0/idevice/{}/installer/uninstall?appid={}".format(self.UDID, bundle_id)
        r = requests.post(url=request_url, headers=self.headers)
        print(r.text)


    #adb Commands
    def run_adb_command(self,  commmand_to_run):
        api_endpoint = "https://api-dev.headspin.io/v0/adb/{}/shell".format(self.UDID)
        r = requests.post(url=api_endpoint, data=commmand_to_run, headers=self.headers, timeout=LONG_TIMOUT)
        result = r.json()
        stdout = str(result['stdout'].encode('utf-8').strip())
        return stdout


    #Pull file from android device
    def pull_file_android(self, source, destination):
        api_endpoint = "https://api-dev.headspin.io/v0/adb/{}/pull?remote={}".format(self.UDID, source)
        r = requests.get(url=api_endpoint,  headers=self.headers)
        print("Status code", r.status_code)
        with open(destination, 'wb') as f:
            f.write(r.content)

    #Adb screenshot
    def get_adb_screenshot(self,filename):
        api_endpoint = "https://api-dev.headspin.io/v0/adb/{}/screenshot".format(self.UDID)
        r = requests.get(url = api_endpoint,  headers=self.headers)
        print("Status code",r.status_code)
        with open(filename, 'wb') as f:
            f.write(r.content)

    #iOS screenshot
    def get_ios_screenshot(self,filename):
        api_endpoint = "https://api-dev.headspin.io/v0/idevice/{}/screenshot".format(self.UDID)
        r = requests.get(url = api_endpoint,  headers={'Authorization': 'Bearer {}'.format(self.access_token)})
        print("Status code",r.status_code)
        with open(filename, 'wb') as f:
                f.write(r.content)

    

    #iOS deivice info
    def get_idevice_info(self):
        headers = {
            "Authorization": "Bearer {}".format(self.access_token)
        }

        request_url = "https://api-dev.headspin.io/v0/idevice/{}/info?json".format(self.UDID)
        r = requests.get(request_url, headers=headers)
        data = r.json()
        print(data)
        return data


    #iOS get list of all apps installed
    def get_app_list_ios(self):
        headers = {
            "Authorization": "Bearer {}".format(self.access_token)
        }

        request_url = "https://api-dev.headspin.io/v0/idevice/{}/installer/list?json".format(self.UDID)
        r = requests.get(request_url, headers=headers)
        try:
            data = r.json()
            return data
        except:
            print("Couldnt take the app list")
    #Dismiss pop up ios	
    def dismiss_ios_popup(self):
        api_endpoint = "https://api-dev.headspin.io/v0/idevice/{}/poptap".format(self.UDID)
        r = requests.post(url = api_endpoint,  headers={'Authorization': 'Bearer {}'.format(self.access_token)} )
        result= r.json()
        print(r.text)

            
    #iOS device restart
    def restart_ios_device(self):
        api_endpoint = "https://api-dev.headspin.io/v0/idevice/{}/diagnostics/restart".format(self.UDID)
        r = requests.post(url = api_endpoint,  headers={'Authorization': 'Bearer {}'.format(self.access_token)} )
        result= r.json()
        print(result)

    ##################################### Platform APIs #############################################
    def start_session_capute(self, capture_network = True, capture_video = True):
        api_endpoint = "https://api-dev.headspin.io/v0/sessions"
        pay_load = {"session_type":"capture", "device_address": self.device_address, "capture_video": capture_video, "capture_network": capture_network}
        r = requests.post(url = api_endpoint, data = json.dumps(pay_load), headers={'Authorization': 'Bearer {}'.format(self.access_token)} )
        result = r.json()
        print(r.text)
        session_id = result['session_id']
        return session_id

    def stop_session_capture(self, session_id):

        # curl_comand = sh.Command('curl')
        # curl_comand( '-X','PATCH', 'https://{}@api-dev.headspin.io/v0/sessions/{}'.format(self.access_token, session_id), '-d', '{"active":false}')
        request_url = self.url_root + 'sessions/' + session_id
        data_payload = {}
        data_payload['active'] = False
        response = requests.patch(request_url, headers=self.headers, json=data_payload, timeout=DEFAULT_TIMEOUT)
        return self.parse_response(response)
 
    def add_session_tags(self,session_id, **kwargs):
        # followed by any number of tags , syntax:<tag_key="tag_value">. eg: type1="test_session",type2="test_session"
        ## Function call example:
        ## hs_class.add_session_tags("3da744a6-c269-11e9-b708-0641978974b8",type="test_session")

        api_endpoint = "https://api-dev.headspin.io/v0/sessions/tags/{}".format(session_id)	
        pay_load=[]
        for key,value in kwargs.items():
            pay_load.append({"%s"%key:value})
        r = requests.post(url = api_endpoint, json = pay_load, headers={'Authorization': 'Bearer {}'.format(self.access_token)} )
        print(r)

    #Add data to existing session
    def add_session_data(self, session_data):
        # Expecting the input dictionary as the argument
        # Sample
        # {"session_id": "<session_id>", "test_name": "<test_name>", "data":[{"key":"bundle_id","value":"com.example.android"}] }
        request_url = self.url_root + "perftests/upload"
        response = requests.post(request_url, headers=self.headers, json=session_data, timeout=DEFAULT_TIMEOUT)
        return self.parse_response(response)

        #####Audio APIs
    def prepare_and_inject(self, audio_id_to_inject):

        # defining the api-endpoint
        prepare_api_endpoint= "https://api-dev.headspin.io/v0/audio/prepare"

        #Prepare
        pay_load= {'hostname': self.device_hostname ,  'audio_ids':[audio_id_to_inject] }
        
        # sending post request for prepare
        r= requests.post(url = prepare_api_endpoint, data = json.dumps(pay_load), headers={'Authorization': 'Bearer {}'.format(self.access_token)})
        print(r.text)

        print("Inject")
        inject_api_endpoint= "https://api-dev.headspin.io/v0/audio/inject/start"
        pay_load= {'device_address':self.device_address, 'audio_id':audio_id_for_inject }
        requests.post(url = inject_api_endpoint, data = json.dumps(pay_load), headers={'Authorization': 'Bearer {}'.format(self.access_token)})
        print(r.text)

        #Capture audio
    def capture_audio(self, duration, tag=None):
        api_endpoint= "https://api-dev.headspin.io/v0/audio/capture/start"
        pay_load= {'device_address': self.device_address, 'max_duration':'%s'%duration, 'tag':tag}
        r = requests.post(url = api_endpoint,  data = json.dumps(pay_load),  headers={'Authorization': 'Bearer {}'.format(self.access_token)})
        result= r.json()
        results= json.dumps(result)
        print(results)
        audio_id = result['audio_id']
        print(audio_id)
        return audio_id

    def add_annotation(self, session_id, data_payload):
        request_url = self.url_root + 'sessions/' + session_id + '/label/add'
        response = requests.post(request_url, headers=self.headers, json=data_payload, timeout=DEFAULT_TIMEOUT)
        return self.parse_response(response)

    def get_labels(self, session_id):
        request_url = self.url_root + 'sessions/' + session_id + '/label/list'
        response = requests.get(request_url, headers=self.headers, timeout=DEFAULT_TIMEOUT)
        return self.parse_response(response)


    def get_sessions(self, num_of_sessions=30):
        request_url = self.url_root + 'sessions?include_all=true&num_sessions=' + str(num_of_sessions)
        response = requests.get(request_url, headers=self.headers, timeout=DEFAULT_TIMEOUT)
        return self.parse_response(response)

    def update_session_name_and_description(self, session_id, name, description):
        request_url = self.url_root + 'sessions/' + session_id + '/description'
        data_payload = {}
        data_payload['name'] = name
        data_payload['description'] = description
        print(request_url)
        print(data_payload)
        response = requests.post(request_url, headers=self.headers, json=data_payload, timeout=DEFAULT_TIMEOUT)
        return self.parse_response(response)

    def get_appium_log(self, session_id, working_dir):
        print('get_appium_log')
        request_url = self.url_root + 'sessions/' + session_id + '.appium.log'
        print('request_url', request_url)
        r = requests.get(url=request_url,  headers=self.headers)
        print("Status code", r.status_code)
        if r.ok:
            outfile = os.path.join(working_dir, session_id + '.appium.log')
            with open(outfile, 'wb') as f:
                f.write(r.content)
            return outfile

    def download_captured_audio(self, audio_id_to_download,file_name):        
        cmd= shlex.split("curl -X GET https://{}@api-dev.headspin.io/v0/audio/{}/download?channels=mono -o {}".format(self.access_token,audio_id_to_download, file_name+".wav"))
        print("Downloading")
        print(cmd)
        process = subprocess.Popen(cmd, stdout=subprocess.PIPE)
        print(process.stdout)	



    ######################### Mangae the device state on HS platform

#if __name__ == '__main__':
#
#	{"session_id": "<session_id>", "test_name": "<test_name>", "data":[{"key":"bundle_id","value":"com.example.android"}] }
#	session_id = "6c625eaa-d08a-11e9-b71f-069b78c55cae"
#	test_name= "dummy_test"
#	package = "com.example.android"
#
#	session_data = {"session_id": session_id, "test_name": "dummy_test", "status":"Passed","data":[{"key":"bundle_id","value":package}] }	
#
#	api_call = hsApi("b715ac5e","ff516f1a286541429e156967b179c591")
#	api_call.add_session_data(session_data)


    
