import mimetypes
import streamlit as st
from main_functions import extract_info, setup_client, process_file

def upload_proposal_file():
    # Set up client
    client, processor_name, credentials = setup_client()

    # Set up a file uploader widget
    uploaded_file = st.file_uploader("Choose a file", type=["pdf", "tif", "tiff", "png", "jpg", "jpeg"])

    # When the user clicks the "Extract" button, process the file and display the text
    if st.button("Evaluate"):
        if uploaded_file is not None:
            mime_type = mimetypes.guess_type(uploaded_file.name)[0]
            if mime_type not in ['application/pdf', 'image/tiff', 'image/png', 'image/jpeg']:
                st.warning("Please upload a supported file type (PDF, TIFF, PNG, JPG).")
            else:
                process_file(mime_type, client, processor_name, uploaded_file, credentials)
        else:
            st.error("No file uploaded.")





def main():
    st.title('StealTheDeal')
    st.subheader('# Seal the Deal on Your Next Investment')
    st.subheader('Your Investment Partner: Our Application Helps You Make the Right Decisions')
    
    page = st.sidebar.selectbox("Choose a page", ["--Select Page--", "Upload Proposal File"])
    
    if page == "--Select Page--":
        st.write('')
        st.write('StealTheDeal is an investment evaluation application that helps investors make informed decisions about investing in proposals. The application allows users to upload proposals in any format and provides a comprehensive evaluation of the proposals viability. By leveraging sophisticated algorithms and machine learning techniques, StealTheDeal analyzes various factors such as market demand, financial viability, and risk assessment to determine whether the proposal is worth investing in or not. The application provides investors with a clear assessment of the investment opportunity and minimizes their exposure to potential losses. With StealTheDeal, investors can make more informed investment decisions and increase their chances of success.')
        st.write('')
        st.subheader("Please select a page from the list given on the sidebar")
    
    elif page == "Upload Proposal File":
        st.write('')
        st.write('Upload your investment proposal and get an evaluation of its viability.')
        st.write('')
        upload_proposal_file()

if __name__ == '__main__':
    main()