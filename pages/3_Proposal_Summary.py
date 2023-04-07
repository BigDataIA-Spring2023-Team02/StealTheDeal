# Importing necessary modules
import streamlit as st
from main_functions import brief_summary
from main_functions import create_graph, create_donut_chart, evaluate_investability, list_uploaded_file, extract_info, setup_client


# Setting the title and header of the application
st.title('StealTheDeal')
st.header('# Seal the Deal on Your Next Investment')
st.write('')


client, processor_name, credentials = setup_client()

uploaded_files = list_uploaded_file(credentials)

selected_file = st.selectbox("Select an uploaded file", uploaded_files)



if selected_file:
    information, text = extract_info(selected_file, credentials)
    summary = brief_summary(text)
    st.write('Brief Summary about the proposal')
    st.write('')
    st.write(summary)

