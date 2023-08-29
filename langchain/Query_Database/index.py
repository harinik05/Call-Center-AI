import streamlit as st
import os
import traceback
from utilities.helper import LLMHelper

'''
Delete embeddings:
It will search the vector store to delete the key with the embedding
If the data embedding is present in the session state, it will delete the embeddings
in the session state
'''
def delete_embedding():
    llm_helper.vector_store.delete_keys([f"{st.session_state['embedding_to_drop']}"])
    if 'data_embeddings' in st.session_state:
        del st.session_state['data_embeddings'] 

'''
Delete file embeddings
If the data embeddings in the session state is not empty. Determine the file to delete
has any embeddings. Then, choose to delete the embeddings
'''
def delete_file_embeddings():
    if st.session_state['data_embeddings'].shape[0] != 0:
        file_to_delete = st.session_state['file_to_drop']
        embeddings_to_delete = st.session_state['data_embeddings'][st.session_state['data_embeddings']['filename'] == file_to_delete]['key'].tolist()
        embeddings_to_delete = list(map(lambda x: f"{x}", embeddings_to_delete))
        if len(embeddings_to_delete) > 0:
            llm_helper.vector_store.delete_keys(embeddings_to_delete)
            st.session_state['data_embeddings'] = st.session_state['data_embeddings'].drop(st.session_state['data_embeddings'][st.session_state['data_embeddings']['filename'] == file_to_delete].index)

'''
Delete All
Embeddings to delete where the list of embeddings are stated out in the session state. 
'''
def delete_all():
    embeddings_to_delete = st.session_state['data_embeddings'].key.tolist()
    embeddings_to_delete = list(map(lambda x: f"{x}", embeddings_to_delete))
    llm_helper.vector_store.delete_keys(embeddings_to_delete)   



try:

    '''
    state the menu elements and configure the page
    '''
    menu_items = {
	'Get help': None,
	'Report a bug': None,
	'About': '''
	 ## Embeddings App
	 Embedding testing application.
	'''
    }
    st.set_page_config(layout="wide", menu_items=menu_items)

    llm_helper = LLMHelper()

    '''
    get all the documents from redis and put in session state
    '''
    st.session_state['data_embeddings'] = llm_helper.get_all_documents(k=1000)

    nb_embeddings = len(st.session_state['data_embeddings'])
    '''
    if the length is 0, then there are no embeddings
    '''
    if nb_embeddings == 0:
        st.warning("No embeddings found. Go to the 'Add Document' tab to insert your docs.")
    
    
    else:
        '''
        Download embeddings
        '''
        st.dataframe(st.session_state['data_embeddings'], use_container_width=True)
        st.text("")
        st.text("")
        st.download_button("Download data", st.session_state['data_embeddings'].to_csv(index=False).encode('utf-8'), "embeddings.csv", "text/csv", key='download-embeddings')

        st.text("")
        st.text("")
        col1, col2, col3 = st.columns([3,1,3])
        '''
        delete embeddings by id
        '''
        with col1:
            st.selectbox("Embedding id to delete", st.session_state['data_embeddings'].get('key',[]), key="embedding_to_drop")
            st.text("")
            st.button("Delete embedding", on_click=delete_embedding)
        with col2:
            st.text("")

        '''
        delete embeddings for the file 
        '''
        with col3:
            st.selectbox("File name to delete its embeddings", set(st.session_state['data_embeddings'].get('filename',[])), key="file_to_drop")
            st.text("")
            st.button("Delete file embeddings", on_click=delete_file_embeddings)

        st.text("")
        st.text("")
        st.button("Delete all embeddings", type="secondary", on_click=delete_all)
 
except Exception as e:
    st.error(traceback.format_exc())