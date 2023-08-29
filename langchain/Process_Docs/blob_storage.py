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


    '''
    function will upload the binary data (bytes) to Azure Blob Storage container and 
    returns a SAS (Shared Access Signature) URL for the uploaded file
    @input: bytes data (binary data that needs to be uploaded to Blob), file name (given to the file
    we're uploading), convert type (default value is pdf) 
    '''
    def upload_file(self, bytes_data, file_name, content_type='application/pdf'):
        '''
        initialize the blob_client to be used which will take in the container and file name (file that we're uploading)
        '''
        blob_client = self.blob_service_client.get_blob_client(container=self.container_name, blob=file_name)
        
        '''
        The upload_blob function in the blob client will upload the object with bytes data
        to the specific blob
        It also takes care of any duplicates that exist by overwriting it
        '''
        blob_client.upload_blob(bytes_data, overwrite=True, content_settings=ContentSettings(content_type=content_type))
        
        '''
        the output of this function will be the url of the uploaded blob
        ? is used to seperate the base URL from the SAS token 
        SAS url can be used to provide temporary access to the uploaded file
        '''
        return blob_client.url + '?' + generate_blob_sas(self.account_name, self.container_name, file_name,account_key=self.account_key,  permission="r", expiry=datetime.utcnow() + timedelta(hours=3))

    '''
    this function is responsible for retrieving a list of files (blobs) from the Azure Blob Storage
    container, gathering metadata about these files (blobs) form the Azure Blob Storage, and 
    creating a list of dictionaries containing information about each file
    '''
    def get_all_files(self):
        '''
        initializes the client object using the get client method of blob service client 
        attribute with the specific container in the Azure blob storage
        '''
        container_client = self.blob_service_client.get_container_client(self.container_name)

        '''
        this will be able to fetch the list of blobs within the specified container using the 
        list blobs method from the container client
        '''
        blob_list = container_client.list_blobs(include='metadata')
        
        '''
        Generates a SAS token for the container. This token allows read-only access (permission = "R) and
        this is set to expire three hours from the current UTC time
        '''
        sas = generate_container_sas(self.account_name, self.container_name,account_key=self.account_key,  permission="r", expiry=datetime.utcnow() + timedelta(hours=3))
        
        '''
        initializes two empty lists to collect information about the files and their 
        conversion status
        '''
        files = []
        converted_files = {}

        '''
        this loop iterates through each blob in the blob list 
        '''
        for blob in blob_list:
            '''
            this condition checks that the blob doesn't start with converted
            '''
            if not blob.name.startswith('converted/'):
                '''
                a dictionary is created with the following information;
                1. filename: name of the blob
                2. converted: boolean indicating if the blob is marked as converted (based on the metadata)
                3. embeddings added: boolean indicating if embeddings have been added (based on metadata)
                4. full path: URL that includes the SAS token for accessing the blob
                5. converted file name: name of the converted version fo the file (if its available in metadata)
                6. conveted path: initially empty string
                '''
                files.append({
                    "filename" : blob.name,
                    "converted": blob.metadata.get('converted', 'false') == 'true' if blob.metadata else False,
                    "embeddings_added": blob.metadata.get('embeddings_added', 'false') == 'true' if blob.metadata else False,
                    "fullpath": f"https://{self.account_name}.blob.core.windows.net/{self.container_name}/{blob.name}?{sas}",
                    "converted_filename": blob.metadata.get('converted_filename', '') if blob.metadata else '',
                    "converted_path": ""
                    })
            else:
                '''
                for the files that are already converted it will add them to the converted files dictionary
                '''
                converted_files[blob.name] = f"https://{self.account_name}.blob.core.windows.net/{self.container_name}/{blob.name}?{sas}"

        '''
        after collecting the informatino about the files, it iterates through the files list
        '''
        for file in files:
            '''
            it checks if the converted file exist in the dictionary. if yes, it marks the metadata
            with a true tag and puts the path name corresponding to the url
            '''
            converted_filename = file.pop('converted_filename', '')
            if converted_filename in converted_files:
                file['converted'] = True
                file['converted_path'] = converted_files[converted_filename]

        '''
        it will return all the files and its information 
        ''' 
        return files


    '''
    update and insert metadata associated with a specific file (blob) in an Azure Blob 
    Container
    @input: file name, metadata
    '''
    def upsert_blob_metadata(self, file_name, metadata):
        '''
        
        '''
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