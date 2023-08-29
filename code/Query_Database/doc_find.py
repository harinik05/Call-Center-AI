import streamlit as st
import os
import traceback
from utilities.helper import LLMHelper
import streamlit.components.v1 as components
from urllib import parse

'''
Function will delete embeddings associated with a specific file from a knowledge base
'''
def delete_embeddings_of_file(file_to_delete):

    '''
    checks if the data files embeddings is in the session_state. if not it will retrieve all of the data
    from the redis database (k = 1000 max)
    '''
    if 'data_files_embeddings' not in st.session_state:
        st.session_state['data_files_embeddings'] = llm_helper.get_all_documents(k=1000)

    '''
    checks if the retrieved data is empty (no embeddings/documents) were there in the knowledgebase
    this uses the first dimension of shape (if 0, then its empty)
    '''
    if st.session_state['data_files_embeddings'].shape[0] == 0:
        return

    '''
    iterates over the list containing a single file extension (.txt)
    '''
    for converted_file_extension in ['.txt']:
        '''
        file to delete contains the details like file path and extension of the file to be deleted from the knowledge base
        '''
        file_to_delete = 'converted/' + file_to_delete + converted_file_extension

        '''
        Extracts a list of keys for embeddings associated with specified file. It filters the data stored in the file based
        on the file name and then extracts the key column 
        '''
        embeddings_to_delete = st.session_state['data_files_embeddings'][st.session_state['data_files_embeddings']['filename'] == file_to_delete]['key'].tolist()
        embeddings_to_delete = list(map(lambda x: f"{x}", embeddings_to_delete))

        '''
        checks if there is embeddings to be deleted. deletes it and updates the session state
        '''
        if len(embeddings_to_delete) > 0:
            llm_helper.vector_store.delete_keys(embeddings_to_delete)
            # remove all embeddings lines for the filename from session state
            st.session_state['data_files_embeddings'] = st.session_state['data_files_embeddings'].drop(st.session_state['data_files_embeddings'][st.session_state['data_files_embeddings']['filename'] == file_to_delete].index)

'''
deletes both the source file, converted file, and associated embeddings
'''
def delete_file_and_embeddings(filename=''):
    '''
    checks if the data_files_embeddings is in the session state. if this is not in the session state, it
    will retrieve from redis (max = 1000 data)
    '''
    if 'data_files_embeddings' not in st.session_state:
        st.session_state['data_files_embeddings'] = llm_helper.get_all_documents(k=1000)

    '''
    Checks the filename and sees if the argument is empty. If it is, then it should add it in session 
    state as a filename to delete
    '''
    if filename == '':
        filename = st.session_state['file_and_embeddings_to_drop'] 
    
    '''
    Line searches for a dictionary in the session state list that matches the filename
    '''
    file_dict = next((d for d in st.session_state['data_files'] if d['filename'] == filename), None)

    '''
    Condition to check if a valid file_dict is found. if file_dict is not empty, then there must be a 
    file with specified filename in the knowledge base
    '''
    if len(file_dict) > 0:
        '''
        initially deletes the source file and uses the blob client to do so
        '''
        source_file = file_dict['filename']
        try:
            llm_helper.blob_client.delete_file(source_file)
        except Exception as e:
            st.error(f"Error deleting file: {source_file} - {e}")

        '''
        if there is a converted file version that exists, it will delete this too
        '''
        if file_dict['converted']:
            converted_file = 'converted/' + file_dict['filename'] + '.txt'
            try:
                llm_helper.blob_client.delete_file(converted_file)
            except Exception as e:
                st.error(f"Error deleting file : {converted_file} - {e}")

        '''
        deletes the embeddings
        '''
        if file_dict['embeddings_added']:
            delete_embeddings_of_file(parse.quote(filename))
    
    '''
    must update the session state with the status of the filenames
    '''
    st.session_state['data_files'] = [d for d in st.session_state['data_files'] if d['filename'] != '{filename}']

'''
Responsible for deleting all the files and their associated embeddings from a knowledge base
'''
def delete_all_files_and_embeddings():
    '''
    contains information about the files present in the knowledge base
    '''
    files_list = st.session_state['data_files']
    '''
    delete the file specified by the dictionary;s filename and embeddings
    '''
    for filename_dict in files_list:
        delete_file_and_embeddings(filename_dict['filename'])

try:
    '''
    style for the page
    '''
    menu_items = {
	'Get help': None,
	'Report a bug': None,
	'About': '''
	 ## Embeddings App

	Document Reader Sample Demo.
	'''
    }

    st.set_page_config(layout="wide", menu_items=menu_items)

    hide_streamlit_style = """
                <style>
                #MainMenu {visibility: hidden;}
                footer {visibility: hidden;}
                </style>
                """
    st.markdown(hide_streamlit_style, unsafe_allow_html=True) 

    llm_helper = LLMHelper()

    '''
    Initializes 
    '''
    st.session_state['data_files'] = llm_helper.blob_client.get_all_files()
    st.session_state['data_files_embeddings'] = llm_helper.get_all_documents(k=1000)

    if len(st.session_state['data_files']) == 0:
        st.warning("No files found. Go to the 'Add Document' tab to insert your docs.")

    else:
        st.dataframe(st.session_state['data_files'], use_container_width=True)

        st.text("")
        st.text("")
        st.text("")

        filenames_list = [d['filename'] for d in st.session_state['data_files']]
        st.selectbox("Select filename to delete", filenames_list, key="file_and_embeddings_to_drop")
         
        st.text("")
        st.button("Delete file and its embeddings", on_click=delete_file_and_embeddings)
        st.text("")
        st.text("")

        if len(st.session_state['data_files']) > 1:
            st.button("Delete all files (with their embeddings)", type="secondary", on_click=delete_all_files_and_embeddings, args=None, kwargs=None)

except Exception as e:
    st.error(traceback.format_exc())