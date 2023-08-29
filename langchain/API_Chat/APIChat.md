# API Chat Instructions

## Purpose
Triggered by Azure Functions (HTTP Request) by receiving a POST request containing JSON data, parses this data, and processes this using LLMHelper (Large Language Model) class.This function returns a HTTP response containing all the information mapped in a dictionary. 

## Dependencies Required 
* azure.functions: Module for creating Azure functions 
```
pip install azure-functions
```

* load_dotenv: Used to load env variables from .env file 
```
pip install python-dotenv
```

* os: Used to access the env variables. Built-in module in py (no installation required)

* LLMHelper: Creates helper functions related to language model (possibly GPT-3 or similar model)
```
pip install llm-helper
```
Inside the utilities folder, there's a `helper.py` file created that contains the function `get_semantic_answer_lang_chain` to return the tuple needed to process the data. 

## Overview of `function.json`
`function.json` is a configuration file used in Azure Functions for serverless functions. It specifies various settings such as function's input and output bindings, authentication level, and trigger type. Here's an overview of this file:
1. `"scriptFile": "__init__.py"`: Specifies the name of script name that contains the code for Azure Functions
2. `"bindings" `: Array that defines the input and output bindings that explicitly uses HTTP Trigger Binding
3. `"authLevel": "anonymous"`: Specifies that a function can be triggered without requiring authentication. Anyone should be able to make POST request to trigger the function
4. `"type": "httpTrigger" `: Indicates that binding is an HTTP trigger
5. `"direction": "in"`: Input binding as its receiving data from HTTP request
6. `"name": "input_func"`: Assigns input_func to the binding (used in functions main method)
7. `"methods": ["post"]`: Specifies that the function should only be triggered when a HTTP POST request is made
8. `"type": "http" `: Binding is a HTTP output binding type 
9. `"direction": "out"`: Indicates that its an output binding
10. `"name": "$return"`: Specifies the name of variable used in main method to represent the HTTP response that will be returned 

In conclusion, it defines the set of configuration for an Azure function to be triggered via POST HTTP request with no authentication required. It expects a HTTP request object named `input_func` as input and uses the HTTP response object `$return` to send the response back to the client. 


## Code Walkthrough of `__init__.py`
`__init__.py` file has a main method powered by Azure Functions to take in HTTP request as input and returns the output as a string via HTTP response. It takes in bodyJSON if a valid JSON body exists and extracts the essential information from it:
1. Question field
2. History field (List Type)
3. Custom Prompt
4. Custom Temperature 

`custom_temperature_in` is a hyperparameter that is tuned for randomness of generated text. Low temperature (0-0.5) is an indicator of more deterministic or focused data. When creating models for prediction, this setting is good for repetitive responses. In the case of our model, the default was 0.7, which is moderate temperature, which is good for generating responses when there is a diversified dataset. 

`LLMHelper` function was used to facilitate the generation of a tuple with all the information and response, which was mapped to their corresponding keys in the dictionary. This is returned as a HTTP response with `mimetype` as JSON since this is a parsed JSON type that is being returned as a string. 