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

import aiy.audio  # noqa
from aiy._drivers._hat import get_aiy_device_name

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


    
    headers = {
        # Request headers
        #'Content-Type': 'multipart/form-data',
        'Content-type': 'multipart/form-data', 'Sample-Rate':'16000',
        'Ocp-Apim-Subscription-Key': 'ab53cbba29934842bc35323cb33ca3db',
    }

    params = urllib.parse.urlencode({
        # Request parameters
        'shortAudio': 'true',
    })
    

#    try:
    input("When you're ready, press enter and say 'Testing, 1 2 3'...")
    print('Recording...')
    aiy.audio.record_to_wave(temp_path, RECORD_DURATION_SECONDS)

    try:
        conn = http.client.HTTPSConnection('westus.api.cognitive.microsoft.com')
        body = open(temp_path,'rb')
        conn.request("POST", "/spid/v1.0/identificationProfiles/352ece55-6d78-4bf9-a824-47717efabf06/enroll?%s" % params, body, headers)
        response = conn.getresponse()
        print(response)
        data = response.read()
        print(data)
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
