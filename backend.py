# %%

import pandas as pd
#from datetime import datetime
#import datetime
import plotly.express as px
import plotly.graph_objects as go
import numpy as np


from omie import obtener_omie_mensual, obtener_omie_diario
from meff import obtener_FTB




# %% [markdown]
# ## OBTENEMOS DATOS DE OMIE

# %%
def obtener_omie():
    df_omie_mensual=obtener_omie_mensual()
    df_omie_diario=obtener_omie_diario()
    return df_omie_mensual,df_omie_diario

# %%
df_omie_mensual,df_omie_diario=obtener_omie()

# %% [markdown]
# ## dataframe de partida para Periodo = Mensual

# %%
def obtener_meff_mensual():
    
        df_FTB = obtener_FTB(web_meff=True)

        #filtramos por Periodo 'Mensual'
        df_FTB_mensual=df_FTB[df_FTB['Cod.'].str.startswith('FTBCM')]
        #hacemos copy del df
        df_FTB_mensual=df_FTB_mensual.copy()
        #añadimos columna con el mes de la fecha de negociación
        df_FTB_mensual['Mes_Fecha']=df_FTB_mensual['Fecha'].dt.month
        #añadimos columna con el mes de la fecha de entrega
        meses = {'ene': 1, 'feb': 2, 'mar': 3, 'abr': 4, 'may': 5, 'jun': 6, 
                'jul': 7, 'ago': 8, 'sep': 9, 'oct': 10, 'nov': 11, 'dic': 12}
        df_FTB_mensual['Mes_Entrega']=df_FTB_mensual['Entrega'].str[:3].map(meses)
        #modificamos el mes de entrega para poder restar
        df_FTB_mensual['Mes_Entrega'] = np.where((df_FTB_mensual['Mes_Fecha'] == 12) & (df_FTB_mensual['Mes_Entrega'] <= 12),
                                df_FTB_mensual['Mes_Entrega'] + 12,
                                df_FTB_mensual['Mes_Entrega'])

        # Filtrar las filas donde 'Entrega' contiene '24'
        l_entregas_24 = df_FTB_mensual[df_FTB_mensual['Entrega'].str.contains('24', na=False)]['Entrega'].unique().tolist()
        l_meses_unicos=df_FTB_mensual['Entrega'].unique().tolist()
        
        return df_FTB_mensual, meses, l_entregas_24,l_meses_unicos


