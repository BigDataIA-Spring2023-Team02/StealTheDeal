import os
import re
import openai
import pandas as pd
from dotenv import load_dotenv
import plotly.graph_objs as go
import plotly.graph_objects as go
from google.cloud import storage
from nltk.stem import WordNetLemmatizer
from google.oauth2 import service_account
from nltk.tokenize import word_tokenize, sent_tokenize
from google.cloud import documentai_v1beta3 as documentai


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


def extract_info(selected_file,credentials):   

    # Define the filename variable
    filename = selected_file

    # Download the file from Google Cloud Storage
    storage_project_id = os.environ.get('project_id')
    bucket_name = os.environ.get('bucket_name')
    storage_client = storage.Client(project=storage_project_id, credentials=credentials)
    bucket = storage_client.get_bucket(bucket_name)
    
    blob = bucket.blob(f'extract/{filename}')
    text = blob.download_as_text() 
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

    return output_dict, text


def upload_file(uploaded_file, credentials):
    # Upload the original file to GCS
    storage_project_id = os.environ.get('project_id')
    bucket_name = os.environ.get('bucket_name')
    storage_client = storage.Client(project = storage_project_id, credentials = credentials)
    bucket = storage_client.get_bucket(bucket_name)
    blob = bucket.blob('docs/' + uploaded_file.name)
    blob.upload_from_string(uploaded_file.getvalue())
    

def list_uploaded_file(credentials):
    storage_project_id = os.environ.get('project_id')
    bucket_name = os.environ.get('bucket_name')
    storage_client = storage.Client(project = storage_project_id, credentials = credentials)
    bucket = storage_client.get_bucket(bucket_name)
    
    blobs = bucket.list_blobs(prefix='extract/')
    files = [blob.name.split('/')[1] for blob in blobs]
    
    return files


def process_file(mime_type, client, processor_name, uploaded_file, credentials):
    """Process a file through the Document AI parser."""
    
    # Run the file through the Document AI parser and extract the text
    content = uploaded_file.read()
    document = documentai.types.Document(content = content, mime_type = mime_type)
    name = processor_name
    response = client.process_document(request={'name': name, 'document': document})
    document = response.document
    text = document.text
    text = lemmatize_text(text)

    # Upload the extracted text to GCS
    storage_project_id = os.environ.get('project_id')
    bucket_name = os.environ.get('bucket_name')
    storage_client = storage.Client(project = storage_project_id, credentials = credentials)
    bucket = storage_client.get_bucket(bucket_name)
    extracted_text_filename = 'extracted_' + uploaded_file.name.split('.')[0] + '.txt'
    blob = bucket.blob('extract/' + extracted_text_filename)
    blob.upload_from_string(text)
    
    
    return text


def evaluate_investability(text):
    # Preprocess text by removing non-alphanumeric characters and short words
    if not isinstance(text, str):
        return 0
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
    investability_score = float(response.choices[0].text.strip())
    
    return investability_score


def convert_to_float(value):
    if value == '' or value is None:
        return 0.0
    
    if isinstance(value, str):
        value = value.replace('$', '').replace(',', '')

        if value[-1] == 'M':
            return float(value[:-1]) * 1000000
        elif value[-1] == 'B':
            return float(value[:-1]) * 1000000000
        else:
            # Handle cases like '5 million'
            match = re.search(r'([\d.]+)\s*(million|billion|M|B)?', value)
            if match:
                num = float(match.group(1))
                unit = match.group(2)
                if unit:
                    if unit.lower() == 'million' or unit.lower() == 'm':
                        return num * 1000000
                    elif unit.lower() == 'billion' or unit.lower() == 'b':
                        return num * 1000000000
                else:
                    return num
            else:
                return 0.0
    
    else:
        return float(value)


def create_graph(output_dict):
    # Process the values and convert them to numbers if needed
    for key in output_dict:
        output_dict[key] = [convert_to_float(value) for value in output_dict[key]]

    # Create a DataFrame from the dictionary
    df = pd.DataFrame(output_dict, columns=output_dict.keys())

    sums = [df[col].sum() for col in df.columns]

    # Create a bar chart with the sums of each key
    fig = go.Figure(data=[
        go.Bar(name='Sales', x=df.columns, y=sums)
    ])

    fig.update_layout(
        title='Metrics Overview',
        xaxis_title='Metrics',
        yaxis_title='Value',
    )

    return fig


def create_bar_chart(investability_score):
    fig = go.Figure(data=[
        go.Bar(name='Investability Score', x=['Investability Score'], y=[investability_score]),
        go.Bar(name='Remaining', x=['Remaining'], y=[10 - investability_score])
    ])

    fig.update_layout(
        title='Investability Score (Out of 10)',
        xaxis_title='Score',
        yaxis_title='Value',
        barmode='stack',
    )

    return fig


def create_donut_chart(investability_score):
    fig = go.Figure(go.Pie(
        labels=['Investability Score', 'Remaining'],
        values=[investability_score, 10 - investability_score],
        hole=.3,
        marker_colors=['#00b894', '#d3d3d3']
    ))

    fig.update_layout(
        title='Investability Score (Out of 10)',
        legend_title='Score',
    )

    return fig


def brief_summary(information):    
    max_length = 1000
    chunks = re.findall(r'.{1,%d}\b(?!\S)' % max_length, information)
    
    prompt = (
        "Give me 1 strong points for  :\n "
    )
    
    outputs = []
    for chunk in chunks:
        response = openai.Completion.create(
            engine = "text-davinci-002",
            prompt = prompt + chunk,
            max_tokens = 1024,
            n = 1,
            stop = None,
            temperature = 0.5,
        )
        outputs.append(response.choices[0].text.strip())
    
    summary = "\n".join(outputs)
    return summary


def key_question(information):    
    max_length = 1000
    chunks = re.findall(r'.{1,%d}\b(?!\S)' % max_length, information)
    
    prompt = (
        "Give 3 questions that needs to be asked to the pitcher"
    )
    
    outputs = []
    for chunk in chunks:
        response = openai.Completion.create(
            engine = "text-davinci-002",
            prompt = prompt + chunk,
            max_tokens = 1024,
            n = 1,
            stop = None,
            temperature = 0.5,
        )
        outputs.append(response.choices[0].text.strip())
    
    questions = "\n".join(outputs)
    return questions
