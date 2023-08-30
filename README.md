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

2. **`delete_file`**: This method deletes a file (blob) from the Azure Blob Storage container. It takes the file name as an input and uses the Azure SDK to delete the specified blob.

3. **`upload_file`**: This method uploads binary data (bytes) to the Azure Blob Storage container. It takes the binary data, file name, and optional content type as inputs. It uses the Azure SDK to upload the data and generates a Shared Access Signature (SAS) URL for the uploaded file.

4. **`get_all_files`**: This method retrieves a list of files (blobs) from the Azure Blob Storage container, including metadata about each file. It creates a list of dictionaries containing information about each file, such as filename, conversion status, and URLs for access.

5. **`upsert_blob_metadata`**: This method updates or inserts metadata associated with a specific file (blob) in the Azure Blob Storage container. It takes the file name and metadata as inputs and uses the Azure SDK to update the metadata.

6. **`get_container_sas`**: This method generates and returns a Shared Access Signature (SAS) URL for the entire Azure Blob Storage container. It allows read-only access to the container and includes an expiry time.

7. **`get_blob_sas`**: This method generates and returns a Shared Access Signature (SAS) URL for a specific blob (file) in the Azure Blob Storage container. It allows read-only access to the blob and includes an expiry time.

Improved Security Measures: Uploading the file as a binary data instead of actual file content to Blob storage, and 







