# Call-Center-AI
This project represents an advanced AI-driven web application harnessing the capabilities of Microsoft Azure's Machine Learning tools and the OpenAI model. It centers around the utilization of a Large Language Model (LLM) in conjunction with the data supplied. Its primary function is streamlining the management of call center data.The application operates by first ingesting call center data and transforming it into prompts and questions through cognitive services. Subsequently, it employs OpenAI's embedding techniques to query a vector database, seeking relevant information. Once the search is complete, the application returns well-informed responses to the user. In essence, this seamlessly integrates the power of AI and natural language processing to enhance call center data analysis and response generation, significantly improving efficiency and user experience.

![Untitled Diagram drawio-2](https://github.com/harinik05/Call-Center-AI/assets/63025647/b570592c-d954-4ce2-a593-7eee2a156a1a)

## Retrieval-Augmented Generation Approach
Retrieval-Augmented Generation (RAG) is a powerful technique in Natural Language Processing (NLP) that combines elements of both retrieval and generation to create more informative and contextually relevant responses or content. This approach is often used in tasks like question-answering, chatbots, content generation, and recommendation systems. Here's a breakdown of how Retrieval-Augmented Generation works:

1. **Retrieval Phase:** In the retrieval phase, the system looks for relevant information or documents from a large database or corpus. This retrieval can be based on keyword search, semantic similarity, or other retrieval methods. The goal is to find a set of documents or pieces of information that are likely to contain the answer or content needed.

2. **Generation Phase:** Once the relevant documents or information are retrieved, the system generates a response or content based on this retrieved information. This generation can be performed using language models like GPT (Generative Pre-trained Transformer) or other sequence-to-sequence models. The generated content is often more contextually accurate because it's grounded in existing knowledge.

3. **Combining Retrieval and Generation:** The key innovation in Retrieval-Augmented Generation is the synergy between the retrieval and generation phases. Instead of relying solely on generative models, the system leverages retrieved information to inform and enhance the content generation process. This can lead to more informative, context-aware, and accurate responses.

4. **Scoring and Ranking:** In some cases, retrieved documents or information are scored and ranked based on their relevance before being used in the generation phase. This helps ensure that the most relevant information has a stronger influence on the final response.

![Untitled Diagram-Page-2 drawio](https://github.com/harinik05/Call-Center-AI/assets/63025647/414e6821-532c-4f48-9fa6-af1b4561cb3c)

In the depicted illustration, this design pattern is formed by integrating retrieval and generation methods. The data is first stored in the knowledge base and then transferred to the vector database. Subsequently, it is retrieved and employed by the Large Language Model (LLM) to craft the given input. Following this analysis, it is used to produce the response for users.

## Data Ingestion
Azure Blob Storage is a cloud-based object storage service provided by Microsoft Azure. It is designed to store and manage unstructured data such as documents, images, videos, backups, and more. Azure Blob Storage offers a highly scalable, secure, and durable solution for storing large amounts of data in the cloud. There were primarily two types of storage accounts types that were used: container (blobs) and queue (messages). 

### Initialization of Data Ingestion Process
There is a mock client created for Azure Blob Storage, which is initialized with the following information in the constructor: 

| Parameters | Env Var. Value | Variable Name |
| ---------------- | ---------------- |---------------- |
| Account Name  | AZURE_BLOB_ACCOUNT_NAME  |blob_acc_name  |
| Account Key  | AZURE_BLOB_ACCOUNT_NAME  |blob_acc_key  |
| Connection String (URL) |  |blob_connection_url  |
| Container Name  | AZURE_BLOB_CONTAINER_NAME |blob_container_name  |
| Blob Client |   |blob_client  |
| File SAS (Queue) |   |SAS_queue  |


1. **`__init__`**: This is the constructor method for the `AzureBlobStorageClient` class. It initializes the attributes of an instance of the class, including account name, account key, and container name. It also loads environment variables from a .env file.

2. **`upload_file_metadata`**: This method uploads binary data (bytes) to the Azure Blob Storage container. It takes the binary data, file name, and optional content type as inputs. It uses the Azure SDK to upload the data and generates a Shared Access Signature (SAS) URL for the uploaded file.

4. **`obtain_file_information`**: This method retrieves a list of files (blobs) from the Azure Blob Storage container, including metadata about each file. It creates a list of dictionaries containing information about each file, such as filename, conversion status, and URLs for access.

5. **`insert_metadata`**: This method updates or inserts metadata associated with a specific file (blob) in the Azure Blob Storage container. It takes the file name and metadata as inputs and uses the Azure SDK to update the metadata.

6. **`retrieve_sas_container`**: This method generates and returns a Shared Access Signature (SAS) URL for the entire Azure Blob Storage container. It allows read-only access to the container and includes an expiry time.

7. **`retrieve_sas_blob`**: This method generates and returns a Shared Access Signature (SAS) URL for a specific blob (file) in the Azure Blob Storage container. It allows read-only access to the blob and includes an expiry time.

Improved Security Measures: Uploading the file as a binary data instead of actual file content to Blob storage, and using SAS tokens to access the files instead of hardcoding or using environmental variables. 

### File Packaging Process
Block blobs were employed due to the large size of the file (the Apple iPhone manual) and for security considerations. The file was converted into binary data for storage. This functionality was integrated into the `__init.py__` main method as part of Azure Functions. A POST HTTP request is dispatched to upload the file and its metadata content, and a success message is obtained upon successful completion. This design was implemented using the Singleton pattern, employing the `get_instance` class method to eliminate the need for client reinitialization for each operation, thus enhancing efficiency and resource management.
![Untitled Diagram-Page-3 drawio](https://github.com/harinik05/Call-Center-AI/assets/63025647/674fee70-1561-40a3-a68c-3dd3adf787de)

### Processing Chat History Files (Repetitive Data)
The conversation history between the user and OpenAI, likely saved as a text file, requires processing. This involves treating it as a list of documents and preparing it for inclusion in the vector store. The process begins by invoking the `add_embeddings_preprocess` function, responsible for encoding, segmenting, and refining the data before its integration into the vector store. Initially, only the preprocessing phase is activated. Upon completion, a metadata tag, "embeddings_added," is marked as "true," indicating readiness for addition to the store. If the filetype is not .txt, then this will be converted and a new metatag for this will be established. This is how the pre-processing is done with the documents in txt format:

1. **Document Loading**: It seems that documents are initially loaded from a `source_url` using `self.document_loaders(source_url).load()`. This suggests that documents are fetched from some source.

2. **Encoding Conversion**: For each document in the list, there is an attempt to convert its `page_content` to UTF-8 encoding. If the document content can be encoded using both "iso-8859-1" and "latin-1" encodings without error, it is then converted to UTF-8 and any non-UTF-8 characters are ignored (via the `errors="ignore"` parameter). This ensures that the text content is in a consistent and compatible encoding.

3. **Document Splitting**: After encoding conversion, the code uses a `text_splitter` (likely a custom module or function) to split the documents into smaller chunks. It seems that this step is related to text processing.

4. **Non-ASCII Character Removal**: A regular expression (`pattern`) is used to identify and remove specific non-ASCII characters from the content of each document. These characters include control characters, non-breaking spaces, and others.

5. **Key Generation**: For each document, a unique key is generated. This key is based on a combination of the `source_url`, the document index (`i`), and a SHA-1 hash of this combination. The key is likely used for identifying and retrieving the document later.

![Untitled Diagram-Page-4 drawio](https://github.com/harinik05/Call-Center-AI/assets/63025647/a6af7dc4-50f6-4d9c-a19e-1afe3975104e)


## Data Wrangler
Form Recognizer is a Microsoft Azure service designed for extracting structured data from documents. It uses advanced machine learning techniques to analyze various types of documents, such as invoices, receipts, forms, and more. Form Recognizer can automatically identify key fields within these documents, extract information like names, dates, amounts, and other structured data, and then output the results in a structured format. Azure Translator will take any document in the default languages list provided 

| Parameters | Env Var. Value | Variable Name |
| ---------------- | ---------------- |---------------- |
| Pages per Embeddings | AZURE_PAGES_PER_EMBEDDING  |pages_per_embeddings  |
| Section to Exclude  |   |section_to_exclude  |
| Form Recognizer Endpoint |AZURE_FORM_RECOGNIZER_ENDPOINT |form_recognizer_endpoint |
| Form Recognizer Key | AZURE_FORM_RECOGNIZER_KEY |form_recognizer_key  |
| Translate Key | AZURE_TRANSLATE_KEY |translate_key  |
| Translate Region | AZURE_TRANSLATE_REGION |translate_region  |
| Translate Key | AZURE_TRANSLATE_KEY |translate_key  |
| Translate Endpoint | AZURE_TRANSLATE_ENDPOINT |translate_endpoint  |
| API Version | AZURE_API_VERSION |api_version  |

The class `AzureFormRecognizerClient` provides a way to perform document analysis using Azure Form Recognizer, extract content from paragraphs and tables in the document, and organize the content into output files based on specified parameters. 

The Python class (`AzureTranslatorClient`) for language translation using Azure Translator services. It detects the language of input text and, if needed, translates it to the specified target language. It uses Azure credentials and endpoints specified through environment variables or constructor parameters.





