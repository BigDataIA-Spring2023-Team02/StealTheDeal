import os
import re
import nltk
import openai
from dotenv import load_dotenv
from google.cloud import storage
from nltk.stem import WordNetLemmatizer
from google.oauth2 import service_account
from nltk.tokenize import word_tokenize, sent_tokenize
from google.cloud import documentai_v1beta3 as documentai
import streamlit as st
import plotly.graph_objs as go
import plotly.express as px
import pandas as pd
import matplotlib.pyplot as plt
import locale
import plotly.graph_objects as go


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
    openai.api_key = os.environ.get('openai.api_key')
    
    return client, processor_name, credentials

def lemmatize_text(text):
    """Lemmatize the extracted text."""
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
    max_length = 1000
    chunks = re.findall(r'.{1,%d}\b(?!\S)' % max_length, text)
    
    prompt = (
        "Extract and convert into the integer value of Total Sales, Total Revenue, Total Valuation, and Owners Equity from the following text and just give me the number with it value if the number have text convert it into its numberic form:\n\n"
        "Total Sales:\n"
        "Total Revenue:\n"
        "Total Valuation:\n"
        "Owners Equity:\n"
    )

    # Send each chunk to the GPT API and collect the output
    outputs = []
    output_dict = {'Sales': [], 'Revenue': [], 'Valuation': [], 'Equity': []}
    
    for chunk in chunks:
        response = openai.Completion.create(
            engine="text-davinci-002",
            prompt=chunk + prompt,
            max_tokens=1024,
            n=1,
            stop=None,
            temperature=0.5,
        )

        for choice in response.choices:
            # Split the choice text into lines and extract the relevant information
            choice_text = choice.text.strip()
            lines = choice_text.split("\n")
            sales, revenue, valuation, equity = "", "", "", ""
            for line in lines:
                if "Total Sales:" in line:
                    sales = (line.split("Total Sales:")[1].split("\n")[0].strip())
                elif "Total Revenue:" in line:
                    revenue = (line.split("Total Revenue:")[1].split("\n")[0].strip())
                elif "Total Valuation:" in line:
                    valuation = (line.split("Total Valuation:")[1].split("\n")[0].strip())
                elif "Owners Equity:" in line:
                    equity = (line.split("Owners Equity:")[1].split("\n")[0].strip())

            # Append the relevant information to the output dictionary
            output_dict["Sales"].append(sales)
            output_dict["Revenue"].append(revenue)
            output_dict["Valuation"].append(valuation)
            output_dict["Equity"].append(equity)

    return output_dict  # Return the output_dict instead of the undefined variable 'info'


    
   

def process_file(mime_type, client, processor_name, uploaded_file, credentials):
    """Process a file through the Document AI parser."""
    
    # Run the file through the Document AI parser and extract the text
    content = uploaded_file.read()
    document = documentai.types.Document(content = content, mime_type = mime_type)
    name = processor_name
    response = client.process_document(request={'name': name, 'document': document})
    document = response.document
    text = document.text

    # Upload the extracted text to GCS
    storage_project_id = os.environ.get('project_id')
    bucket_name = os.environ.get('bucket_name')
    storage_client = storage.Client(project = storage_project_id, credentials = credentials)
    bucket = storage_client.get_bucket(bucket_name)
    blob = bucket.blob('extract/extracted_text.txt')
    blob.upload_from_string(text)
    text = lemmatize_text(text)
    
    info = extract_info(text)
    st.write(info)
    fig = create_graph(info)
    st.plotly_chart(fig)
    invest = evaluate_investability(text)
    st.write(invest)
    return info
    
 


def evaluate_investability(text):
    # Preprocess text by removing non-alphanumeric characters and short words
    text = re.sub(r'\W+', ' ', text)
    text = ' '.join([word for word in text.split() if len(word) > 3])
    
    # Use GPT-3 to generate a score indicating the investability of the business
    prompt = "Evaluate the investability of the following business:\n" + text + "\nInvestability score:"
    response = openai.Completion.create(
        engine="text-davinci-002",
        prompt=prompt,
        temperature=0.5,
        max_tokens=50,
        n=1,
        stop=None,
        timeout=10,
    )
    investability_score = response.choices[0].text.strip()
    
    return investability_score


def convert_to_float(value):
    if value == '':
        return 0.0
    value = value.replace('$', '').replace(',', '')
    if value[-1] == 'M':
        return float(value[:-1]) * 1000000
    elif value[-1] == 'B':
        return float(value[:-1]) * 1000000000
    else:
        return float(value)


def create_graph(output_dict):
    # Process the values and convert them to numbers if needed
    for key in output_dict:
        output_dict[key] = [convert_to_float(value) for value in output_dict[key]]

    # Create a DataFrame from the dictionary
    df = pd.DataFrame(output_dict, columns=output_dict.keys())

    # Create a bar chart using Plotly
    fig = go.Figure()

    for col in df.columns:
        fig.add_trace(go.Bar(x=[col], y=[df[col].sum()], name=col))

    fig.update_layout(
        title='Financial Overview',
        xaxis_title='Metrics',
        yaxis_title='Amount ($)',
        legend_title='Metrics',
        plot_bgcolor='rgba(255, 255, 255, 1)',
    )

    return fig