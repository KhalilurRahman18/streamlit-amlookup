import streamlit as st
from streamlit_extras.app_logo import add_logo
from streamlit_extras.switch_page_button import switch_page

st.set_page_config(
    page_title="AMLookUp",
    page_icon="🔎",
)
st.write("# Welcome to AMLookUp! 🔎")
add_logo("logo.png", height=100)

st.markdown(
    """
    AMLookUp is an Machine Learning and Data Science projects initiated to combating
    Green Financial Crime and Money Laundering through 
    satellite imagery, and machine learning implementation.
"""
)
if st.button('Start'):        
        switch_page("Define_Entities")