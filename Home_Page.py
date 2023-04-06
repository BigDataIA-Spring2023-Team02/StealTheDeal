# Importing the streamlit module
import streamlit as st

# Defining the main function of the application
def main():
    
    # Setting the title of the application
    st.title('StealTheDeal')
    
    # Adding header for the application
    st.header('# Seal the Deal on Your Next Investment')
    st.header('Your Investment Partner: Our Application Helps You Make the Right Decisions')
    st.write('')
    
    # Describing the application in brief
    st.write('StealTheDeal is an investment evaluation application that helps investors make informed decisions about investing in proposals. The application allows users to upload proposals in any format and provides a comprehensive evaluation of the proposals viability. By leveraging sophisticated algorithms and machine learning techniques, StealTheDeal analyzes various factors such as market demand, financial viability, and risk assessment to determine whether the proposal is worth investing in or not. The application provides investors with a clear assessment of the investment opportunity and minimizes their exposure to potential losses. With StealTheDeal, investors can make more informed investment decisions and increase their chances of success.')
    st.write('')
    
    # Adding a sub-header to the application
    st.subheader("Please select a page from the list given on the sidebar")

# Condition to run the main function when the script is executed
if __name__ == '__main__':
    main()