# %%
def obtener_datos_mes_entrega(df_FTB_mensual,mes_entrega,entrega):
    ## ESTE DATAFRAME LO USAMOS PARA OBTENER UNA GRÁFICA DE OMIP PARA EL MES DE ENTREGA (MINIPORRA) DESDE 6 MESES ATRÁS

    #filtramos por el mes de entrega (miniporra) y por mes fecha (para evitar futuros dentro del mismo mes)
    df_FTB_mensual_entrega_menos1=df_FTB_mensual[(df_FTB_mensual['Mes_Entrega']==mes_entrega) & (df_FTB_mensual['Mes_Fecha']!=df_FTB_mensual['Mes_Entrega'])]
    df_FTB_mensual_entrega=df_FTB_mensual[df_FTB_mensual['Mes_Entrega']==mes_entrega] # & (df_FTB_mensual['Mes_Fecha']!=df_FTB_mensual['Mes_Entrega'])]
    
    #se usa simplemente para determinar la escala y del gráfico de area para los 3 ultimos valores
    #max_precio_entrega=df_FTB_mensual_entrega['Precio'].max()

    #dataframe con los 3 valores últimos para resaltarlos. USADOS PARA EL AREA DE LOS TRES ULTIMOS VALORES INCLUIDO EL MES DE ENTREGA
    df_FTB_mensual_entrega_last3=df_FTB_mensual_entrega.tail(3)
    #dataframe con los 3 valores últimos del mes anterior. USADOS PARA EL AREA DE LOS TRES ULTIMOS VALORES
    df_FTB_mensual_entrega_last3_menos1=df_FTB_mensual_entrega_menos1.tail(3)
    #media de omip
    omip_entrega=round(df_FTB_mensual_entrega_last3['Precio'].mean(),2)
    omip_entrega_menos1=round(df_FTB_mensual_entrega_last3_menos1['Precio'].mean(),2)

    #valor dinamico de omie para el mes de la miniporra (mes de entrega)
    df_omie_entrega=df_omie_mensual[df_omie_mensual['Entrega']==entrega]['omie']
    omie_entrega=df_omie_entrega.iloc[0]

    #PRIMER GRÁFICO DE DATOS. EVOLUCIÓN DE OMIP vs OMIE MEDIO
    graf_futuros=px.line(df_FTB_mensual_entrega, x='Fecha',y='Precio',
        labels={'Precio':'€/MWh'},
    )

    graf_futuros.update_traces(
        line=dict(color='sienna'),
        name='omip',
        showlegend=True
    )

    graf_futuros.update_xaxes(
        showgrid=True
    )

    graf_futuros.update_layout(
        title=dict(
            text=f'Evolución de OMIP para el mes de {entrega}.',
            x=.5,
            xanchor='center',
        ),
        xaxis=dict(
            rangeslider=dict(
                visible=True,
                bgcolor='rgba(173, 216, 230, 0.5)'
            ),  
            rangeselector=dict(
                buttons=list([
                    dict(count=1, label="1m", step="month", stepmode="backward"),
                    dict(count=6, label="6m", step="month", stepmode="backward"),
                    dict(step="all")  # Visualizar todos los datos
                ]),
                #visible=True
            )
        )
    )
    
    #añadimos rectangulo transparente con los tres precios últimos de OMIP incluido mes de entrega
    ancho=3
    graf_futuros.add_trace(
        go.Scatter(
            x=df_FTB_mensual_entrega_last3['Fecha'],
            y=[omip_entrega+ancho]*len(df_FTB_mensual_entrega_last3),
            mode='lines', 
            line=dict(color='rgba(255, 255, 204, 0.0)'),                   
            showlegend=False
        )
    )
    graf_futuros.add_trace(
        go.Scatter(
            x=df_FTB_mensual_entrega_last3['Fecha'],
            y=[omip_entrega-ancho]*len(df_FTB_mensual_entrega_last3), 
            fill='tonexty',
            mode='none',
            fillcolor='rgba(255, 255, 204, 0.2)',
            name='last 3',
            
        )
    )

    #añadimos rectangulo transparente con los tres precios últimos de OMIP
    graf_futuros.add_trace(
        go.Scatter(
            x=df_FTB_mensual_entrega_last3_menos1['Fecha'],
            y=[omip_entrega_menos1+ancho]*len(df_FTB_mensual_entrega_last3_menos1), 
            mode='lines',
            line=dict(color='rgba(255, 150, 150, 0.0)'),
            showlegend=False
            
        )
    )

    graf_futuros.add_trace(
        go.Scatter(
            x=df_FTB_mensual_entrega_last3_menos1['Fecha'],
            y=[omip_entrega_menos1-ancho]*len(df_FTB_mensual_entrega_last3_menos1), 
            fill='tonexty',
            mode='none',
            fillcolor='rgba(255, 150, 150, 0.2)',
            name='last3 M-1'
            
        )
    )




    ##AÑADIMOS VALOR MEDIO DE OMIE PARA EL MES SELECCIONADO
    graf_futuros.add_trace(
        go.Scatter(
            x=df_FTB_mensual_entrega['Fecha'],
            y=[omie_entrega]*len(df_FTB_mensual_entrega), #['Precio'],
            #fill='tozeroy',
            mode='lines',
            fillcolor='rgba(255, 150, 150, 0.2)',
            line=dict(dash='dot', color='green'),
            name='omie'
        )
    )
        
    return graf_futuros, omie_entrega, omip_entrega, omip_entrega_menos1, df_FTB_mensual_entrega

