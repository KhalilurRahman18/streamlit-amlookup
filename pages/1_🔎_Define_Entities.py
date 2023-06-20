import streamlit as st
import time
import numpy as np
import pandas as pd
from streamlit_extras.app_logo import add_logo
from streamlit_extras.switch_page_button import switch_page
from urllib.error import URLError

st.set_page_config(page_title="Define Entities", page_icon="📃", layout="wide", 
    initial_sidebar_state="expanded")
st.markdown("# Define Entities")
st.markdown("Import Data (.csv)")
add_logo("logo.png", height=100)
# st.write(
#     """This demo illustrates a combination of plotting and animation with
# Streamlit. We're generating a bunch of random numbers in a loop for around
# 5 seconds. Enjoy!"""
# )
uploaded_file = st.file_uploader("Choose a Transaction Data")
uploaded_data = st.file_uploader("Choose a Company Data")

@st.cache_data
def from_data_file(file):
    dataframe = pd.read_csv(file)
    return dataframe


if uploaded_file is not None:
    try:
        dataframe = from_data_file(uploaded_file)
        dataframe = dataframe.drop(['isfraud', 'typeoffraud'], axis=1)
        dataframe.columns = ['Jenis Transaksi', 'No.Rek.Pengirim', 'No.Rek.Penerima', 'Jumlah Transaksi', 'Tanggal Transaksi']
        dataframe = dataframe.astype({'No.Rek.Pengirim': 'str', 'No.Rek.Penerima': 'str'})
        st.session_state['df'] = dataframe
        st.markdown("#### Transaction")
        st.write("Show 10 from {} data".format(len(dataframe.index)))
        st.dataframe(dataframe)
        st.write("Press “Analyze” button to analying data.")

        if st.button('Analyze'):
            st.write('Data is being analyzed')
            switch_page("Analyze_Transaction")
        else:
            st.write('')


    except URLError as e:
        st.error(
            """
            **This demo requires internet access.**
            Connection error: %s
        """
            % e.reason
            )
else :
    try:
        dataframecache = st.session_state['df']
        st.markdown("#### Financial Transaction")
        st.write("Menampilkan {} data".format(len(dataframecache.index)))
        st.dataframe(dataframecache)
        st.write("Press “Analyze” button to analying data.")

        if st.button('Analyze'):
            st.write('Data is being analyzed')
            switch_page("Analyze_Transaction")
        else:
            st.write('')
    except KeyError as e:
        st.error(
           """
            **Please define your data.**
            
        """
            )