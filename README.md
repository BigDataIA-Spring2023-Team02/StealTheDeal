# Big Data Systems & Intelligence Analytics

## Team Information
| Name     | NUID        |
| ---      | ---         |
| Meet     | 002776055   |
| Ajin     | 002745287   |
| Siddhi   | 002737346   |
| Akhil    | 002766590   |

## About
This repository contains a collection of Big Data Systems & Intelligence Analytics Assignments & Projects that utilize the power of AWS and SQLite to process and analyze data using Streamlit. The assignments are designed to showcase the capabilities of these technologies in handling and processing large and complex datasets in real-time. The assignments cover various topics such as data ingestion, data processing, data storage, and data analysis, among others. Whether you are a big data enthusiast or a professional looking to build your skills in this field, this repository is a great resource to get started. So, go ahead, fork the repository and start working on these assignments to take your big data skills to the next level!

# Link to Live application
Streamlit: 
Codelabs: https://codelabs-preview.appspot.com/?file_id=1JUiP2P7-XNgthY3x2lD1vF1hmEAjJAJNVtv9sY-R9J8#3

# StealTheDeal
## Seal the Deal on Your Next Investment

The goal of this application is to develop an investment evaluation application that can assist investors in determining the viability of investment proposals. This application will allow users to upload proposals in any format and provide a clear assessment of whether the proposal is worth investing in or not. By leveraging sophisticated algorithms and machine learning techniques, the application will analyze the proposal and provide a comprehensive evaluation that takes into account various factors such as market demand, financial viability, and risk assessment. With this application, investors can make more informed investment decisions and minimize their exposure to potential losses.

# Installation
Clone this repository: git clone https://github.com/BigDataIA-Spring2023-Team02/StealTheDeal.git

### Project Tree:
```bash
.
└── StealTheDeal
    ├── pages
    │   ├── 1_Upload_Proposal_File.py
    │   ├── 2_Proposal_Dashboard.py
    │   └── 3_Proposal_Summary.py
    ├── .env
    ├── .gitignore
    ├── download.py
    ├── Home_Page.py
    ├── main_functions.py
    ├── README.md
    ├── requirements.txt
    └── *.json
```

### Prerequisites
* IDE
* Python 3.x
```bash
python -m venv stealdeal_venv
source stealdeal_venv\bin\activate
```

### Process Flow
* Create a python virtual environment and activate
```bash
python -m venv stealdeal_venv
```

* Activate the virtual environment
```bash
source stealdeal_venv/bin/activate  # on Linux/macOS
env\Scripts\activate     # on Windows
```

* Install the required packages from requirements.txt file
```bash
pip install -r requirements.txt
```

* Set your environment variable
```bash
key_path='*****.json'
project_id='*****'
storage_bucket_name='*****'
location='*****'
processor_id='*****'
client_options={'api_endpoint': f'{location}-documentai.googleapis.com'}
processor_name=f'projects/{project_id}/locations/{location}/processors/{processor_id}'
client=documentai.DocumentProcessorServiceClient(client_options=client_options)
bucket_name='*****'
openai.api_key="*****"
```

* Export your key_path environment variable to give access to user credentials
```bash
export GOOGLE_APPLICATION_CREDENTIALS="*****.json"
```

* Run Streamlit app
```bash
streamlit run Home_Page.py
```


========================================================================================================================
> WE ATTEST THAT WE HAVEN’T USED ANY OTHER STUDENTS’ WORK IN OUR ASSIGNMENT AND ABIDE BY THE POLICIES LISTED IN THE STUDENT HANDBOOK.
> Meet: 25%, Ajin: 25%, Siddhi: 25%, Akhil: 25%