# %%
def omie_diario(df_omie_diario, entrega, omip_entrega):
    df_omie_diario_entrega=df_omie_diario[df_omie_diario['Entrega']==entrega]
    #omie_entrega=round(df_omie_diario_entrega['omie'].mean(),2)
    fecha_ini_entrega=df_omie_diario_entrega['datetime'].min()
    #código para obtener el último dia del mes a partir de la fecha primer dia
    fecha_fin_entrega=(fecha_ini_entrega+pd.DateOffset(months=1) - pd.DateOffset(days=1)).date()
    #creamos un df con los dias del mes de entrega
    df_rango_dias_entrega = pd.DataFrame({'datetime': pd.date_range(start=fecha_ini_entrega, end=fecha_fin_entrega)})
    df_omie_diario_entrega_rango=df_rango_dias_entrega.merge(df_omie_diario_entrega, on='datetime', how='left')
    df_omie_diario_entrega_rango['omip']=omip_entrega

    

    return df_omie_diario_entrega_rango

# %%
def obtener_datos_mes_anterior(df_FTB_mensual,df_FTB_mensual_entrega):
    #filtramos aquellos meses que sean justo uno menos que el mes de entrega
    #USAMOS EL DATAFRAME PARA OBTENER LOS ULTIMOS 3 VALORES DE CADA MES DE ENTREGA
    df_FTB_mensual_mes_anterior=df_FTB_mensual[df_FTB_mensual['Mes_Fecha']==df_FTB_mensual['Mes_Entrega']-1]
    #de cada mes, nos quedamos sólo con los valores de las últimas tres sesiones
    df_FTB_mensual_mes_anterior_last3=df_FTB_mensual_mes_anterior.groupby('Entrega').tail(3)
    #obtenemos la media de esos tres dias, por mes de entrega
    df_FTB_mensual_mes_anterior_last3=df_FTB_mensual_mes_anterior_last3.groupby('Entrega', as_index=False)['Precio'].mean().round(2)
    ## ORDENAMOS CRONOLÓGICAMENTE POR MES DE ENTREGA TIPO ene-24, feb-24 ...
    #lista de meses
    months_order = ['ene', 'feb', 'mar', 'abr', 'may', 'jun', 'jul', 'ago', 'sep', 'oct', 'nov', 'dic']
    #convertimos 'Entrega' en categoría para poder ordenar
    df_FTB_mensual_mes_anterior_last3['Entrega'] = pd.Categorical(df_FTB_mensual_mes_anterior_last3['Entrega'], categories=[f'{m}-{y}' for y in ['23', '24', '25'] for m in months_order], ordered=True)
    #esta es la lista ordenada con los meses de entrega y la media de MEFF de los últimos tres dias
    df_FTB_mensual_mes_anterior_last3_ordered = df_FTB_mensual_mes_anterior_last3.sort_values('Entrega').reset_index(drop=True)

    df_omie_omip=pd.merge(df_FTB_mensual_mes_anterior_last3_ordered,df_omie_mensual, on='Entrega',how='left')
    df_omie_omip=df_omie_omip.rename(columns={'Precio':'omip'})
    df_omie_omip['dif']=df_omie_omip['omie']-df_omie_omip['omip']
    df_omie_omip['dif%']=df_omie_omip['dif']/df_omie_omip['omie']
    df_omie_omip['dif%_abs']=df_omie_omip['dif%'].abs()

    graf_entrega=px.bar(df_omie_omip,x='Entrega',y=['omip','omie','dif'],
                    title='OMIP vs OMIE (€/MWh). OMIP a partir de los tres últimos registros del mes anterior',
                    labels={'value':'€/MWh', 'Entrega': 'Mes'},
                    text_auto=True,
                    barmode='group',
                    opacity=.75,
                    
                    color_discrete_map={'omip':'violet','omie':'orange'}
                    
                    )

    graf_entrega.update_layout(
        bargap=.3,
        title={'x':.5,'xanchor':'center'},
        legend={'title':''}
    )

    graf_entrega.update_traces(
        width=.2,
        textangle=0,
        #textfont=dict(bold=True)
    )


    df_omie_omip_ordenado=df_omie_omip.sort_values(by= 'dif%_abs',ascending=False)
    df_omip_desvios=df_omie_omip_ordenado.iloc[2:]
    desvio_omip=df_omip_desvios['dif%_abs'].sum()
    df_FTB_mensual_entrega_last3=df_FTB_mensual_entrega.groupby('Entrega').tail(3)
    df_FTB_mensual_entrega_last3
    media_last3=df_FTB_mensual_entrega_last3['Precio'].mean()
    
    media_last3
    
    return df_omie_omip

