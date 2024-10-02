import pandas as pd
import datetime
import time
from pathlib import Path

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


def obtener_historicos():
    #obtenemos los históricos guardados
    df_historicos_FTB=pd.read_csv('historicos_FTB.csv',sep=';')
    ##LAS DOS LINEAS SIGUIENTES LAS USABA CON EL FORMATO INICIAL DE FECHA 01/01/2024 Y PRECIO SIN PUNTOS
    #df_historicos_FTB['Precio']=df_historicos_FTB['Precio']/100
    #df_historicos_FTB['Fecha']=pd.to_datetime(df_historicos_FTB['Fecha'], format='%d/%m/%Y')
    df_historicos_FTB['Fecha']=pd.to_datetime(df_historicos_FTB['Fecha'], format='%Y-%m-%d')
    #obtenemos la fecha del último registro
    ultimo_registro=df_historicos_FTB['Fecha'].max().date()
    
    return df_historicos_FTB, ultimo_registro

def obtener_param_meff(ultimo_registro):
    #OBTENEMOS LAS FECHAS DE INICIO Y FINAL PARA LA DESCARGA DE MEFF
    #datetime date
    fecha_fin=datetime.datetime.now().date()
    #str parámetro a pasar
    fecha_fin_meff=fecha_fin.strftime('%d/%m/%Y')
    #str parámetro a pasar
    fecha_ini_meff=(ultimo_registro+datetime.timedelta(days=1)).strftime('%d/%m/%Y')
    #OBTENEMOS LA RUTA PARA DESCARGAR MEFF
    #path
    ruta_app=Path.cwd()
    #convertido a str como parámetro def
    ruta_app_str=str(ruta_app)

    return ruta_app_str,fecha_ini_meff,fecha_fin_meff


def descargar_meff(ruta_app_str,fecha_ini_meff,fecha_fin_meff):

    # Configurar la descarga automática para archivos .xls
    chrome_options = webdriver.ChromeOptions()
    #la ruta debe ser en str
    prefs = {
        "download.default_directory": ruta_app_str, 
        "download.prompt_for_download": False,
        "download.directory_upgrade": True,
        "safebrowsing.enabled": True
        }
    chrome_options.add_experimental_option("prefs", prefs)
    #chrome_options.add_argument("--headless")
    #chrome_options.add_argument("--disable-gpu")
    #chrome_options.add_argument("--window-size=1920x1080")
    #chrome_options.add_argument("--no-sandbox")
    #chrome_options.add_argument("--disable-dev-shm-usage")


    driver = webdriver.Chrome(options=chrome_options)

    # Abrir la página web
    driver.get("https://www.meff.es/esp/Derivados-Commodities/Historico-Detalle")

    # Aceptar cookies
    try:
        aceptar_cookies = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.ID, 'onetrust-accept-btn-handler'))
            )
        aceptar_cookies.click()
    
    except Exception as e:
        print(f"Error al aceptar cookies: {e}")

    # Introducir las fechas en los campos "Desde" y "Hasta"
    try:
        # Esperar a que el campo "Desde" esté presente e introducir la fecha
        campo_desde = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.NAME, 'ctl00$ctl00$Contenido$Contenido$Desde$Desde_Fecha'))
        )
        campo_desde.clear() # Limpiar el campo antes de ingresar la fecha
        
        #fecha de inicio 
        campo_desde.send_keys(fecha_ini_meff) # Introduce la fecha "Desde" aquí

        # Esperar a que el campo "Hasta" esté presente e introducir la fecha
        campo_hasta = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.NAME, 'ctl00$ctl00$Contenido$Contenido$Hasta$Hasta_Fecha'))
        )
        campo_hasta.clear() # Limpiar el campo antes de ingresar la fecha

        #fecha de fin
        campo_hasta.send_keys(fecha_fin_meff) 

        # Hacer clic en el botón de búsqueda/descarga
        boton_descarga = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.NAME, 'ctl00$ctl00$Contenido$Contenido$Buscar'))
        )
        boton_descarga.click()

        # Esperar unos segundos para asegurarse de que la descarga se complete
        time.sleep(3)

    except Exception as e:
        print(f"Error al interactuar con los campos de fecha o al intentar descargar el archivo: {e}")

    # Cerrar el navegador
    driver.quit()

    ruta_archivo=Path(f'{ruta_app_str}\PreciosCierreDerEnergia.xls')
    if ruta_archivo.exists():
        try:
            df_datos_raw=pd.read_html(ruta_archivo)[0]
            #print(ruta_archivo)
            
            #filtramos codigo por FTB
            df_ftb_meff=df_datos_raw[df_datos_raw['Cod.'].str.startswith('FTB')]
            df_ftb_meff=df_ftb_meff.copy().reset_index(drop=True)
            #df_ftb_meff=pd.read_csv('PreciosCierreDerEnergia.xls',sep=';')
            df_ftb_meff['Precio']=df_ftb_meff['Precio']/100
            df_ftb_meff['Fecha']=pd.to_datetime(df_ftb_meff['Fecha'], format='%d/%m/%Y')
            ruta_archivo.unlink()
            return df_ftb_meff, True
        except Exception as e:
            return None, False
    else:
        return None, False

    



def obtener_FTB(web_meff):
    df_historicos_FTB, ultimo_registro=obtener_historicos()
    if web_meff:
        ruta_app_str,fecha_ini_meff,fecha_fin_meff=obtener_param_meff(ultimo_registro)
        df_ftb_meff, hay_datos=descargar_meff(ruta_app_str,fecha_ini_meff,fecha_fin_meff)
        #print(df_ftb_meff)
        
        if hay_datos:
            df_FTB=pd.concat([df_historicos_FTB,df_ftb_meff],ignore_index=True)
            df_FTB.to_csv('historicos_FTB.csv',sep=';',index=False)
        else:
            df_FTB=df_historicos_FTB
        
    else:
        df_FTB=df_historicos_FTB

    return df_FTB


#df_FTB = obtener_FTB(web_meff=True)
#print(df_FTB)

