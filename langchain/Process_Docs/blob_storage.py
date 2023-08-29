import os
from datetime import datetime, timedelta
from azure.storage.blob import BlobServiceClient, BlobClient, ContainerClient, generate_blob_sas, generate_container_sas, ContentSettings
from dotenv import load_dotenv

class AzureBlobStorageClient:

    '''
    constructor created to initialize the attributes and properties of an instance of class when 
    made
    @input: account name, account key, container name
    All of the input parameters are initialized with value of None, which means that you can 
    create the instance of this class without having to provide these params explicitly
    '''
    def __init__(self, account_name: str = None, account_key: str = None, container_name: str = None):

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
        self.account_name : str = account_name if account_name else os.getenv('BLOB_ACCOUNT_NAME')
        self.account_key : str = account_key if account_key else os.getenv('BLOB_ACCOUNT_KEY')
        self.connect_str : str = f"DefaultEndpointsProtocol=https;AccountName={self.account_name};AccountKey={self.account_key};EndpointSuffix=core.windows.net"
        self.container_name : str = container_name if container_name else os.getenv('BLOB_CONTAINER_NAME')
        self.blob_service_client : BlobServiceClient = BlobServiceClient.from_connection_string(self.connect_str)

    '''
    Function to delete the files 
    @input: file name (name of the file that we want to delete from Azure Blob Storage)
    '''
    def delete_file(self, file_name):
        '''
        Initialize the blob client object (instance of this class)
        retrieves a client for a specific blob by taking the container (where the blob is located)
        and name of the blob we want to delete
        '''
        blob_client = self.blob_service_client.get_blob_client(container=self.container_name, blob=file_name)
        '''
        Deletes the blob based on the initialization done for the blob client 
        '''
        blob_client.delete_blob()


    def upload_file(self, bytes_data, file_name, content_type='application/pdf'):
        # Create a blob client using the local file name as the name for the blob
        blob_client = self.blob_service_client.get_blob_client(container=self.container_name, blob=file_name)
        # Upload the created file
        blob_client.upload_blob(bytes_data, overwrite=True, content_settings=ContentSettings(content_type=content_type))
        # Generate a SAS URL to the blob and return it
        return blob_client.url + '?' + generate_blob_sas(self.account_name, self.container_name, file_name,account_key=self.account_key,  permission="r", expiry=datetime.utcnow() + timedelta(hours=3))

    def get_all_files(self):
        # Get all files in the container from Azure Blob Storage
        container_client = self.blob_service_client.get_container_client(self.container_name)
        blob_list = container_client.list_blobs(include='metadata')
        # sas = generate_blob_sas(account_name, container_name, blob.name,account_key=account_key,  permission="r", expiry=datetime.utcnow() + timedelta(hours=3))
        sas = generate_container_sas(self.account_name, self.container_name,account_key=self.account_key,  permission="r", expiry=datetime.utcnow() + timedelta(hours=3))
        files = []
        converted_files = {}
        for blob in blob_list:
            if not blob.name.startswith('converted/'):
                files.append({
                    "filename" : blob.name,
                    "converted": blob.metadata.get('converted', 'false') == 'true' if blob.metadata else False,
                    "embeddings_added": blob.metadata.get('embeddings_added', 'false') == 'true' if blob.metadata else False,
                    "fullpath": f"https://{self.account_name}.blob.core.windows.net/{self.container_name}/{blob.name}?{sas}",
                    "converted_filename": blob.metadata.get('converted_filename', '') if blob.metadata else '',
                    "converted_path": ""
                    })
            else:
                converted_files[blob.name] = f"https://{self.account_name}.blob.core.windows.net/{self.container_name}/{blob.name}?{sas}"

        for file in files:
            converted_filename = file.pop('converted_filename', '')
            if converted_filename in converted_files:
                file['converted'] = True
                file['converted_path'] = converted_files[converted_filename]
        
        return files

    def upsert_blob_metadata(self, file_name, metadata):
        blob_client = BlobServiceClient.from_connection_string(self.connect_str).get_blob_client(container=self.container_name, blob=file_name)
        # Read metadata from the blob
        blob_metadata = blob_client.get_blob_properties().metadata
        # Update metadata
        blob_metadata.update(metadata)
        # Add metadata to the blob
        blob_client.set_blob_metadata(metadata= blob_metadata)

    def get_container_sas(self):
        # Generate a SAS URL to the container and return it
        return "?" + generate_container_sas(account_name= self.account_name, container_name= self.container_name,account_key=self.account_key,  permission="r", expiry=datetime.utcnow() + timedelta(hours=1))

    def get_blob_sas(self, file_name):
        # Generate a SAS URL to the blob and return it
        return f"https://{self.account_name}.blob.core.windows.net/{self.container_name}/{file_name}" + "?" + generate_blob_sas(account_name= self.account_name, container_name=self.container_name, blob_name= file_name, account_key= self.account_key, permission='r', expiry=datetime.utcnow() + timedelta(hours=1))