# %%
def grafico_omie_omip(df_omie_diario_entrega_rango,entrega):

    graf_omie_omip=px.line(df_omie_diario_entrega_rango, x='datetime',y='omie',
                        labels={'datetime':'fecha'},
                        )

    graf_omie_omip.update_traces(
        line=dict(color='green'),
        name='omie',
        showlegend=True,
        mode='lines+markers',
        marker=dict(symbol='square'),
        
    )

    graf_omie_omip.update_layout(
        title=dict(
            text=f'Evolución de OMIE para el mes de {entrega}. ',
            x=.5,
            xanchor='center',
            ),
        yaxis_title='€/MWh'
        )
        #legend_title_text='omip'


    graf_omie_omip.add_trace(
        go.Scatter(
            x=df_omie_diario_entrega_rango['datetime'],
            y=df_omie_diario_entrega_rango['omip'],
            #y=[omie_mensual_entrega]*len(df_FTB_mensual_entrega), #['Precio'],
            #fill='tozeroy',
            mode='lines',
            #fillcolor='rgba(255, 100, 100, 0.5)',
            line=dict(dash='dot', color='sienna'),
            name='omip'
        )
    )

    graf_omie_omip.update_yaxes(
        range=[0,df_omie_diario_entrega_rango['omie'].max()+10]
    )

    return graf_omie_omip

# %% [markdown]
# ## ACCEDEMOS A LA TABLA DE ACUMULADO PORCENTAJE DE LA EXCEL

# %%
def obtener_clasificacion_porc():
    #ruta_superporra= r'C:\Users\jovid\Documents\015 JOSE\070 ENERGIA\00001 PUBLICACIONES LINKEDIN\002 Miniporras\SUPERPORRA2024.xlsm'
    ruta_superporra='SUPERPORRA2024.xlsm'

    #cogemos la tabla acum_porc y las columnas A a M. CUIDADO CON ESTO A VER SI NOS QUEDAMOS CORTOS.
    df_porra_desvios_porc=pd.read_excel(ruta_superporra,sheet_name='acum_porc',usecols='A:N')

    #contamos los meses que llevamos jugando
    num_meses_porra=sum('24' in col for col in df_porra_desvios_porc.columns)

    #pasamos a numericos los datos de 'contar', para poder filtrar las que nos interesan
    df_porra_desvios_porc['contar'] = df_porra_desvios_porc['contar'].apply(pd.to_numeric, errors='coerce')
    #eliminamos aquellos participantes que llevan meses porra menos 2
    df_porra_desvios_porc=df_porra_desvios_porc[df_porra_desvios_porc['contar']>=num_meses_porra-2]
    #eliminamos espacios en los nombres de las columnas (por si acaso)
    df_porra_desvios_porc.columns = df_porra_desvios_porc.columns.str.strip()

    #creamos una lista con los nombres de las columnas de los meses del excel acum porc
    li_meses_porra = [col for col in df_porra_desvios_porc.columns if '24' in col]
    #obtenemos el último mes
    ultimo_mes_porra=li_meses_porra[-1]

    df_porra_desvios_porc=df_porra_desvios_porc.loc[:,['Nombre']+li_meses_porra]
    #convertimos los valores de los desvíos% de todos los meses en numericos
    df_porra_desvios_porc[li_meses_porra] = df_porra_desvios_porc[li_meses_porra].apply(pd.to_numeric, errors='coerce')

    def eliminar_valores_mas_altos(row):
        # Filtrar solo los valores válidos (no NaN)
        valores_validos = row.dropna()
        num_validos = len(valores_validos)
        
        # Definir cuántos valores eliminar
        if num_validos > num_meses_porra-2:
            # Calcular cuántos valores eliminar para dejar n-2
            eliminar_count = num_validos - (num_meses_porra-2)
            
            # Obtener los valores más altos a eliminar
            top_n = valores_validos.nlargest(eliminar_count)
            
            # Reemplazar esos valores con NaN
            return row.apply(lambda x: np.nan if x in top_n.values else x)
        else:
            # Si hay 7 o menos válidos, no eliminamos nada
            return row

    #eliminamos los valores más altos de cada participante
    df_porra_desvios_porc[li_meses_porra] = df_porra_desvios_porc[li_meses_porra].apply(eliminar_valores_mas_altos, axis=1)

    #añadimos columna con la suma y la media de los mejores resultados
    df_porra_desvios_porc['Suma'] = df_porra_desvios_porc.iloc[:, 1:].sum(axis=1, skipna=True)
    df_porra_desvios_porc['Media'] = df_porra_desvios_porc.iloc[:, 1:-1].mean(axis=1, skipna=True)
    #pasamos a numericos los valores de suma y media
    df_porra_desvios_porc[['Suma','Media']] = df_porra_desvios_porc[['Suma','Media']].apply(pd.to_numeric, errors='coerce')
    df_porra_desvios_porc=df_porra_desvios_porc.sort_values(by = 'Media')
    
    #generamos una lista de participantes
    lista_starpowers=df_porra_desvios_porc['Nombre'].unique().tolist()
    num_starpowers=len(lista_starpowers)

    return df_porra_desvios_porc, lista_starpowers, num_starpowers,ultimo_mes_porra


