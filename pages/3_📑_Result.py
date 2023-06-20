import streamlit as st
import pandas as pd
from urllib.error import URLError
from streamlit_extras.app_logo import add_logo
from collections import defaultdict
from IPython.core.display import display, HTML
import streamlit.components.v1 as components

st.set_page_config(page_title="Detail Transaksi", page_icon="📊", layout="wide", 
    initial_sidebar_state="expanded")

st.markdown("# Result Detail")
add_logo("logo.png", height=100)
try:
        transact = st.session_state['df']
        noorek = st.session_state['noorek'] 

        def show_graph(graph):
            HtmlFile = open(graph, 'r', encoding='utf-8')
            source_code = HtmlFile.read() 
            components.html(source_code, height = 550,width=1100)

        st.markdown("## Grafik Social Network Analysis")
        show_graph("10_show_group_with_given_node.html")
        st.markdown("## Daftar Transaksi")

        transact.columns = ['Jenis Transaksi','NoRekening', 'NoRekeningPenerima', 'Jumlah Transaksi', 'Tanggal Transaksi']

        col1, col2 = st.columns(2)
        col1.header("Transaksi Keluar")
        col1.dataframe(transact[(transact.NoRekening == noorek)])
        col2.header("Transaksi Masuk")
        col2.dataframe(transact[(transact.NoRekeningPenerima == noorek)])
except KeyError as e:
        st.error(
           """
            **Please define your data.**
            
        """
            )