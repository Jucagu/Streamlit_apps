import streamlit as st
import pandas as pd
import numpy as np
import pydeck as pdk
import plotly.express as px

DATA_URL = "https://drive.google.com/uc?export=download&id=1K5aCEBQ6S78QXiNWry5MzuIuGejSadFk"
st.title("Choques de vehiculos en Nueva York")
st.markdown('Esta aplicacion es un dashboard en streamlit que permite analizar los choques vehiculares en NYC')
@st.cache(persist=True)
def load_data(nrows):
    data=pd.read_csv(DATA_URL,nrows=nrows,parse_dates=[['CRASH_DATE','CRASH_TIME']])
    data.dropna(subset=['LATITUDE','LONGITUDE'],inplace=True)
    lowercase=lambda x :str(x).lower()
    data.rename(lowercase,axis='columns',inplace=True)
    data.rename(columns={'crash_date_crash_time':'date/time'},inplace=True)
    return data
data=load_data(400000)
original_data=data
st.header('Donde hay mas heridos en NYC?')
heridos=st.slider("Numero de personas heridas ",0,19)
st.map(data.query("injured_persons >= @heridos")[["latitude","longitude"]].dropna(how="any"))

st.header('Cuantos accidentes ocurrieron en una hora dada')
hora=st.slider('Seleccione la hora a consultar',0,23)
data=data[data['date/time'].dt.hour==hora]

st.markdown('Choques de vehiculos entre %i:00 y %i:00' %(hora, (hora+1)%24))
puntomedio=(np.average(data['latitude']),np.average(data['longitude']))
st.write(pdk.Deck(
    map_style='mapbox://styles/mapbox/light-v9',
    initial_view_state={
        'latitude':puntomedio[0],
        'longitude':puntomedio[1],
        'zoom':11,
        'pitch':50,

    },
    layers=[
    pdk.Layer(
    "HexagonLayer",
    data=data[['date/time','latitude','longitude']],
    get_position=['longitude','latitude'],
    radius=100,
    extruded=True,
    pickable=True,
    elevation_scale=4,
    elevation_range=[0,1000],
    )
    ]
))

st.subheader('Numero de choques por minuto entre %i:00 y %i:00' %(hora, (hora+1)%24))
filtered= data[
    (data['date/time'].dt.hour >=hora) & (data['date/time'].dt.hour <hora+1)
]
hist = np.histogram(filtered['date/time'].dt.minute,bins=60,range=(0,60))[0]
tabla=pd.DataFrame({'Minuto':range(60),"Choques":hist})
fig=px.bar(tabla,x='Minuto',y='Choques',hover_data=['Minuto','Choques'],height=400)
st.write(fig)
st.header('Top 5 calles más peligrosas por tipo')
select=st.selectbox('Tipo de afectado',['Peatones','Ciclistas','Motorizados'])

if select =='Peatones':
    st.write(original_data.query('injured_pedestrians >=1')[['on_street_name','injured_pedestrians']].sort_values(by=['injured_pedestrians'],ascending=False).dropna(how='any')[:5])
elif select =='Ciclistas':
    st.write(original_data.query('injured_cyclists >=1')[['on_street_name','injured_cyclists']].sort_values(by=['injured_cyclists'],ascending=False).dropna(how='any')[:5])
elif select =='Motorizados':
    st.write(original_data.query('injured_motorists >=1')[['on_street_name','injured_motorists']].sort_values(by=['injured_motorists'],ascending=False).dropna(how='any')[:5])



if st.checkbox("Mostrar",False):
    st.subheader('Raw Data')
    st.write(data)
