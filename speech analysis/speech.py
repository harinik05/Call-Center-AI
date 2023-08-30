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
