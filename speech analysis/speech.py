from dotenv import load_dotenv
from pathlib import Path
env_path = Path('../../../.env') # Change with your .env file
load_dotenv(dotenv_path=env_path,override=True)


import azure.cognitiveservices.speech as speechsdk

import json, os
import string
import time
import wave

import openai
import re
import requests
import sys
from num2words import num2words
import os
import pandas as pd
import numpy as np
from openai.embeddings_utils import get_embedding, cosine_similarity
from transformers import GPT2TokenizerFast

openai.api_type = "azure"
openai.api_key = os.getenv('OPENAI_API_KEY') 
openai.api_base = os.getenv('OPENAI_API_BASE') 
openai.api_version = "2022-06-01-preview"

SPEECH_KEY = os.environ["SPEECH_API_KEY"]

COMPLETIONS_MODEL = os.environ["COMPLETIONS_MODEL"]


def recognize_speech_from_file(filename):
    # Set up the subscription info for the Speech Service:
    # Replace with your own subscription key and service region (e.g., "westus").
    speech_key = SPEECH_KEY
    service_region = "westeurope"

    speech_config = speechsdk.SpeechConfig(subscription=speech_key, region=service_region)
    audio_config = speechsdk.audio.AudioConfig(filename=filename)
    # Creates a speech recognizer using a file as audio input, also specify the speech language
    speech_recognizer = speechsdk.SpeechRecognizer(speech_config=speech_config,  audio_config=audio_config)

    global done 
    done = False
    global recognized_text_list 
    recognized_text_list=[]
    def stop_cb(evt: speechsdk.SessionEventArgs):
        """callback that signals to stop continuous recognition upon receiving an event `evt`"""
        print('CLOSING on {}'.format(evt))
        global done
        done = True

    def recognize_cb(evt: speechsdk.SpeechRecognitionEventArgs):
        """callback for recognizing the recognized text"""
        global recognized_text_list
        recognized_text_list.append(evt.result.text)
        # print('RECOGNIZED: {}'.format(evt.result.text))

    # Connect callbacks to the events fired by the speech recognizer
    # speech_recognizer.recognizing.connect(lambda evt: print('RECOGNIZING: {}'.format(evt)))
    speech_recognizer.recognized.connect(recognize_cb)
    speech_recognizer.session_started.connect(lambda evt: print('STT SESSION STARTED: {}'.format(evt)))
    speech_recognizer.session_stopped.connect(lambda evt: print('STT SESSION STOPPED {}'.format(evt)))
    # speech_recognizer.canceled.connect(lambda evt: print('CANCELED {}'.format(evt)))
    # stop continuous recognition on either session stopped or canceled events
    speech_recognizer.session_stopped.connect(stop_cb)
    # speech_recognizer.canceled.connect(stop_cb)

    # Start continuous speech recognition
    speech_recognizer.start_continuous_recognition()
    while not done:
        time.sleep(.5)

    speech_recognizer.stop_continuous_recognition()

    return recognized_text_list