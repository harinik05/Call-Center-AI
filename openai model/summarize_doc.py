import streamlit as st
from utilities.helper import LLMHelper
import os
import traceback

'''
summarize the document by waiting for the prompt completion and put the summary
in the response
'''
def summarize():
    response = llm_helper.get_completion(get_prompt())
    st.session_state['summary'] = response

'''
reset the summary
'''
def clear_summary():
    st.session_state['summary'] = ""

'''
get_prompt will take the text that is currently present and provide with one of the following
options
'''
def get_prompt():
    text = st.session_state['text']
    if text is None or text == '':
        text = '{}'
    if summary_type == "Basic Summary":
        prompt = "Summarize the following text:\n\n{}\n\nSummary:".format(text)
    elif summary_type == "Bullet Points":
        prompt = "Summarize the following text into bullet points:\n\n{}\n\nSummary:".format(text)
    elif summary_type == "Explain it to a second grader":
        prompt = "Explain the following text to a second grader:\n\n{}\n\nSummary:".format(text)

    return prompt

try:
    '''
    set the page layout
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
    summarization 
    '''
    st.markdown("## Summarization")
    summary_type = st.radio(
        "Select a type of summarization",
        ["Basic Summary", "Bullet Points", "Explain it to a second grader"],
        key="visibility"
    )
    
    '''
    prompt the user to enter some text that they want summarized
    '''
    st.session_state['text'] = st.text_area(label="Enter some text to summarize",value='A neutron star is the collapsed core of a massive supergiant star, which had a total mass of between 10 and 25 solar masses, possibly more if the star was especially metal-rich.[1] Neutron stars are the smallest and densest stellar objects, excluding black holes and hypothetical white holes, quark stars, and strange stars.[2] Neutron stars have a radius on the order of 10 kilometres (6.2 mi) and a mass of about 1.4 solar masses.[3] They result from the supernova explosion of a massive star, combined with gravitational collapse, that compresses the core past white dwarf star density to that of atomic nuclei.', height=200)
    st.button(label="Summarize", on_click=summarize)

    # if summary doesn't exist in the state, make it an empty string
    summary = ""
    if 'summary' in st.session_state:
        summary = st.session_state['summary']

    '''
    this is used to summarize the result and prompt
    '''
    st.text_area(label="Summary result", value=summary, height=200)
    st.button(label="Clear summary", on_click=clear_summary)

    
    st.text_area(label="Prompt",value=get_prompt(), height=400)
    st.button(label="Summarize with updated prompt")

except Exception as e:
    st.error(traceback.format_exc())