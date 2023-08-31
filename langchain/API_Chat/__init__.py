# Import necessary modules
import azure.functions
from dotenv import load_dotenv
import os
from utilities.helper import LLMHelper

# Load environment variables from .env file
load_dotenv()

# Define the entry point for the Azure function
def main(request: azure.functions.HttpRequest) -> str:
    # Validate and parse JSON data from the HTTP request body
    try:
        request_data = request.get_json()
    except ValueError:
        return azure.functions.HttpResponse("Invalid JSON data in the request body", status_code=400)

    # Extract specific information from the JSON data
    question = request_data.get('question')
    history = request_data.get('history', [])
    custom_prompt = request_data.get('custom_prompt', "")
    custom_temperature = float(request_data.get('custom_temperature', os.getenv("OPENAI_TEMPERATURE", 0.7)))

    # Create an instance of the LLMHelper class
    llm_inst = LLMHelper(custom_prompt=custom_prompt, temperature=custom_temperature)

    # Call the LLMHelper method to get semantic answers and related data
    question, response, context, sources = llm_inst.retrieve_semantic_response(question, history)

    # Prepare the response data as a dictionary
    response_data = {
        'question': question,
        'response': response,
        'context': context,
        'sources': sources
    }

    # Return the response data as a JSON string in the HTTP response
    return azure.functions.HttpResponse(str(response_data), mimetype="application/json")
