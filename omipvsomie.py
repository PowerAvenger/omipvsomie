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

from backend import obtener_omie, obtener_meff_mensual, obtener_datos_mes_entrega, omie_diario, grafico_omie_omip, obtener_clasificacion_porc, grafico_clasificacion, obtener_comparativa, grafico_comparativo,obtener_datos_mes_anterior, animar_porra, porra_evolution

hoy=datetime.datetime.now().date()
mes_hoy=hoy.month

def autoplay_audio(file_path: str):
                
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


if 'download_meff' not in st.session_state:
    st.session_state.download_meff=False
    #obtenemos la lista de meses 2024 en formato 'sep-24' y la lista de meses en formato ene : 1
    #df_FTB_mensual, meses, l_entregas_24,l_meses_unicos=obtener_meff_mensual(st.session_state.download_meff)
    #df_omie_mensual,df_omie_diario=obtener_omie()
#if 'password_verified' not in st.session_state:
#    st.session_state.password_verified = False
#    st.session_state.download_meff=False

#obtenemos la lista de meses 2024 en formato 'sep-24' y la lista de meses en formato ene : 1
df_FTB_mensual, meses, l_entregas_24,l_meses_unicos=obtener_meff_mensual(st.session_state.download_meff)
df_omie_mensual,df_omie_diario=obtener_omie()

def actualiza_meff(password):
    if password=='josepass':
                
                st.session_state.download_meff=True
                df_FTB_mensual, meses, l_entregas_24,l_meses_unicos=obtener_meff_mensual(st.session_state.download_meff)
                st.session_state.download_meff=False
    return



##DEFINIMOS PRIMER GRUPO DE COLUMNAS PARA LOS 2 GRÁFICOS INICIALES
col1,col2,col3=st.columns([.2,.4,.4])
#columna pequeña de la izquierda con datos resumen
with col1:
    st.subheader("1. OMIP vs OMIE.",divider='rainbow')
    st.info('Para el mes seleccionado, vas a visualizar los valores de OMIP de los últimos seis meses. Para calcular su media y compararla con OMIE, sólo tomamos los tres últimos valores.',icon="ℹ️")
    #selector de meses que nos devuelve el mes de entrega en formato 'ene-24'
    lista_options=l_entregas_24[:mes_hoy]
    col1001,col1002 = st.columns(2)
    with col1001:
        entrega_seleccion=st.selectbox('Selecciona el mes a visualizar', options=lista_options,index=mes_hoy-1)
    
            
            #if password=='josepass':
            #    st.session_state.download_meff=True
            #    df_FTB_mensual, meses, l_entregas_24,l_meses_unicos=obtener_meff_mensual(st.session_state.download_meff)
            #    st.session_state.download_meff=False
            #    st.success('Descarga autorizada. Actualizando datos...', icon="✅")
            #        #st.rerun()
            #elif password:
            #        st.error('Contraseña incorrecta.',icon="🚫")
            #else:
                #st.success('Contraseña ya verificada. Datos actualizados.', icon="✅")
                
    #obtenemos el número de mes correspondiente
    entrega_seleccion_recortado=entrega_seleccion[:3]
    
    mes_entrega_seleccion=meses[entrega_seleccion_recortado]

    #obtenemos los datos resumen de omip omie y otros df y graf
    graf_futuros, omie_entrega, omip_entrega, omip_entrega_menos1, df_FTB_mensual_entrega=obtener_datos_mes_entrega(df_FTB_mensual, mes_entrega_seleccion, entrega_seleccion)
    df_omie_diario_entrega_rango=omie_diario(df_omie_diario,entrega_seleccion, omip_entrega)
    
    #primera fila de indicadores
    col101,col102,col103=st.columns(3)
    with col101:
        st.metric('OMIE media',value=omie_entrega)
        
        
    with col102:
        st.metric('OMIP (mes anterior)',value=omip_entrega_menos1,help='Valor medio de OMIP de los últimos tres dias del mes anterior. Valor estático y usado en las siguientes secciones como referencia.')
        #st.metric('OMIP (mes en curso)',value=omip_entrega)
    with col103:
        dif_omipm1_omie=round(omip_entrega_menos1-omie_entrega,2)
        delta_dif_m1=round((dif_omipm1_omie/omie_entrega)*100,2)
        st.metric('Diferencia', value=dif_omipm1_omie,delta=f'{delta_dif_m1}%')

    #segunda fila de indicadores    
    col111,col112,col113=st.columns(3)
    with col111:
        with st.popover('Actualizar OMIP'):
            st.markdown('⚠️ ¡Sólo autorizados! ⚠️')
            #if not st.session_state.password_verified:
            password=st.text_input('Introduce la contraseña',type='password')
            actualiza_password=st.button('Confirmar',on_click=actualiza_meff(password))
        
    with col112:
        #st.metric('OMIP (mes anterior)',value=omip_entrega_menos1)
        st.metric('OMIP (mes en curso)',value=omip_entrega, help='Valor medio de OMIP de los tres últimos días disponibles durante el mes en curso. Es un valor dinámico.')
    with col113:
        #dif_omipm1_omie=round(omip_entrega_menos1-omie_entrega,2)
        #delta_dif_m1=round((dif_omipm1_omie/omie_entrega)*100,2)
        #st.metric('Diferencia', value=dif_omipm1_omie,delta=f'{delta_dif_m1}%')
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
        
        dif_jugador_omip=round(media_jugador-media_omip,1)
        
        if dif_jugador_omip < 0: #gana jugador

            if 'nombre_seleccionado_anterior' not in st.session_state:
                st.session_state.nombre_seleccionado_anterior=None
            if st.session_state.nombre_seleccionado_anterior !=nombre_seleccionado:
                #st.balloons()
                autoplay_audio("Niños.mp3")
                st.balloons()

                st.session_state.nombre_seleccionado_anterior= nombre_seleccionado

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
    st.subheader("3. Clasificación #superporraomie2024",divider='rainbow')
    st.info('Pues aquí tenemos a los aspirantes a #MVPStarPower2024, ordenados de menor a mayor desvío medio en porcentaje y tras eliminar los dos peores resultados de cada participantes. ¡Hasta puedes ver tu evolución si en el paso anterior te has seleccionado!',icon="ℹ️")
    st.metric('Num. StarPowers', num_starpowers)
    on = st.toggle('Superporra Evolution')
with col11:
    
    if on:
        df_animado=porra_evolution(df_porra_desvios_porc,nombre_seleccionado)
        balloons=False
        fig2=animar_porra(df_animado)
        st.write(fig2)    
    else:
        graf_clasificacion=grafico_clasificacion(df_porra_desvios_porc)
        st.write(graf_clasificacion)
    
