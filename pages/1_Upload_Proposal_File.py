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

# Setting up the client
client, processor_name, credentials = setup_client()

# Creating a file uploader widget that allows users to upload only certain file types
uploaded_file = st.file_uploader("Choose a file", type=["pdf", "tif", "tiff", "png", "jpg", "jpeg"])

# When the "Evaluate" button is clicked, process the file and display the text
if st.button("Evaluate"):
    if uploaded_file is not None:
        # Determine the mime type of the uploaded file
        mime_type = mimetypes.guess_type(uploaded_file.name)[0]
        # Check if the mime type is supported
        if mime_type not in ['application/pdf', 'image/tiff', 'image/png', 'image/jpeg']:
            st.warning("Please upload a supported file type (PDF, TIFF, PNG, JPG).")
        else:
            # If the file type is supported, process the file
            process_file(mime_type, client, processor_name, uploaded_file, credentials)
    else:
        # If no file is uploaded, display an error message
        st.error("No file uploaded.")
