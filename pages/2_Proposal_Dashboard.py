import streamlit as st
from main_functions import create_graph, create_donut_chart, evaluate_investability, list_uploaded_file, extract_info, setup_client

# Setting the title and header of the application
st.title('StealTheDeal')
st.header('# Seal the Deal on Your Next Investment')
st.write('')

client, processor_name, credentials = setup_client()

# Get the list of uploaded files
uploaded_files = list_uploaded_file(credentials)

# Create a dropdown menu to display the uploaded files
selected_file = st.selectbox("Select an uploaded file", uploaded_files)



if selected_file:
    # If a file is selected, process the information
    information,text = extract_info(selected_file,credentials)

    fig = create_graph(information)
    st.plotly_chart(fig)
    
    investability = evaluate_investability(text)
    if investability >= 7:
        st.success(f"Investability Score: {investability}")
    elif investability >= 4:
        st.warning(f"Investability Score: {investability}")
    else:
        st.error(f"Investability Score: {investability}")
    
    st.write('')
    
    donut_chart = create_donut_chart(investability)
    st.plotly_chart(donut_chart)

if "information" not in st.session_state:
    st.session_state.information = None

if st.session_state.information is None:
    st.warning('Please see if the file is evaluated successfully !!!')
