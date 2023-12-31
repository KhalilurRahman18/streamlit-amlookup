import streamlit as st
import time
import numpy as np
import pandas as pd
from streamlit_extras.app_logo import add_logo
from streamlit_extras.switch_page_button import switch_page
from urllib.error import URLError
import streamlit as st
import pandas as pd
import time
import base64
import googlemaps
import gmaps
import folium
from streamlit_folium import folium_static

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
        st.session_state['df1'] = dataframe
        st.markdown("#### Financial Transaction Data")
        st.write("Show 10 from {} data".format(len(dataframe.index)))
        st.dataframe(dataframe)        
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
        st.markdown("#### Financial Transaction Data")
        st.write("Menampilkan {} data".format(len(dataframecache.index)))
        st.dataframe(dataframecache)
    except KeyError as e:
        st.error(
           """
            **Please define your data.**
            
        """
            )

if uploaded_data is not None:
    try:
        dataframe1 = from_data_file(uploaded_data)
        dataframe1 = dataframe1.drop(["rt_perseroan","rw_perseroan","kode_pos_perseroan","provinsi_id_perseroan","kabupaten_id_perseroan","kecamatan_id_perseroan","kelurahan_id_perseroan"], axis=1)
        dataframe1.columns = ["nama_perseroan","alamat_perseroan","provinsi_nama_perseroan","kabupaten_nama_perseroan","kecamatan_nama_perseroan","kelurahan"]        
        st.session_state['df2'] = dataframe1
        st.markdown("#### Company Data")
        st.write("Show 10 from {} data".format(len(dataframe1.index)))
        st.dataframe(dataframe1)
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
        dataframecache1 = st.session_state['df1']
        st.markdown("#### Company Data")
        st.write("Menampilkan {} data".format(len(dataframecache1.index)))
        st.dataframe(dataframecache1)
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

def create_address_col(df):
    st.sidebar.title("Select Address columns")
    st.sidebar.info("You need to select address column (Street name and number), post code and City")
    address_name = st.sidebar.selectbox("Select Address column", df.columns.tolist())    
    city = st.sidebar.selectbox("Select the City Column", df.columns.tolist())
    country = st.sidebar.text_input("Write the country of the addresses")
    df["geocode_col"] =  df[address_name].astype(str) + ',' + df[city] + ',' + country   
    return df
    
def choose_geocode_column(df):
    selection = st.selectbox("Select the column", df.columns.tolist())
    df["geocde_col"] = df[selection]
    return df

def geocode_address(row):    
    geocode_result = gmaps.geocode(row['geocode_col'])
    print(geocode_result[0]['geometry']['location']['lat'])
    #row['latitude'] = geocode_result[0]['geometry']['location']['lat']
    #row['longitude'] = geocode_result[0]['geometry']['location']['lng']
    return row

def geocode(df):    
    gmaps = googlemaps.Client(key='AIzaSyBhS__8UQvbimnR301g0wOiG_dEwycKB-Q')
    #locator = Nominatim(user_agent="myGeocoder")
    #geocode = RateLimiter(locator.geocode, min_delay_seconds=1)    
    #df['location'] = df['geocode_col'].apply(geocode)        
    df['latitude'] = None  # Create the 'latitude' column with initial None values
    df['longitude'] = None  # Create the 'longitude' column with initial None values
    for x in range(len(df)):
        geocode_result = gmaps.geocode(df['geocode_col'][x])
        df['latitude'][x] = geocode_result[0]['geometry']['location'] ['lat']
        df['longitude'][x] = geocode_result[0]['geometry']['location']['lng']
    #output = df['geocode_col'].apply(gmaps.geocode)
    print(df)
    #df['point'] = df['location'].apply(lambda loc: tuple(loc.point) if loc else None)
    #df[['latitude', 'longitude', 'altitude']] = pd.DataFrame(df['point'].tolist(), index=df.index)
    output = df[['latitude', 'longitude']]
    return output

st.cache(persist=True, suppress_st_warning=True)
def display_map(df):
    '''
    px.set_mapbox_access_token("pk.eyJ1Ijoia2hhbGlsdXIxOCIsImEiOiJja2J2ajIzencwNmo0MzFwM3JtdTF1eGlrIn0.pjwEihVupN6CqkBme-YhMw")
    fig = px.scatter_mapbox(df, lat='latitude', lon='longitude')
    '''
    m = folium.Map(location=[df.latitude.mean(), df.longitude.mean()], 
                 zoom_start=3, control_scale=True)

    #Loop through each row in the dataframe
    for i,row in df.iterrows():
        #Setup the content of the popup
        iframe = folium.IFrame('Well Name:' + str(row['latitude']) +','+ str(row['longitude']))
        
        #Initialise the popup using the iframe
        popup = folium.Popup(iframe, min_width=300, max_width=300)
        
        #Add each row to the map
        folium.Marker(location=[row['latitude'],row['longitude']],
                    popup = popup, c=row['latitude']).add_to(m)
    
    fig = folium_static(m, width=700)
    return fig


def download_csv(df):
    csv = df.to_csv(index=False)
    b64 = base64.b64encode(csv.encode()).decode()  # some strings <-> bytes conversions necessary here
    href = f'<a href="data:file/csv;base64,{b64}">Download CSV File</a> (right-click and save as &lt;some_name&gt;.csv)'
    return href


def main():
    file = st.file_uploader("Choose a CSV file", type="csv")

    if file is not None:
        df = pd.read_csv(file)
        with st.spinner('Reading CSV File...'):
            time.sleep(5)
            st.success('Done!')
        st.subheader("Your CSV Table ....")
        st.write(df.head())

        cols = df.columns.tolist()

        st.subheader("Choose Address Columns from the Sidebar")
        st.info("Example correct address: Karlaplan 13,115 20,STOCKHOLM, Sweden")
        

        if st.checkbox("Address Formatted correctly (Example Above)"):
            df_address = choose_geocode_column(df)
            st.write(df_address["geocode_col"].head())
            #geocoded_df = geocode(df_address)
            with st.spinner('Geocoding Hold tight...'):
                time.sleep(5)
            st.success('Done!')
            #st.write(geocoded_df.head())
            #st.plotly_chart(display_map(geocoded_df))
            
            st.markdown(download_csv(geocoded_df), unsafe_allow_html=True)
        if st.checkbox("Not Correctly Formatted"):
            df_address = create_address_col(df)
            st.write(df_address["geocode_col"].head())
            geocoded_df = geocode(df_address)
            with st.spinner('Geocoding Hold tight...'):
                time.sleep(5)
            st.success('Done!')
            st.write(geocoded_df.head())
            #st.plotly_chart(display_map(geocoded_df))
            display_map(geocoded_df)
            st.markdown(download_csv(geocoded_df), unsafe_allow_html=True)

if __name__ == "__main__":
    main()
