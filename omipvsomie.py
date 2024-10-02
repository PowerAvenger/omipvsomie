import streamlit as st
import datetime
import pandas as pd


#configuramos la web y cabecera
st.set_page_config(
    page_title="omipvsomie",
    page_icon=":bulb:",
    layout='wide',
    initial_sidebar_state='collapsed'
)
st.title('¿Bates a OMIP?')
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
    st.subheader("OMIP, OMIE según mes",divider='rainbow')
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

##DEFINIMOS LAYOUT PARA LA CLASIFICACIÓN GENERAL PORCENTAJE DESVIO
col10,col11=st.columns([.2,.8])
with col10:
    st.subheader("Clasificación #superporraomie2024",divider='rainbow')
    st.info('Pues aquí tenemos a los aspirantes a #MVPStarPower2024, ordenados de menor a mayor desvío eliminando los dos peores resultados.#',icon="ℹ️")
with col11:
    df_porra_desvios_porc, lista_starpower = obtener_clasificacion_porc()
    graf_clasificacion=grafico_clasificacion(df_porra_desvios_porc)
    st.write(graf_clasificacion)

col20,col21 = st.columns([.2,.8])
with col20:
    st.subheader("¿Bates a OMIP?",divider='rainbow')
    st.info('Ale, selecciona tu nombre y sabrás si bates a OMIP. Recuerda que se han eliminado tus dos peores resultados. Con OMIP se ha hecho exactamente lo mismo. La lista está ordenada alfabéticamente.',icon="ℹ️")
    lista_starpower_ordenada=sorted(lista_starpower)
    nombre_seleccionado=st.selectbox('Búscate',options=lista_starpower_ordenada)
    #df_comp_nombre_omip_melted = obtener_comparativa(nombre_seleccionado, df_porra_desvios_porc, df_omie_omip,meses_porra,entrega)
    df_omie_omip=obtener_datos_mes_anterior(df_FTB_mensual,df_FTB_mensual_entrega)
    
    #st.write(df_omie_omip)
    
    #df_entregas_24=pd.DataFrame(l_entregas_24)

    #st.write(entrega_seleccion)
    df_comp_nombre_omip_melted = obtener_comparativa(nombre_seleccionado, df_porra_desvios_porc, df_omie_omip,9,'sep 2024')
    #st.write(df_comp_nombre_omip_melted)
with col21:
    graf_comparativo=grafico_comparativo(df_comp_nombre_omip_melted,nombre_seleccionado)
    st.write(graf_comparativo)


