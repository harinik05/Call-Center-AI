import streamlit as st
import os, json, re, io
from os import path
import requests
import mimetypes
import traceback
import chardet
from utilities.helper import LLMHelper
import uuid
from redis.exceptions import ResponseError 
from urllib import parse

'''
function is triggered when user clicks on the compute embeddings button after entering the text. 
Uploads the text to Azure Blob Storage and adds embeddings to it
'''
def upload_text_and_embeddings():
    file_name = f"{uuid.uuid4()}.txt"
    source_url = llm_helper.blob_client.upload_file(st.session_state['doc_text'], file_name=file_name, content_type='text/plain; charset=utf-8')
    llm_helper.add_embeddings_lc(source_url) 
    st.success("Embeddings added successfully.")

'''
function sends a request to a remote service to convert and add embeddings to files. the service URL is
obtained from the env variable
'''
def remote_convert_files_and_add_embeddings(process_all=False):
    url = os.getenv('CONVERT_ADD_EMBEDDINGS_URL')
    if process_all:
        url = f"{url}?process_all=true"
    try:
        response = requests.post(url)
        if response.status_code == 200:
            st.success(f"{response.text}\nPlease note this is an asynchronous process and may take a few minutes to complete.")
        else:
            st.error(f"Error: {response.text}")
    except Exception as e:
        st.error(traceback.format_exc())

'''
Deletes the document from knowledge base using Redis. Associated with a user interface element
'''
def delete_row():
    st.session_state['data_to_drop'] 
    redisembeddings.delete_document(st.session_state['data_to_drop'])

'''
Processes and adds embeddings to the urls entered by the URLs entered by the user
'''
def add_urls():
    urls = st.session_state['urls'].split('\n')
    for url in urls:
        if url:
            llm_helper.add_embeddings_lc(url)
            st.success(f"Embeddings added successfully for {url}")

'''
uploads a file to blob storage and adds embeddings to it. the content and char encoding are
determined based on the file type
'''
def upload_file(bytes_data: bytes, file_name: str):
    # Upload a new file
    st.session_state['filename'] = file_name
    content_type = mimetypes.MimeTypes().guess_type(file_name)[0]
    charset = f"; charset={chardet.detect(bytes_data)['encoding']}" if content_type == 'text/plain' else ''
    st.session_state['file_url'] = llm_helper.blob_client.upload_file(bytes_data, st.session_state['filename'], content_type=content_type+charset)