# %%
def grafico_clasificacion(df_porra_desvios_porc):
    graf_clasificacion=px.bar(df_porra_desvios_porc, x='Media',y='Nombre',
                            orientation='h',
                            height=800,
                            color='Media',
                            #color_continuous_scale='Viridis',
                            color_continuous_scale=px.colors.sequential.Electric_r,
                            text_auto=False,
                            labels={'Media':'Desvío medio'}
                            
                            )

    graf_clasificacion.update_layout(
        showlegend=False,
        margin=dict(l=250),
        bargap=.5
        
    )

    graf_clasificacion.update_yaxes(
        autorange="reversed",
        title='',
        tickfont=dict(size=16)
        )

    graf_clasificacion.update_traces(
        width=.7,
        texttemplate='%{x:.3f}', textposition='inside'
    )

    #graf_clasificacion.update_yaxes(
    #    tickfont=dict(size=16)
    #)

    return graf_clasificacion

# %%
def obtener_comparativa(nombre_seleccionado, df_porra_desvios_porc, df_omie_omip,num_meses_porra,entrega):
    
    #mini df con una fila que el nombre seleccionado
    df_nombre_seleccionado=df_porra_desvios_porc[df_porra_desvios_porc['Nombre']==nombre_seleccionado]

    #estos son los valores de los desvíos de OMIP frente a OMIE, por meses y en lista
    li_desvios_porc_omip = df_omie_omip['dif%_abs'].dropna().to_list()
    #print(li_desvios_porc_omip)
    li_desvios_porc_omip=li_desvios_porc_omip[:num_meses_porra]
    
    #esta fila se añade al nombre seleccionado
    li_desvios_porc_omip = ['omip'] + li_desvios_porc_omip +['']+['']
    #convertimos a dataframe
    df_desvios_porc_omip = pd.DataFrame([li_desvios_porc_omip], columns=df_nombre_seleccionado.columns)
    df_comp_nombre_omip=pd.concat([df_nombre_seleccionado,df_desvios_porc_omip], ignore_index=True)
    #localizamos las columnas del nombre con NaN
    columns_with_nan = df_comp_nombre_omip.iloc[0].isna()
    #Convertimos a NaN los valores de las columnas None del nombre
    #print(df_comp_nombre_omip)
    df_comp_nombre_omip.loc[1, columns_with_nan] = np.nan
    #print(df_comp_nombre_omip)
    df_comp_nombre_omip.iloc[:, 1:num_meses_porra] = df_comp_nombre_omip.iloc[:, 1:num_meses_porra].apply(pd.to_numeric, errors='coerce')
    df_comp_nombre_omip.loc[df_comp_nombre_omip['Nombre']=='omip','Suma'] = df_comp_nombre_omip.iloc[1, 1:num_meses_porra].sum(skipna=True)
    df_comp_nombre_omip.loc[df_comp_nombre_omip['Nombre']=='omip','Media'] = df_comp_nombre_omip.iloc[1, 1:num_meses_porra].mean(skipna=True)
    df_comp_nombre_omip[['Suma','Media']] = df_comp_nombre_omip[['Suma','Media']].apply(pd.to_numeric, errors='coerce')

    def calcular_suma_media(df, mes_inicio, mes_fin):
        # Seleccionar las columnas entre el mes de inicio y el mes de fin
        columnas_meses = df.columns.get_loc(mes_inicio),df.columns.get_loc(mes_fin) + 1
        #print (columnas_meses)
        df.loc[:,'Suma'] = df.iloc[:,columnas_meses[0]:columnas_meses[1]].sum(axis=1,skipna=True) 
        df.loc[:, 'Media'] = df.iloc[:, columnas_meses[0]:columnas_meses[1]].mean(axis=1, skipna=True)   # Crear nuevas columnas con la suma y la media ignorando los NaN
        columnas_a_conservar = ['Nombre']+list(df.columns[columnas_meses[0]:columnas_meses[1]]) + ['Suma', 'Media']
        df = df[columnas_a_conservar]
        return df, columnas_meses

    mes_inicio = 'ene-24'
    #entrega = 'Ago 2024'  
    #mes_fin = entrega.capitalize()

    
    df_comp_nombre_omip_din,columnas_meses = calcular_suma_media(df_comp_nombre_omip, mes_inicio, entrega)

    #obtenemos df para graficar en barras las comparativas mensuales, suma y media de los desvios en %
    #del jugador vs omip
    df_comp_nombre_omip_melted=df_comp_nombre_omip_din.melt(id_vars=['Nombre'],
                                          var_name='Mes',
                                          value_name='Valor')
    df_comp_nombre_omip_melted['Valor']=df_comp_nombre_omip_melted['Valor']*100
    df_comp_nombre_omip_melted['Valor']=df_comp_nombre_omip_melted['Valor'].round(1)
    #df_comp_nombre_omip_melted['media_texto'] = df_comp_nombre_omip_melted['Valor'].apply(lambda x: None if np.isnan(x) else x)
    df_comp_nombre_omip_melted['media_texto'] = df_comp_nombre_omip_melted['Valor'].apply(
        lambda x: str(x) if not np.isnan(x) else None
    )
    media_jugador=df_comp_nombre_omip_melted.iloc[-2,-2]
    media_omip=df_comp_nombre_omip_melted.iloc[-1,-2]
    df_comp_nombre_omip_melted = df_comp_nombre_omip_melted.drop(df_comp_nombre_omip_melted.index[-4:-2])
    return df_comp_nombre_omip_melted, media_jugador, media_omip


