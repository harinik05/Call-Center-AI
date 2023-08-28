'''
chat_app.py: Streamlit application for creating a chat interface that interacts with 
a language model to answer user questions and provide follow-up questions
'''

'''
Imports
1. streamlit as st: streamlit library is used to build the user interface
2. streamlit_chat: This is a custom module for formatting chat messages
3. LLMHelper: custom module for helper functions
4. regex: imports the regex library for regular expression processing
5. os: working with operating system and reading the env variables
6. random: import the randint function for generating random integers
'''
import streamlit as st
from streamlit_chat import message
from utilities.helper import LLMHelper
import regex as re
import os
from random import randint

'''
function to clear the chat history by setting all of the session state 
variable to empty strings or arrays 
'''
def clear_chat_data():
    st.session_state['chat_history'] = []
    st.session_state['chat_source_documents'] = []
    st.session_state['chat_askedquestion'] = ''
    st.session_state['chat_question'] = ''
    st.session_state['chat_followup_questions'] = []
    answer_with_citations = ""

'''
This function is responsible for storing the user's question in the session 
state when a question is asked
It takes in the input question and message key which is saved inside the variable
stored in this function
'''
def questionAsked():
    st.session_state.chat_askedquestion = st.session_state["input"+str(st.session_state ['input_message_key'])]
    st.session_state.chat_question = st.session_state.chat_askedquestion

'''
Asks a follow up question based on the user's answer to the first question
the input message key will be aggregated by 1
'''
def ask_followup_question(followup_question):
    st.session_state.chat_askedquestion = followup_question
    st.session_state['input_message_key'] = st.session_state['input_message_key'] + 1

try :

    '''
    Session state initialization 
    Initializes the session state variables to manage chat history, user questions, 
    source documents, follow-up questions, and input message keys
    '''
    if 'chat_question' not in st.session_state:
            st.session_state['chat_question'] = ''
    if 'chat_askedquestion' not in st.session_state:
        st.session_state.chat_askedquestion = ''
    if 'chat_history' not in st.session_state:
        st.session_state['chat_history'] = []
    if 'chat_source_documents' not in st.session_state:
        st.session_state['chat_source_documents'] = []
    if 'chat_followup_questions' not in st.session_state:
        st.session_state['chat_followup_questions'] = []
    if 'input_message_key' not in st.session_state:
        st.session_state ['input_message_key'] = 1

    '''
    Reads the environment variables relating to the avatar styles and names for the AI
    component and user component of a chat application

    If the env variables are already set, then they are used. Otherwise, the default values 
    provided will be used
    '''
    ai_avatar_style = os.getenv("CHAT_AI_AVATAR_STYLE", "thumbs")
    ai_seed = os.getenv("CHAT_AI_SEED", "Lucy")
    user_avatar_style = os.getenv("CHAT_USER_AVATAR_STYLE", "thumbs")
    user_seed = os.getenv("CHAT_USER_SEED", "Bubba")

    '''
    Created an instance of LLMHelper class
    '''
    llm_helper = LLMHelper()

    '''
    Button to clear chat and input text for typing in the question by the user
    ''' 
    clear_chat = st.button("Clear chat", key="clear_chat", on_click=clear_chat_data)
    input_text = st.text_input("You: ", placeholder="type your question", value=st.session_state.chat_askedquestion, key="input"+str(st.session_state ['input_message_key']), on_change=questionAsked)


    '''
    Once the question is asked by the user, the request is being put to get the result, context, sources, and up to 3 follow-up questions 
    The user will provide their input and once they do:
    Once the user provides the question, it will reset the value for the asked question to an empty string. This means that the chat system has
    processed the question and now is ready for the new one
    Processes the question using the lang_chain function in the helper methods and provides a response with some context and sources (question, result, context, sources)
    Extracts follow-up questions from the result and assigns the modified result and list of questions to result
    Tuple that stores the chat_history by appending the user question and chatbot response
    Appends sources, which is possibly documents or sources of info to generate the information 
    updates a list of followup question extracted from the response
    '''
    # If a question is asked execute the request to get the result, context, sources and up to 3 follow-up questions proposals
    if st.session_state.chat_askedquestion:
        st.session_state['chat_question'] = st.session_state.chat_askedquestion
        st.session_state.chat_askedquestion = ""
        st.session_state['chat_question'], result, context, sources = llm_helper.get_semantic_answer_lang_chain(st.session_state['chat_question'], st.session_state['chat_history'])    
        result, chat_followup_questions_list = llm_helper.extract_followupquestions(result)
        st.session_state['chat_history'].append((st.session_state['chat_question'], result))
        st.session_state['chat_source_documents'].append(sources)
        st.session_state['chat_followup_questions'] = chat_followup_questions_list


    '''
    Displays the chat history
    Iterates through the chat history, displaying the user's questions, answers, source docs and followup questions (displays it)
    The followup questions are displayed as buttons to be clicked to automatically ask the selected question
    '''
    if st.session_state['chat_history']:
        history_range = range(len(st.session_state['chat_history'])-1, -1, -1)
        for i in range(len(st.session_state['chat_history'])-1, -1, -1):

            # This history entry is the latest one - also show follow-up questions, buttons to access source(s) context(s) 
            if i == history_range.start:
                answer_with_citations, sourceList, matchedSourcesList, linkList, filenameList = llm_helper.get_links_filenames(st.session_state['chat_history'][i][1], st.session_state['chat_source_documents'][i])
                st.session_state['chat_history'][i] = st.session_state['chat_history'][i][:1] + (answer_with_citations,)

                answer_with_citations = re.sub(r'\$\^\{(.*?)\}\$', r'(\1)', st.session_state['chat_history'][i][1]).strip() # message() does not get Latex nor html

                # Display proposed follow-up questions which can be clicked on to ask that question automatically
                if len(st.session_state['chat_followup_questions']) > 0:
                    st.markdown('**Proposed follow-up questions:**')
                with st.container():
                    for questionId, followup_question in enumerate(st.session_state['chat_followup_questions']):
                        if followup_question:
                            str_followup_question = re.sub(r"(^|[^\\\\])'", r"\1\\'", followup_question)
                            st.button(str_followup_question, key=randint(1000,99999), on_click=ask_followup_question, args=(followup_question, ))
                    
                for questionId, followup_question in enumerate(st.session_state['chat_followup_questions']):
                    if followup_question:
                        str_followup_question = re.sub(r"(^|[^\\\\])'", r"\1\\'", followup_question)

            answer_with_citations = re.sub(r'\$\^\{(.*?)\}\$', r'(\1)', st.session_state['chat_history'][i][1]) # message() does not get Latex nor html
            message(answer_with_citations ,key=str(i)+'answers', avatar_style=ai_avatar_style, seed=ai_seed)
            st.markdown(f'\n\nSources: {st.session_state["chat_source_documents"][i]}')
            message(st.session_state['chat_history'][i][0], is_user=True, key=str(i)+'user' + '_user', avatar_style=user_avatar_style, seed=user_seed)

except Exception:
    st.error(traceback.format_exc())