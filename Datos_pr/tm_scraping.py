import pandas as pd
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import random
import json
import os

print("🏭 Iniciando Minero Industrial (V11 - Procesamiento Masivo CSV)...")

# --- 1. CONFIGURACIÓN DE BASE DE DATOS ---
archivo_entrada = 'Scouting_Database_Final.csv'
archivo_salida = 'Scouting_Database_con_TM.csv'

# Si ya existe un archivo de progreso, lo cargamos para continuar donde nos quedamos
if os.path.exists(archivo_salida):
    print(f"📂 Archivo de progreso detectado: {archivo_salida}. Retomando...")
    df = pd.read_csv(archivo_salida)
else:
    print(f"📂 Iniciando desde cero con: {archivo_entrada}")
    df = pd.read_csv(archivo_entrada)
    # Creamos la columna TM_Value si no existe
    if 'TM_Value' not in df.columns:
        df['TM_Value'] = 0

# Obtenemos la lista de jugadores únicos que aún tienen TM_Value en 0 (para no repetir)
# Agrupamos por jugador y comprobamos si su suma de TM_Value es 0
jugadores_pendientes = df.groupby('Player')['TM_Value'].sum()
jugadores_unicos = jugadores_pendientes[jugadores_pendientes == 0].index.tolist()

print(f"📊 Jugadores únicos pendientes de procesar: {len(jugadores_unicos)}")

if len(jugadores_unicos) == 0:
    print("✅ ¡Toda la base de datos ya ha sido procesada!")
    exit()

# --- 2. CONFIGURACIÓN DEL NAVEGADOR ---
options = Options()
# options.add_argument('--headless') # Recomiendo no usar headless aún para vigilarlo

try:
    driver = webdriver.Firefox(options=options)
    driver.set_script_timeout(15)
    driver.set_window_size(1280, 800)
except Exception as e:
    print(f"❌ Error al iniciar Firefox: {e}")
    exit()

# Variable para controlar el primer aviso de cookies
primer_jugador_procesado = False

# --- 3. BUCLE PRINCIPAL (El motor de la fábrica) ---
for i, jugador in enumerate(jugadores_unicos, 1):
    print(f"\n[{i}/{len(jugadores_unicos)}] 🔍 Buscando a: {jugador}...")
    
    try:
        # PASO A: Búsqueda y Extracción del ID
        search_url = f"https://www.transfermarkt.com/schnellsuche/ergebnis/schnellsuche?query={jugador.replace(' ', '+')}"
        driver.get(search_url)
        
        try:
            WebDriverWait(driver, 6).until(EC.presence_of_element_located((By.CLASS_NAME, "items")))
        except:
            print(f"   ❌ No se encontró la tabla en TM. Marcando como no encontrado (-1).")
            # Marcamos con -1 para saber que lo buscamos pero falló, y no volver a buscarlo mañana
            df.loc[df['Player'] == jugador, 'TM_Value'] = -1
            df.to_csv(archivo_salida, index=False)
            continue
            
        links = driver.find_elements(By.XPATH, "//table[@class='items']//td[@class='hauptlink']//a")
        if not links:
            print(f"   ❌ Jugador no encontrado. Marcando como -1.")
            df.loc[df['Player'] == jugador, 'TM_Value'] = -1
            df.to_csv(archivo_salida, index=False)
            continue
            
        perfil_url = links[0].get_attribute('href')
        player_id = perfil_url.split('/')[-1]
        
        # PASO B: Calentar cookies (Solo si es el primer jugador)
        if not primer_jugador_procesado:
            driver.get(perfil_url)
            print("   ⏳ ESPERANDO 5 SEGUNDOS: Si sale el aviso de cookies, acéptalo AHORA.")
            time.sleep(5) 
            primer_jugador_procesado = True
        
        # PASO C: El Caballo de Troya (Fetch)
        api_url = f"https://tmapi-alpha.transfermarkt.technology/player/{player_id}/market-value-history"
        
        script_fetch = """
        var done = arguments[arguments.length - 1];
        var url = arguments[0];
        fetch(url)
            .then(response => response.json())
            .then(data => done(data))
            .catch(err => done({'error_interno': err.message}));
        """
        
        datos = driver.execute_async_script(script_fetch, api_url)
        
        if not datos or 'error_interno' in datos:
            print(f"   ❌ Falló el fetch interno. Marcando como -1.")
            df.loc[df['Player'] == jugador, 'TM_Value'] = -1
            continue
            
        historial = datos.get('data', {}).get('history', [])
        if not historial:
            print("   ⚠️ Sin historial. Marcando como -1.")
            df.loc[df['Player'] == jugador, 'TM_Value'] = -1
            df.to_csv(archivo_salida, index=False)
            continue

        # Convertimos el historial a un diccionario fácil de usar {Temporada: Valor_Máximo}
        precios_por_temporada = {}
        for item in historial:
            szn = item.get('seasonId')
            valor = item.get('marketValue', {}).get('value', 0)
            
            # Si un jugador cambia de precio varias veces en un año, nos quedamos con el último/más alto
            precios_por_temporada[szn] = valor

        # PASO D: Inyectar datos en TODAS las filas de ese jugador en el CSV
        filas_actualizadas = 0
        for index, row in df[df['Player'] == jugador].iterrows():
            temporada_csv = row['Szn']
            
            if temporada_csv in precios_por_temporada:
                precio_encontrado = precios_por_temporada[temporada_csv]
                df.at[index, 'TM_Value'] = precio_encontrado
                filas_actualizadas += 1
            else:
                # Si no hay dato exacto de esa temporada, buscamos el valor más cercano hacia atrás
                temporadas_pasadas = [s for s in precios_por_temporada.keys() if s <= temporada_csv]
                if temporadas_pasadas:
                    temp_mas_cercana = max(temporadas_pasadas)
                    df.at[index, 'TM_Value'] = precios_por_temporada[temp_mas_cercana]
                    filas_actualizadas += 1
                else:
                    df.at[index, 'TM_Value'] = -1 # No había ni nacido futbolísticamente

        print(f"   ✅ ¡Éxito! Se actualizaron {filas_actualizadas} filas de {jugador}.")
        
        # PASO E: Guardado de Seguridad
        df.to_csv(archivo_salida, index=False)
        
        # PASO F: Pausa de humano para no ser baneados
        pausa = random.uniform(2.5, 4.5)
        time.sleep(pausa)

    except Exception as e:
        print(f"   ❌ Error inesperado con {jugador}: {e}")
        time.sleep(5) # Pausa larga si hay error antes de seguir

driver.quit()
print("\n🎉 Misión Masiva Completada. Revisa el archivo Scouting_Database_con_TM.csv")