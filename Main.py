import streamlit as st
from google.cloud import documentai_v1beta3 as documentai
from google.oauth2 import service_account
import mimetypes
from dotenv import load_dotenv
from google.cloud import storage
import os


def setup_client():
    """Set up credentials and Document AI client."""
    load_dotenv()
    key_path = os.environ.get('key_path')
    credentials = service_account.Credentials.from_service_account_file(key_path)
    project_id = os.environ.get('project_id')
    location = os.environ.get('location')  # The location of the processing resources
    processor_id = os.environ.get('processor_id') # replace with your processor_id variable
    client_options = {'api_endpoint': f'{location}-documentai.googleapis.com'}
    processor_name = f'projects/{project_id}/locations/{location}/processors/{processor_id}'
    client = documentai.DocumentProcessorServiceClient(client_options=client_options)
    return client, processor_name, credentials


def process_file(client, processor_name, uploaded_file, credentials):
    """Process a file through the Document AI parser."""
    # Check if the uploaded file is a supported type
    mime_type = mimetypes.guess_type(uploaded_file.name)[0]
    if mime_type not in ['application/pdf', 'image/tiff', 'image/png', 'image/jpeg']:
        st.warning("Please upload a supported file type (PDF, TIFF, PNG, JPG).")
    else:
        # Run the file through the Document AI parser and extract the text
        content = uploaded_file.read()
        document = documentai.types.Document(content=content, mime_type=mime_type)
        name = processor_name
        response = client.process_document(request={'name': name, 'document': document})
        document = response.document
        text = document.text

        # Display the extracted text on the Streamlit app
        st.write(text)

        # Upload the extracted text to GCS
        storage_project_id = os.environ.get('project_id')
        bucket_name = os.environ.get('bucket_name')
        storage_client = storage.Client(project=storage_project_id, credentials=credentials)
        bucket = storage_client.get_bucket(bucket_name)
        blob = bucket.blob('extract/extracted_text.txt')
        blob.upload_from_string(text)


def main():
    # Set up client
    client, processor_name, credentials = setup_client()

    # Set up a file uploader widget
    uploaded_file = st.file_uploader("Choose a file", type=["pdf", "tif", "tiff", "png", "jpg", "jpeg"])

    # When the user clicks the "Extract" button, process the file and display the text
    if st.button("Extract"):
        if uploaded_file is not None:
            process_file(client, processor_name, uploaded_file, credentials)
        else:
            st.warning("No file uploaded.")


if __name__ == '__main__':
    main()
