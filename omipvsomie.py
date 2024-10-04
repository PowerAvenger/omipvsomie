import streamlit as st
import datetime
import base64
import time


#configuramos la web y cabecera
st.set_page_config(
    page_title="omipvsomie",
    page_icon=":bulb:",
    layout='wide',
    initial_sidebar_state='collapsed'
)
st.title('Superporrero: ¿Bates a OMIP?')
st.caption("Copyright by Jose Vidal :ok_hand:")
url_apps = "https://powerappspy-josevidal.streamlit.app/"
st.write("Visita mi mini-web de [PowerAPPs](%s) con un montón de utilidades." % url_apps)
url_linkedin = "https://www.linkedin.com/posts/jfvidalsierra_powerapps-activity-7216715360010461184-YhHj?utm_source=share&utm_medium=member_desktop"
st.write("Deja tus comentarios y propuestas en mi perfil de [Linkedin](%s)." % url_linkedin)

from backend import obtener_meff_mensual, obtener_datos_mes_entrega, omie_diario, grafico_omie_omip, obtener_clasificacion_porc, grafico_clasificacion, obtener_comparativa, grafico_comparativo,obtener_datos_mes_anterior

hoy=datetime.datetime.now().date()
mes_hoy=hoy.month



#obtenemos la lista de meses 2024 en formato 'sep-24' y la lista de meses en formato ene : 1
df_FTB_mensual, meses, l_entregas_24,l_meses_unicos=obtener_meff_mensual()


##DEFINIMOS PRIMER GRUPO DE COLUMNAS PARA LOS 2 GRÁFICOS INICIALES
col1,col2,col3=st.columns([.2,.4,.4])
with col1:
    st.subheader("1. OMIP vs OMIE.",divider='rainbow')
    st.info('Para el mes seleccionado, vas a visualizar los valores de OMIP de los últimos seis meses. Para calcular su media y compararla con OMIE, sólo tomamos los tres últimos valores.',icon="ℹ️")
    #selector de meses que nos devuelve el mes de entrega en formato 'ene-24'
    lista_options=l_entregas_24[:mes_hoy]
    entrega_seleccion=st.selectbox('Selecciona el mes a visualizar', options=lista_options,index=mes_hoy-1)
    
    #obtenemos el número de mes correspondiente
    entrega_seleccion_recortado=entrega_seleccion[:3]
    mes_entrega_seleccion=meses[entrega_seleccion_recortado]

    #obtenemos los datos resumen de omip omie y otros df y graf
    graf_futuros, omie_entrega, omip_entrega, df_FTB_mensual_entrega=obtener_datos_mes_entrega(df_FTB_mensual, mes_entrega_seleccion, entrega_seleccion)
    df_omie_diario_entrega_rango=omie_diario(entrega_seleccion, omip_entrega)
    #fecha_ultimo_registro=ultimo_registro.strftime("%d.%m.%Y")
    #hora_ultimo_registro=ultimo_registro.strftime("%H:%M")
    col101,col102,col103=st.columns(3)
    with col101:
        st.metric('OMIP',value=omip_entrega)
    with col102:
        st.metric('OMIE',value=omie_entrega)
    with col103:
        dif_omip_omie=round(omip_entrega-omie_entrega,2)
        delta_dif=round((dif_omip_omie/omie_entrega)*100,2)
        st.metric('Diferencia', value=dif_omip_omie,delta=f'{delta_dif}%')   
with col2:
    st.write (graf_futuros)
with col3:     
    graf_omie_omip=grafico_omie_omip(df_omie_diario_entrega_rango, entrega_seleccion)
    st.write(graf_omie_omip)



#DEFINIMOS LAYOUT PARA LA COMPARATIVA JUGADOR - OMIP
df_omie_omip=obtener_datos_mes_anterior(df_FTB_mensual,df_FTB_mensual_entrega)
df_porra_desvios_porc, lista_starpowers, num_starpowers,ultimo_mes_porra = obtener_clasificacion_porc()
col20,col21 = st.columns([.2,.8])
with col20:
    st.subheader("2. Y tú, ¿bates a OMIP?",divider='rainbow')
    st.info('Superporrero: Selecciona tu nombre y sabrás si bates a OMIP en la lucha por el **MVPStarPower2024**. Recuerda que se han eliminado tus dos peores resultados. Con OMIP se ha hecho exactamente lo mismo. La lista está ordenada alfabéticamente.',icon="ℹ️")
    lista_starpowers_ordenada=sorted(lista_starpowers)
    lista_starpowers_ordenada.insert(0,'')

    nombre_seleccionado=st.selectbox('Búscate',options=lista_starpowers_ordenada)
    df_comp_nombre_omip_melted, media_jugador, media_omip = obtener_comparativa(nombre_seleccionado, df_porra_desvios_porc, df_omie_omip,num_starpowers,ultimo_mes_porra)
    if nombre_seleccionado!='':
        #df_comp_nombre_omip_melted, media_jugador, media_omip = obtener_comparativa(nombre_seleccionado, df_porra_desvios_porc, df_omie_omip,num_starpowers,ultimo_mes_porra)
        dif_jugador_omip=round(media_jugador-media_omip,1)
        #dif_jugador_omip
        if dif_jugador_omip<0: #gana jugador

            def autoplay_audio(file_path: str):
                st.balloons()
                with open(file_path, "rb") as f:
                    data = f.read()
                    b64 = base64.b64encode(data).decode()
                    md = f"""
                        <audio autoplay="true">
                        <source src="data:audio/mp3;base64,{b64}" type="audio/mp3">
                        </audio>
                        """
                    st.markdown(
                        md,
                        unsafe_allow_html=True,
                    )

            autoplay_audio("Niños.mp3")
           
            st.balloons()
        
        col201,col202,col203=st.columns(3)
        with col201:
            st.metric('Media OMIP', value=f'{media_omip}%')
            
        with col202:
            st.metric('Media jugador',value=f'{media_jugador}%', delta=f'{dif_jugador_omip}%', delta_color='inverse')
        #with col203:
        #    st.metric('Dif', value = dif_jugador_omip)
with col21:
    #if nombre_seleccionado!='':
        graf_comparativo=grafico_comparativo(df_comp_nombre_omip_melted,nombre_seleccionado)
        st.write(graf_comparativo)
        #st.write(df_comp_nombre_omip_melted)


#DEFINIMOS LAYOUT PARA LA CLASIFICACIÓN GENERAL PORCENTAJE DESVIO

col10,col11=st.columns([.2,.8])
with col10:
    st.subheader("Clasificación #superporraomie2024",divider='rainbow')
    st.info('Pues aquí tenemos a los aspirantes a #MVPStarPower2024, ordenados de menor a mayor desvío medio en porcentaje y tras eliminar los dos peores resultados de cada participantes.',icon="ℹ️")
    st.metric('Num. StarPowers', num_starpowers)
with col11:
    
    graf_clasificacion=grafico_clasificacion(df_porra_desvios_porc)
    st.write(graf_clasificacion)
    #st.write(df_porra_desvios_porc)