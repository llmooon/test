#!/usr/bin/env python3
# Copyright 2017 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Check that the voiceHAT audio input and output are both working."""


import fileinput
import os
import re
import subprocess
import sys
import tempfile
import textwrap
import traceback

import wave
import base64
import http.client, urllib.request, urllib.parse, urllib.error, base64
import json
import time

import aiy.audio  # noqa
from aiy._drivers._hat import get_aiy_device_name
from aiy.vision.leds import Leds
from aiy.vision.leds import Pattern
from aiy.vision.leds import PrivacyLed
from aiy.vision.leds import RgbLeds



AIY_PROJECTS_DIR = os.path.dirname(os.path.dirname(__file__))

CARDS_PATH = '/proc/asound/cards'
CARDS_ID = {
    "Voice Hat": "googlevoicehat",
    "Voice Bonnet": "aiy-voicebonnet",
}

STOP_DELAY = 1.0

TEST_SOUND_PATH = '/usr/share/sounds/alsa/Front_Center.wav'

RECORD_DURATION_SECONDS = 5

def check_mic_works():
    temp_file, temp_path = tempfile.mkstemp(suffix='.wav')
    print(temp_file,temp_path)
    os.close(temp_file)

    ah = '3fa2f6d6-d7c2-4799-b97c-8b5789f9c898'
    bh = 'df211582-f284-42ef-b676-2a0592b45783'
    ma =  'f07dce9f-0f84-43dd-85e7-592ea4a9d0e0'
    yj =  '4338b960-0de8-413e-b22b-8e3630f8553f'
    
    headers = {
        # Request headers
        #'Content-Type': 'multipart/form-data',
        'Content-type': 'multipart/form-data', 'Sample-Rate':'16000',
        'Ocp-Apim-Subscription-Key': 'b7a5dab14dd54627b39b00a4e0a8d051',
    }
    headers2={
        'Ocp-Apim-Subscription-Key':'b7a5dab14dd54627b39b00a4e0a8d051'
    }

    params = urllib.parse.urlencode({
        # Request parameters
        'shortAudio': 'true',
    })
    

#    try:
    input("When you're ready, press enter and say 'Testing, 1 2 3'...")
    print('Recording...')
    aiy.audio.record_to_wave(temp_path, RECORD_DURATION_SECONDS)

    leds = Leds()
    leds.reset()
    try:
        url='westus.api.cognitive.microsoft.com'
        conn = http.client.HTTPSConnection(url)
        body = open(temp_path,'rb')
        conn.request("POST","/spid/v1.0/identify?identificationProfileIds=3fa2f6d6-d7c2-4799-b97c-8b5789f9c898&%s" % params, body, headers)
        response = conn.getresponse()
        print(response.status)
        #print(response.headers)
        #data = response.read()
        #print(data)
        print(response.headers.get("Operation-Location"))
        conn.close()
        res = 0
        print("=========================identirying...======")
        next_string = response.headers.get("Operation-Location")
        next_url = next_string[len(url)+8:]
        while res==0:
            time.sleep(3)
            conn = http.client.HTTPSConnection(url)
            print(next_string)
        
            conn.request("GET",next_url,"body",headers2)
            response=conn.getresponse()
            print(response.status)
            myres = response.read()
            my_json_res = json.loads(myres.decode())
            print(my_json_res.get("status"))
            api_status = my_json_res.get("status")
            if api_status != "running" and api_status != "notstarted" :
                json_res = my_json_res.get("processingResult")
                owner = json_res.get("identifiedProfileId")
                print(owner)
                print(ah)
                if owner == ah :
                    RED = (0xff, 0x00, 0x00)
                    leds.pattern = Pattern.blink(300)
                    leds.update(Leds.rgb_pattern(RED))
                    aiy.audio.say("hello ah Hyoung")
                    time.sleep(3)
                    leds.reset()
                else :
                    aiy.audio.say("Who Are You?")
                res=1
            conn.close()

    except Exception as e:
         print("[Errno {0}] {1}".format(e.errno, e.strerror))


        #w = wave.open(temp_path,"rb")
        #binary_data = w.readframes(w.getnframes())
        #w.close()
        #b64 = base64.b64encode(binary_data)
        #print(b64)

        #print(binary_data)
        
        #f=open("wavfile.txt",'wb')
        #f.write(b64)

        #f.close()

        #print('Playing back recorded audio...')
        #aiy.audio.play_wave(temp_path)
#    finally:
#        try:
#            os.unlink(temp_path)
#        except FileNotFoundError:
#            pass


def enable_audio_driver():
    print("Enabling audio driver for VoiceKit.")
    configure_driver = os.path.join(AIY_PROJECTS_DIR, 'scripts', 'configure-driver.sh')
    subprocess.check_call(['sudo', configure_driver])


def main():
    if get_aiy_device_name() == 'Voice Hat':
        enable_audio_driver()
    #do_checks()
    check_mic_works()
    #check_speaker_works()


if __name__ == '__main__':
    try:
        main()
        input('Press Enter to close...')
    except Exception:  # pylint: disable=W0703
        traceback.print_exc()
        input('Press Enter to close...')
