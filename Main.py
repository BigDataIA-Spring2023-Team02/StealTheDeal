import streamlit as st
from google.cloud import documentai_v1beta3 as documentai
from google.oauth2 import service_account
import mimetypes
from dotenv import load_dotenv
from google.cloud import storage
import os
import openai
import nltk
from nltk.tokenize import word_tokenize, sent_tokenize
from nltk.stem import WordNetLemmatizer




def lemmatize_text(text):
    """Lemmatize the extracted text."""
    # nltk.download('punkt')
    # nltk.download('wordnet')
    # nltk.download('omw-1.4')

    # nltk.download()

    lemmatizer = WordNetLemmatizer()
    # Tokenize the text into sentences
    sentences = sent_tokenize(text)
    # Tokenize each sentence into words, lemmatize them and join back into a sentence
    lemmatized_sentences = []
    for sentence in sentences:
        words = word_tokenize(sentence)
        lemmatized_words = []
        for word in words:
            lemmatized_word = lemmatizer.lemmatize(word)
            lemmatized_words.append(lemmatized_word)
        lemmatized_sentence = " ".join(lemmatized_words)
        lemmatized_sentences.append(lemmatized_sentence)
    # Join the lemmatized sentences back into a single string
    lemmatized_text = " ".join(lemmatized_sentences)
    return lemmatized_text


def extract_info(text):
    prompt = (
        "Extract the Total Sales, Total Revenue, Total Valuation, and Owners Equity from the following text:\n\n"
        f"{text}\n\n"
        "Total Sales:\n"
        "Total Revenue:\n"
        "Total Valuation:\n"
        "Owners Equity:\n"
    )
    response = openai.Completion.create(
        engine="text-davinci-002",
        prompt=prompt,
        temperature=0.5,
        max_tokens=1024,
        n=1,
        stop=None,
        timeout=60,
    )
    if len(response.choices) > 0:
        choices = response.choices[0]
        sales = choices.text.split("Total Sales:")[1].split("\n")[0].strip()
        revenue = choices.text.split("Total Revenue:")[1].split("\n")[0].strip()
        valuation = choices.text.split("Total Valuation:")[1].split("\n")[0].strip()
        equity = choices.text.split("Owners Equity:")[1].split("\n")[0].strip()
        return sales, revenue, valuation, equity
    else:
        return None


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
    openai.api_key =os.environ.get('openai.api_key')
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
        # st.write(text)

        # Upload the extracted text to GCS
        storage_project_id = os.environ.get('project_id')
        bucket_name = os.environ.get('bucket_name')
        storage_client = storage.Client(project=storage_project_id, credentials=credentials)
        bucket = storage_client.get_bucket(bucket_name)
        blob = bucket.blob('extract/extracted_text.txt')
        blob.upload_from_string(text)

        text = lemmatize_text(text)
        st.write(text)


        # sales, revenue, valuation, equity = extract_info(text)
        # st.write("Total Sales:", sales)
        # st.write("Total Revenue:", revenue)
        # st.write("Total Valuation:", valuation)
        # st.write("Owners Equity:", equity)




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