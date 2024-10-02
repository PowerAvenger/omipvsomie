import streamlit as st
import requests
import pandas as pd


@st.cache_data(ttl=1000)
def download_esios_id(id,fecha_ini,fecha_fin,agrupacion):
        
        token = st.secrets['ESIOS_API_KEY']
        cab = dict()
        cab ['x-api-key']= token
        url_id = 'https://api.esios.ree.es/indicators'
        url=f'{url_id}/{id}?geo_ids[]=3&start_date={fecha_ini}T00:00:00&end_date={fecha_fin}T23:59:59&time_trunc={agrupacion}&time_agg=average'
        #print(url)
        datos_origen = requests.get(url, headers=cab).json()
        
        datos=pd.DataFrame(datos_origen['indicator']['values'])
        datos = (datos
            .assign(datetime=lambda vh_: pd #formateamos campo fecha, desde un str con diferencia horaria a un naive
                .to_datetime(vh_['datetime'],utc=True)  # con la fecha local
                .dt
                .tz_convert('Europe/Madrid')
                .dt
                .tz_localize(None)
                ) 
            )
        #dataframe con los valores horarios de las tecnologias
        #lo mezclamos con el spot horario
        df_spot=datos.copy()
        df_spot=df_spot.loc[:,['datetime','value']]
        #df_spot['fecha']=df_spot['datetime'].dt.date
        #df_spot['hora']=df_spot['datetime'].dt.hour
        df_spot['mes']=df_spot['datetime'].dt.month
        df_spot['año']=df_spot['datetime'].dt.year
        #df_spot.set_index('datetime', inplace=True)
        #df_spot['hora']+=1
        #df_spot['fecha'] = pd.to_datetime(df_spot['fecha']).dt.date
        df_spot=df_spot.rename(columns={'value':'omie'})
        df_spot['omie']=df_spot['omie'].round(2)
        
        return df_spot 


def obtener_omie_mensual():
        
    df_omie_mensual=download_esios_id('600','2024-01-01','2024-12-31','month')

    meses= {1: 'ene', 2: 'feb', 3: 'mar', 4: 'abr', 5: 'may', 6: 'jun', 7: 'jul', 8: 'ago', 9: 'sep', 10: 'oct', 11: 'nov', 12: 'dic'}
    
    df_omie_mensual['Entrega']=df_omie_mensual['mes'].map(meses)
    df_omie_mensual['Entrega']=df_omie_mensual['Entrega']+'-' +df_omie_mensual['año'].astype(str).str[-2:]

    return df_omie_mensual

def obtener_omie_diario():
        
    df_omie_diario=download_esios_id('600','2024-01-01','2024-12-31','day')

    meses= {1: 'ene', 2: 'feb', 3: 'mar', 4: 'abr', 5: 'may', 6: 'jun', 7: 'jul', 8: 'ago', 9: 'sep', 10: 'oct', 11: 'nov', 12: 'dic'}
    
    df_omie_diario['Entrega']=df_omie_diario['mes'].map(meses)
    df_omie_diario['Entrega']=df_omie_diario['Entrega']+'-' +df_omie_diario['año'].astype(str).str[-2:]
    df_omie_diario['dia']=df_omie_diario['datetime'].dt.day

    return df_omie_diario
    