try:
    '''
    menu of the add embeddings function 
    '''
    menu_items = {
	'Get help': None,
	'Report a bug': None,
	'About': '''
	 ## Embeddings App
	 Embedding testing application.
	'''
    }

    '''
    set the page configuration
    '''
    st.set_page_config(layout="wide", menu_items=menu_items)

    '''
    created the instance of helper class
    '''
    llm_helper = LLMHelper()

    '''
    Add a single document to the knowledge base
    Allows the users to add a single document to the knowledge base
    1. Users can upload a document (PDF, image or text) using the st.file_uploader widget
    2. If a document is uploaded, it is read as bytes, and its content and encoding are determined
    3. Depending on the file type, different actions are taken:
       a.) For text files (.txt), the text is added to the knowledge base's embeddings
       b.) For the other data types, the document is converted using OCR service like layout API before adding the embeddings
    4. meta data about the document is updated to indicate that it has been converted and embeddings are added
    5. success message displayed once added to the knowledge base

    '''
    with st.expander("Add a single document to the knowledge base", expanded=True):
        st.write("For heavy or long PDF, please use the 'Add documents in batch' option below.")
        st.checkbox("Translate document to English", key="translate")
        uploaded_file = st.file_uploader("Upload a document to add it to the knowledge base", type=['pdf','jpeg','jpg','png', 'txt'])
        if uploaded_file is not None:
            # To read file as bytes:
            bytes_data = uploaded_file.getvalue()

            if st.session_state.get('filename', '') != uploaded_file.name:
                upload_file(bytes_data, uploaded_file.name)
                converted_filename = ''
                if uploaded_file.name.endswith('.txt'):
                    # Add the text to the embeddings
                    llm_helper.add_embeddings_lc(st.session_state['file_url'])

                else:
                    # Get OCR with Layout API and then add embeddigns
                    converted_filename = llm_helper.convert_file_and_add_embeddings(st.session_state['file_url'], st.session_state['filename'], st.session_state['translate'])
                
                llm_helper.blob_client.upsert_blob_metadata(uploaded_file.name, {'converted': 'true', 'embeddings_added': 'true', 'converted_filename': parse.quote(converted_filename)})
                st.success(f"File {uploaded_file.name} embeddings added to the knowledge base.")
            
    '''
    Add text to the knowledge base

    '''
    with st.expander("Add text to the knowledge base", expanded=False):
        '''
        sets up a layout with two columns. the first column takes up 75% of the space and second column takes up 25%
        '''
        col1, col2 = st.columns([3,1])

        '''
        It has something called "compute embeddings" that will allow you to process the text (this is just the UI part)
        '''
        with col1: 
            st.session_state['doc_text'] = st.text_area("Add a new text content and them click on 'Compute Embeddings'", height=600)

        '''
        Allows user to choose from the list of embeddings model before adding to the knowlege base
        '''
        with col2:
            st.session_state['embeddings_model'] = st.selectbox('Embeddings models', [llm_helper.get_embeddings_model()['doc']], disabled=True)
            st.button("Compute Embeddings", on_click=upload_text_and_embeddings)
    
    '''
    Add documents in the batch
    '''
    with st.expander("Add documents in Batch", expanded=False):
        '''
        The user will be able to upload multiple files since accept_multiple_files = True in the given formats
        '''
        uploaded_files = st.file_uploader("Upload a document to add it to the Azure Storage Account", type=['pdf','jpeg','jpg','png', 'txt'], accept_multiple_files=True)

        '''
        This condition checks if at least one file has been uploaded
        '''
        if uploaded_files is not None:
            '''
            For loop will iterate over all the uploaded files. Reads the content of current file and stores it as bytes in the variable
            '''
            for up in uploaded_files:
                bytes_data = up.getvalue()

                '''
                Checks for duplicate file, doesn't move on without processing this
                '''
                if st.session_state.get('filename', '') != up.name:
                    upload_file(bytes_data, up.name)
                    '''
                    Once the file gets uploaded to Azure storage, it will check if its a txt format before uploading 
                    '''
                    if up.name.endswith('.txt'):
                        llm_helper.blob_client.upsert_blob_metadata(up.name, {'converted': "true"})

        col1, col2, col3 = st.columns([2,2,2])
        '''
        col1 = add the files
        col3 = add the files with true arg to indicate all the uploaded files should be processed 
        '''
        with col1:
            st.button("Convert new files and add embeddings", on_click=remote_convert_files_and_add_embeddings)
        with col3:
            st.button("Convert all files and add embeddings", on_click=remote_convert_files_and_add_embeddings, args=(True,))
    
    '''
    Add urls to the knowledge base
    '''
    with st.expander("Add URLs to the knowledge base", expanded=True):
        col1, col2 = st.columns([3,1])
        '''
        this place is for adding the urls
        '''
        with col1: 
            st.session_state['urls'] = st.text_area("Add a URLs and than click on 'Compute Embeddings'", placeholder="PLACE YOUR URLS HERE SEPARATED BY A NEW LINE", height=100)

        '''
        Adds a select box widget and gets the options for embeddings
        '''
        with col2:
            st.selectbox('Embeddings models', [llm_helper.get_embeddings_model()['doc']], disabled=True, key="embeddings_model_url")
            st.button("Compute Embeddings", on_click=add_urls, key="add_url")

    '''
    view documents in the knowledge
    '''
    with st.expander("View documents in the knowledge base", expanded=False):
        '''
        data will retrieve all the documents up to 1000. if there is no embeddings found, it will return nothing. 
        else, it will return the data with the embeddings as a dataframe so that it can be displayed easily
        '''
        try:
            data = llm_helper.get_all_documents(k=1000)
            if len(data) == 0:
                st.warning("No embeddings found. Copy paste your data in the text input and click on 'Compute Embeddings' or drag-and-drop documents.")
            else:
                st.dataframe(data, use_container_width=True)
        except Exception as e:
            if isinstance(e, ResponseError):
                st.warning("No embeddings found. Copy paste your data in the text input and click on 'Compute Embeddings' or drag-and-drop documents.")
            else:
                st.error(traceback.format_exc())


except Exception as e:
    st.error(traceback.format_exc())