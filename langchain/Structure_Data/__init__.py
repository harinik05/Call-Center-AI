import os
import azure.functions as func
from form_recognizer_client import AzureFormRecognizerClient  
from translator_client import AzureTranslatorClient  

def main(req: func.HttpRequest) -> func.HttpResponse:
    # Initialize the Form Recognizer client
    form_recognizer_client = AzureFormRecognizerClient()

    # Initialize the Translator client
    translator_client = AzureTranslatorClient()

    # Parse the request to get the URL of the document to analyze
    form_url = req.params.get('formUrl')
    if not form_url:
        return func.HttpResponse("Please provide a 'formUrl' parameter in the request.", status_code=400)

    try:
        # Analyze the document using Form Recognizer
        form_results = form_recognizer_client.analyze_read(form_url)

        # Extracted text from Form Recognizer
        extracted_text = '\n'.join(form_results)

        # Translate the extracted text to a different language (e.g., French)
        translated_text = translator_client.translate(extracted_text, language='fr')

        # Return the translated text in the HTTP response
        return func.HttpResponse(translated_text, status_code=200)

    except Exception as e:
        return func.HttpResponse(f"An error occurred: {str(e)}", status_code=500)

if __name__ == "__main__":
    # For local testing
    req = func.HttpRequest(
        method='GET',
        body=None,
        url='/api/translate?formUrl=<YOUR_FORM_URL>',
        params={'formUrl': '<YOUR_FORM_URL>'},
        headers=None
    )
    response = main(req)
    print(response.get_body())
