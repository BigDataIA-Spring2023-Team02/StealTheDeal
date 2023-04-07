# Importing necessary modules
import streamlit as st
from main_functions import create_graph, create_donut_chart, evaluate_investability

# Setting the title and header of the application
st.title('StealTheDeal')
st.header('# Seal the Deal on Your Next Investment')
st.write('')

if st.session_state.information is not None:
    # If the user has already entered information, we will use it
    information = st.session_state.information
    processed_text = st.session_state.processed_text
    
    fig = create_graph(information)
    st.plotly_chart(fig)
    
    investability = evaluate_investability(processed_text)
    st.write('Investability Score:',investability)
    st.write('')
    
    donut_chart = create_donut_chart(investability)
    st.plotly_chart(donut_chart)

if st.session_state.information is None:
    st.warning('Please see if the file is evaluated successfully !!!')
