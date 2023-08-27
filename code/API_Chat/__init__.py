###########################################
# __init__.py

# Triggered by Azure Functions (HTTP Request) by receiving
# a POST request containing JSON data, parses this dats
# and processes this using LLMHelper (Large Language Model) class. 
# This function returns a HTTP response containing all the 
# information mapped in a dictionary. 
###########################################

'''
Import the necessary modules for __init__ file

azure.functions: Module for creating Azure functions 
load_dotenv: Used to load env variables from .env file 
os: Used to access the env variables
LLMHelper: Creates helper functions related to language 
model (possibly GPT-3 or similar model)
'''
import azure.functions
from dotenv import load_dotenv

'''
Loads env variables from .env file which can store secrets
and configs
'''
load_dotenv()

import os
from utilities.helper import LLMHelper

'''
Defines the entry point for the azure function by taking:
@input: azure.functions.HttpRequest
@output: string
'''
def main(input_func: azure.functions.HttpRequest) -> str:
    '''
    Validates and parses the JSON data from the HTTP request 
    body
    '''
    try:
        body_JSON = input_func.get_json()
    except ValueError:
        return azure.functions.HttpResponse("Invalid JSON data in the request body ", status_code = 400)

    else:
        '''
        After storing the body_JSON as JSON data, it extracts specific info:
        1. Question field 
        2. History field (empty list if not found)
        3. Custom prompt (empty string if not found)
        4. Custom temperature (floating num from JSON or default val from env variable)
        '''
        question_in = body_JSON.get('question')
        history_in = body_JSON.get('history', [])
        custom_prompt_in = body_JSON.get('custom_prompt', "")
        custom_temperature_in = float(body_JSON.get('custom_temperature', os.getenv("OPENAI_TEMPERATURE", 0.7)))

        '''
        Here is an example of how to provide these inputs 
        1. Question - "What is the capital of France?"
        2. History - ["What is the weather today?", "It's sunny."]
        3. custom_prompt - "Translate "hello" to French"
        4. temperature - hyperparam
        '''
    
    '''
    Instance of LLMHelper class by passing custom_prompt and temperature values
    as arguments
    custom_prompt_in = given 
    custom_temperature_in = hyperparameter that affects the randomness of generated
    text. Low temperature means that the data is more deterministic or focused (repetitive
    responses). 0.7 is default and its moderate so its good for generating diverse but 
    coherent responses
    '''
    llm_helper_obj = LLMHelper(custom_prompt=custom_prompt_in, temperature=custom_temperature_in)
    
    '''
    data is a dictionary wherin the LLMHelper method "get_semantic_answer_lang_chain"
    assigns the value corresponding to the keys (question, response, context, sources)
    @input: question, history
    @output: tuple containing question, response, context sources
    '''
    output_data = {}
    output_data['question'], output_data['response'], output_data['context'], output_data["sources"] = llm_helper_obj.get_semantic_answer_lang_chain(question_in, history_in)

    '''
    Returns the JSON string of dictionary as HTTP response 
    '''
    return azure.functions.HttpResponse(str(output_data), mimetype = "application/json")