# %%
def grafico_comparativo(df_comp_nombre_omip_melted, nombre_seleccionado):

    graf_comp=px.bar(df_comp_nombre_omip_melted, x='Mes', y='Valor',
        color='Nombre',
        barmode='group',
        color_discrete_map={'omip':'violet',f'{nombre_seleccionado}':'orange'},
        text_auto=True,
        text='media_texto',
        labels={'Valor': 'Desvío en %'},
        #title=f'Comparativa de {nombre_seleccionado} contra OMIP',
        
    )   
    graf_comp.update_layout(
        bargap=.4,
        legend={'title':''},
        font=dict(color='white'),
        title=dict(
            text=f'Comparativa de {nombre_seleccionado} contra OMIP. Valores en %',
            x=.5,
            xanchor='center',
            )
        
    )
    graf_comp.update_traces(
        width=.2,
        textangle=0,
        
        #texttemplate='%{text:.2f}',  # Formato de los valores (2 decimales)
        textfont=dict(
            family='Arial, sans-serif',
                # Tipo de fuente
            #size=16,  # Tamaño de la fuente
            #color='black',  # Color de la fuente
            #weight='bold'  # Negrita
        ),
        textposition='outside'
    )

    for trace in graf_comp.data:
        trace.text = [t if t is not None else '' for t in trace.text]

    

    return graf_comp


