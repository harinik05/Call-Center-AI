import os
from datetime import datetime, timedelta
from azure.storage.blob import BlobServiceClient, generate_blob_sas, generate_container_sas, ContentSettings
from dotenv import load_dotenv

class AzureBlobStorage:

    # Singleton instance
    _instance = None

    @classmethod
    def get_instance(cls, blob_acc_name=None, blob_acc_key=None, container_name=None):
        if cls._instance is None:
            cls._instance = cls(blob_acc_name, blob_acc_key, container_name)
        return cls._instance

    '''
    constructor created to initialize the attributes and properties of an instance of class when 
    made
    @input: account name, account key, container name
    All of the input parameters are initialized with value of None, which means that you can 
    create the instance of this class without having to provide these params explicitly
    '''
    def __init__(self):

        '''
        Loads the env variables from .env file into an applications environment. Common for 
        maintaining sensitive information like account names and keys
        '''
        load_dotenv()

        '''
        if its provided as an argument, it will assign the value for the variable using that. 
        If not, then it will look in the env variables to check for this variable
        1. account name
        2. account key
        3. container name
        4. formatted value of connected string for Azure Blob Storage
            -> derived from account name and account key
        5. service client - creates a client for interacting with Azure Blob storage 
        '''
        self.blob_acc_name = os.getenv('BLOB_ACCOUNT_NAME')
        self.blob_acc_key = os.getenv('BLOB_ACCOUNT_KEY')
        self.container_name = os.getenv('BLOB_CONTAINER_NAME')
        self.blob_connection_url = f"DefaultEndpointsProtocol=https;AccountName={self.blob_acc_name};AccountKey={self.blob_acc_key};EndpointSuffix=core.windows.net"
        self.blob_service_client = BlobServiceClient.from_connection_string(self.blob_connection_url)
        self.azure_blob_client = AzureBlobStorage.get_instance()

    '''
    this function is responsible for retrieving a list of files (blobs) from the Azure Blob Storage
    container, gathering metadata about these files (blobs) form the Azure Blob Storage, and 
    creating a list of dictionaries containing information about each file
    '''
    def obtain_file_information(self):
        '''
        this will be able to fetch the list of blobs within the specified container using the 
        list blobs method from the container client
        '''
        blob_list = self.blob_service_client.get_container_client(self.container_name).list_blobs(include='metadata')

        '''
        Generates a SAS token for the container. This token allows read-only access (permission = "R) and
        this is set to expire three hours from the current UTC time
        '''
        sas_token = self.retrieve_sas_container()

        '''
        initializes two empty lists to collect information about the files and their 
        conversion status
        '''
        files_list = []

        # Iterate through each blob in the blob list
        for blob in blob_list:
            # Check if the blob doesn't start with 'converted/'
            if not blob.name.startswith('converted/'):
                # Create a dictionary with file information
                '''
                    a dictionary is created with the following information;
                    1. filename: name of the blob
                    2. converted: boolean indicating if the blob is marked as converted (based on the metadata)
                    3. embeddings added: boolean indicating if embeddings have been added (based on metadata)
                    4. full path: URL that includes the SAS token for accessing the blob
                    5. converted file name: name of the converted version fo the file (if its available in metadata)
                    6. conveted path: initially empty string
                '''
                file_info = {
                    "filename": blob.name,
                    "converted": blob.metadata.get('converted', 'false') == 'true' if blob.metadata else False,
                    "embeddings_added": blob.metadata.get('embeddings_added', 'false') == 'true' if blob.metadata else False,
                    "fullpath": f"{blob.client.primary_endpoint}/{self.container_name}/{blob.name}?{sas_token}",
                    "converted_filename": blob.metadata.get('converted_filename', '') if blob.metadata else '',
                    "converted_path": ""
                }
                files_list.append(file_info)

        # Return the list of file information
        return files_list
    
   
    '''
    function will upload the binary data (bytes) to Azure Blob Storage container and 
    returns a SAS (Shared Access Signature) URL for the uploaded file
    @input: bytes data (binary data that needs to be uploaded to Blob), file name (given to the file
    we're uploading), convert type (default value is pdf) 
    '''
    def upload_file_metadata(self, bytes_data, file_name, content_type='application/pdf'):
        '''
        The upload_blob function in the blob client will upload the object with bytes data
        to the specific blob
        It also takes care of any duplicates that exist by overwriting it
        '''
        self.azure_blob_client.upload_blob(bytes_data, overwrite=True, content_settings=ContentSettings(content_type=content_type))
        
        '''
        the output of this function will be the url of the uploaded blob
        ? is used to seperate the base URL from the SAS token 
        SAS url can be used to provide temporary access to the uploaded file
        '''
        partOfURL = self.retrieve_sas_blob(self.blob_acc_name, self.container_name, file_name,account_key=self.blob_acc_key,  permission="r", expiry=datetime.utcnow() + timedelta(hours=24))
        return self.azure_blob_client.url + '?' + partOfURL


    '''
    update and insert metadata associated with a specific file (blob) in an Azure Blob 
    Container
    @input: metadata
    '''
    def insert_metadata(self, metadata):
        
        '''
        retrieves the existing metadata associated with the blob
        '''
        blob_metadata = self.azure_blob_client.get_blob_properties().metadata

        '''
        adds or updates the key-value pairs from the metadata dictionary
        If the key already exists in the blob's metadata, the value is updated
        with the new value from the metadata dictionary 
        If the key doesn't exist, it is added to the metadata
        '''
        blob_metadata.update(metadata)
        
        '''
        sets the metadata accordingly
        '''
        self.azure_blob_client.set_blob_metadata(metadata= blob_metadata)

    '''
    generates the shared access signature URL for the Azure Blob Storage container and returns it
    '''
    def retrieve_sas_container(self):
        '''
        Generates a SAS token for the Azure bLOB STORAGE CONTAINER and indicated using the ? to show
        that this is the standard way to start the query of a string in the URL
        '''
        return "?" + generate_container_sas(account_name= self.blob_acc_name, container_name= self.container_name,account_key=self.blob_acc_key,  permission="r", expiry=datetime.utcnow() + timedelta(hours=1))
    '''
    this is the same as the last function (its for the sas of the blob)
    '''
    def retrieve_sas_blob(self, file_name):
        return f"https://{self.blob_acc_name}.blob.core.windows.net/{self.container_name}/{file_name}" + "?" + generate_blob_sas(account_name= self.blob_acc_name, container_name=self.container_name, blob_name= file_name, account_key= self.blob_acc_key, permission='r', expiry=datetime.utcnow() + timedelta(hours=1))