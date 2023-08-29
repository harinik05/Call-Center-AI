import streamlit as st
import os
import traceback
from utilities.helper import LLMHelper

'''
get the prompt from the user and combines the text from the document and input 
provided by the user
'''
def get_prompt():
    return f"{st.session_state['doc_text']}\n{st.session_state['input_prompt']}"

'''
processes the prompt and returns the response 
'''   
def customcompletion():
    response = llm_helper.get_completion(get_prompt())
    st.session_state['prompt_result']= response.encode().decode()

'''
this process function will take the input data based on the condition and selects 
rows from the data frame where the filename column is located. 

the vector store will retrieve the data for the filename and save it as csv
'''
def process_all(data):
    llm_helper.vector_store.delete_prompt_results('prompt*')
    data_to_process = data[data.filename.isin(st.session_state['selected_docs'])]
    for doc in data_to_process.to_dict('records'):
        prompt = f"{doc['content']}\n{st.session_state['input_prompt']}\n\n"
        response = llm_helper.get_completion(prompt)
        llm_helper.vector_store.add_prompt_result(doc['key'], response.encode().decode(), doc['filename'], st.session_state['input_prompt'])
    st.session_state['data_processed'] = llm_helper.vector_store.get_prompt_results().to_csv(index=False)

try:
    # Set page layout to wide screen and menu item
    menu_items = {
	'Get help': None,
	'Report a bug': None,
	'About': '''
	 ## Embeddings App
	 Embedding testing application.
	'''
    }
    st.set_page_config(layout="wide", menu_items=menu_items)

    '''
    if the key data processed is present in the dictionary, then it will store the 
    specific variables and maintain state
    '''
    if not 'data_processed' in st.session_state:
        st.session_state['data_processed'] = None

    llm_helper = LLMHelper()

    '''
    obtain all the documents from the database
    '''
    data = llm_helper.get_all_documents(k=1000)

    '''
    length = 0, then no embeddings will be found
    '''
    if len(data) == 0:
        st.warning("No embeddings found. Go to the 'Add Document' tab to insert your docs.")
    
    else:
        '''
        the code proceeds to display them in dataframe using the text areas called
        document, prompt
        '''
        st.dataframe(data, use_container_width=True)
        st.text_area(label="Document", height=400, key="doc_text")
        st.text_area(label="Prompt", height=100, key="input_prompt")
        st.button(label="Execute tasks", on_click=customcompletion)
        
        '''
        if the prompt result is present in the session state, then it will retrieve the 
        result and display it in a text area labeled results
        '''
        result = ""
        if 'prompt_result' in st.session_state:
            result = st.session_state['prompt_result']
            st.text_area(label="Result", value=result, height=400)

        '''
        process docs and download results
        '''
        cols = st.columns([1,1,1,2])
        with cols[1]:
            st.multiselect("Select documents", sorted(set(data.filename.tolist())), key="selected_docs")
        with cols[2]:
            st.text("-")
            st.button("Execute task on docs", on_click=process_all, args=(data,)) 
        with cols[3]:
            st.text("-")
            download_data = st.session_state['data_processed'] if st.session_state['data_processed'] is not None else ""
            st.download_button(label="Download results", data=download_data, file_name="results.csv", mime="text/csv", disabled=st.session_state['data_processed'] is None)

except Exception as e:
    st.error(traceback.format_exc())