def porra_evolution(df_porra_desvios_porc, nombre_seleccionado):
    # Convertir el dataframe de formato ancho a formato largo (necesario para el gráfico)
    df_melted = df_porra_desvios_porc.melt(id_vars='Nombre', var_name='Mes', value_name='Valor')
    # Crear un diccionario de meses para ordenarlos correctamente
    meses_ordenados = {
        'ene-24': 1, 'feb-24': 2, 'mar-24': 3, 'abr-24': 4, 'may-24': 5,
        'jun-24': 6, 'jul-24': 7, 'ago-24': 8, 'sep-24': 9, 'oct-24': 10
        }
    # Añadir columna para el orden de los meses
    df_melted['Mes_ordenado'] = df_melted['Mes'].map(meses_ordenados)

    #df_melted=df_melted.dropna()
    
    # Ordenar por Nombre y Mes para calcular la media acumulada
    df_melted = df_melted.sort_values(by=['Nombre', 'Mes_ordenado'])
    #eliminamos las filas suma y media. solo nos interesan los meses
    df_melted=df_melted[~df_melted['Mes'].isin(['Suma','Media'])]
    df_melted=df_melted.copy()

    #meses_completos = ['ene-24', 'feb-24', 'mar-24', 'abr-24', 'may-24', 'jun-24', 'jul-24', 'ago-24', 'sep-24', 'oct-24']
    df_melted['Media Acumulada'] = df_melted.groupby('Nombre')['Valor'].expanding().mean().reset_index(level=0,drop=True)
    df_melted=df_melted.sort_values(by='Mes_ordenado')
    

    # Crear un DataFrame para la animación
    df_animado = pd.DataFrame()

    # Agrupar por mes
    for mes in meses_ordenados:
        df_mes = df_melted[df_melted['Mes'] == mes].copy()
        # Ordenar por Media Acumulada
        df_mes = df_mes.sort_values(by='Media Acumulada')
        # Añadir una columna que represente el orden en ese mes
        df_mes['Orden'] = range(len(df_mes))
        
        # Agregar un mes a la animación
        df_animado = pd.concat([df_animado, df_mes], ignore_index=True)

    df_animado['color']=df_animado['Nombre'].apply(lambda x: 'red' if x==nombre_seleccionado else '')

    return df_animado

def animar_porra(df_animado):
    # Crear la animación del gráfico de barras horizontal
    fig2 = px.bar(df_animado,
                x='Media Acumulada',
                y='Nombre',
                #color='Nombre',
                #color='Media Acumulada',
                color='color',
                animation_frame='Mes',
                #range_x=[0, df_animado['Media Acumulada'].max()],
                orientation='h',
                #title='Evolución de la Media Acumulada de Jugadores por Mes',
                labels={'Nombre': 'Jugador', 'Media Acumulada': 'Media Acumulada'},
                height=800,
                color_continuous_scale=px.colors.sequential.Electric_r,
                color_discrete_map={'red':'red'}
    )
    # Ajustar el orden del eje Y por cada mes en el gráfico
    fig2.update_yaxes(categoryorder='total descending', title='Jugador')
    fig2.update_layout(yaxis_title='Jugador', 
                    xaxis_title='Media Acumulada', 
                    barmode='stack',
                    xaxis=dict(tickmode='linear', tickvals=list(range(0, int(df_animado['Media Acumulada'].max()) + 1))))
    
    


    fig2.update_layout(
        showlegend=False,
        margin=dict(l=250),
        bargap=.5
        
    )

    fig2.update_yaxes(
        #autorange="reversed",
        title='',
        tickfont=dict(size=16)
        )

    fig2.update_traces(
        width=.7,
        texttemplate='%{x:.3f}', textposition='inside'
    )
    return fig2