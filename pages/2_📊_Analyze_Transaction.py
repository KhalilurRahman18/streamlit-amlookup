import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import pydeck as pdk
from urllib.error import URLError
from streamlit_extras.app_logo import add_logo
import pandas as pd
import networkx as nx
from pyvis import network as net
from pyvis.network import Network
import matplotlib.pyplot as plt
pd.options.display.float_format = '{:,.0f}'.format
from collections import defaultdict
from IPython.core.display import  HTML
import pickle
from streamlit_extras.switch_page_button import switch_page


st.set_page_config(
    page_title="Analyze Transaction", 
    page_icon="🔎",
    layout="wide", 
    initial_sidebar_state="expanded"
    )

st.markdown("# Analyze Transaction")
add_logo("logo.png", height=100)

try:
        dataframe = st.session_state['df']
        txn_full = dataframe.iloc[:, [1,2,3]]
        txn_full = txn_full.astype('object')
        txn_full.columns = ['sourceid','destinationid', 'amountofmoney']
        txn_full['amountofmoney'] = txn_full['amountofmoney'].astype(float)
        edge_large = txn_full.groupby(['sourceid', 'destinationid'],as_index=False).agg({'amountofmoney':['count','sum']})
        edge_large.columns = ['source','target','agg_edge_large_count','agg_edge_large_amt']
        st.session_state['detail'] = edge_large
        edge_large['value'] = edge_large['agg_edge_large_amt']
        edge_large['title'] = edge_large.apply(lambda df: f'from: {df.source}\nto: {df.target}\nagg_count: {df.agg_edge_large_count:,.0f}\nagg_amount: {df.agg_edge_large_amt:,.0f}', axis=1)
        H = nx.from_pandas_edgelist(edge_large, source='source', target='target', edge_attr=['title','value'], create_using=nx.DiGraph)

        group_dict_H = {}
        for group, nodes in enumerate(sorted(list(nx.weakly_connected_components(H)), key=len, reverse=True), start=1):
            for node in nodes:
                group_dict_H[node] = group

        groups = pd.DataFrame({'source':group_dict_H.keys(), 'group':group_dict_H.values()}).sort_values(by=['group','source'])
        group_summary = groups.groupby('group', as_index=False).agg({'source':'count'}).rename(columns={'source':'num_of_nodes'})

        nx.set_node_attributes(H, group_dict_H, 'group')

        degree_dict_H = dict(H.degree)
        nx.set_node_attributes(H, degree_dict_H, 'value')

        neighbor_dict_H = {}
        for node in list(H.nodes):
            neighbor_dict_H[node] = ','.join(H.neighbors(node))

        title_dict_H = {}
        for node in list(H.nodes):
            title_dict_H[node] = f'id: {node}\ngroup: {group_dict_H[node]}\ndegree: {degree_dict_H[node]}\nneighbor: {neighbor_dict_H[node]}'
        nx.set_node_attributes(H, title_dict_H, 'title')


        target_groups = list(range(20,29))
        target_nodes = [node for node, group in group_dict_H.items() if group in target_groups]

        H_sub = H.subgraph(target_nodes)

        nt = net.Network(height='500px', width='100%', directed=True, notebook=True, cdn_resources='local')
        nt.from_nx(H_sub)

        pos = nx.spring_layout(H_sub, scale=1000, seed=721, k=0.01)
        for node in nt.nodes:
            node['x'] = pos[node['id']][0]
            node['y'] = pos[node['id']][1]

        nt.show('09_communities_spring.html')

        # @st.cache_resource
        def show_graph(graph):
            HtmlFile = open(graph, 'r', encoding='utf-8')
            source_code = HtmlFile.read() 
            components.html(source_code, height = 550,width=1100)

        st.markdown("## Grafik Social Network Analysis")
        show_graph("09_communities_spring.html")

        datarekeningkirim = txn_full.groupby(['sourceid'],as_index=False).agg({'amountofmoney':['count','sum']})
        datarekeningterima = txn_full.groupby(['destinationid'],as_index=False).agg({'amountofmoney':['count','sum']})
        datarekeningkirim.columns = ['NoRekening','Jumlah Transaksi','Total Transaksi']
        datarekeningterima.columns = ['NoRekening','Jumlah Transaksi','Total Transaksi']
        st.markdown("## Data Transaksi")
        noorek = st.text_input('Masukan Nomor Rekening', '')
        st.session_state['noorek'] = noorek

        #Load Fitur SNA
        datapredict = pd.read_csv("hasilgephi.csv")
        datafeature = datapredict.iloc[:, [1,2,3,4,5]]

        filename = 'finalized_model_tuning_SNAfeature_new.sav'
        loaded_model = pickle.load(open(filename, 'rb'))
        y_pred = loaded_model.predict(datafeature)
        datapredict['Hasil Prediksi'] = y_pred
        datapredict = datapredict.astype({'Id': 'str'})
        datapredict = datapredict.iloc[:, [0,6]]
        datapredict.columns = ['NoRekening','Hasil Prediksi']
        columnss=['Hasil Prediksi']
        for var in columnss:
            datapredict[var] = datapredict[var].map(lambda e: 'Terindikasi TKM' if e == 1 else 'Tidak Terindikasi TKM')
        st.markdown("## Hasil Prediksi Model Machine Learning")



        if noorek == "":
            st.dataframe(datapredict)
            col1, col2 = st.columns(2)
            col1.header("Transaksi Keluar")
            col1.dataframe(datarekeningkirim)
            col2.header("Transaksi Masuk")
            col2.dataframe(datarekeningterima)
        else :
            st.dataframe(datapredict[(datapredict.NoRekening == noorek)])
            col1, col2 = st.columns(2)
            col1.header("Transaksi Keluar")
            col1.dataframe(datarekeningkirim[(datarekeningkirim.NoRekening == noorek)])
            col2.header("Transaksi Masuk")
            col2.dataframe(datarekeningterima[(datarekeningterima.NoRekening == noorek)])

        if noorek == "":
            st.write("")
        else :
            target_node = noorek
            target_groups = [dict(H.nodes(data=True))[target_node]['group']]
            target_nodes = [node for node, group in group_dict_H.items() if group in target_groups]

            H_sub = H.subgraph(target_nodes)

            nt = net.Network(height='500px', width='100%', directed=True, notebook=True, cdn_resources='local')
            nt.from_nx(H_sub)

            pos = nx.spring_layout(H_sub, scale=1000, seed=721, k=0.01)
            for node in nt.nodes:
                node['x'] = pos[node['id']][0]
                node['y'] = pos[node['id']][1]

            [node for node in nt.nodes if node['id']==target_node][0]['shape'] = 'image'
            [node for node in nt.nodes if node['id']==target_node][0]['image'] = 'https://openmoji.org/data/color/svg/1F608.svg'
            [node for node in nt.nodes if node['id']==target_node][0]['color'] = '#ff4f4f'

            nt.show('10_show_group_with_given_node.html')

            if st.button('Lihat Detail Transaksi'):
                st.write('Transaksi Sedang Di Proses')
                switch_page('Result')
            else:
                st.write('')
except KeyError as e:
        st.error(
           """
            **Please define your data.**
            
        """
            )