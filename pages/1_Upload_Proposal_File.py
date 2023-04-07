# Importing necessary modules
import mimetypes
import streamlit as st
from main_functions import extract_info, setup_client, process_file

# Setting the title and header of the application
st.title('StealTheDeal')
st.header('# Seal the Deal on Your Next Investment')
st.write('')
st.subheader('Upload your investment proposal and get an evaluation of its viability.')
st.write('')

if 'uploaded_file' not in st.session_state:
    st.session_state.uploaded_file = ''
    st.session_state.client = ''
    st.session_state.processor_name = ''
    st.session_state.credentials = ''
    st.session_state.information = ''
    st.session_state.processed_text = ''

# Creating a file uploader widget that allows users to upload only certain file types
uploaded_file = st.file_uploader("Choose a file", type=["pdf", "tif", "tiff", "png", "jpg", "jpeg"])
st.session_state.uploaded_file = uploaded_file

if st.session_state.uploaded_file is not None:
    
    # When the "Evaluate" button is clicked, process the file and display the text
    if st.button("Evaluate"):
        
        # Setting up the client
        client, processor_name, credentials = setup_client()
        st.session_state.client = client
        st.session_state.processor_name = processor_name
        st.session_state.credentials = credentials

        if uploaded_file is not None:
            
            # Determine the mime type of the uploaded file
            mime_type = mimetypes.guess_type(uploaded_file.name)[0]
            
            # Check if the mime type is supported
            if mime_type not in ['application/pdf', 'image/tiff', 'image/png', 'image/jpeg']:
                st.warning("Please upload a supported file type (PDF, TIFF, PNG, JPG).")
            
            else:
                # If the file type is supported, process the file
                processed_text = process_file(mime_type, client, processor_name, uploaded_file, credentials)
                st.session_state.processed_text = processed_text

                information = extract_info(processed_text)
                st.session_state.information = information
                st.success("Your proposal has been evaluated.")
        else:
            # If no file is uploaded, display an error message
            st.error("No file uploaded.")
            st.experimental_rerun()

if st.session_state.uploaded_file is None:
    st.warning('Please Upload the file to proceed !!!')
    st.experimental_rerun()
