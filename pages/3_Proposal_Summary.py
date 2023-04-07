# Importing necessary modules
import streamlit as st
from main_functions import brief_summary

# Setting the title and header of the application
st.title('StealTheDeal')
st.header('# Seal the Deal on Your Next Investment')
st.write('')

if st.session_state.processed_text is not None:
    # If the user has already entered processed text, we will use it
    processed_text = st.session_state.processed_text
    
    summary = brief_summary(processed_text)
    
    st.write('Brief Summary about the proposal')
    st.write('')
    st.write(summary)

if st.session_state.information is None:
    st.warning('Please see if the file is evaluated successfully !!!')
