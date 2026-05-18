import pandas as pd
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import random
import os

print("💸 Iniciando Minero de Transferencias (V3 - Filtro de Dinero Real)...")

# --- 1. CONFIGURACIÓN DE ARCHIVOS ---
archivo_jugadores = 'Scouting_Database_Final.csv' 
archivo_transferencias = 'Transferencias_DB.csv'  

try:
    df_base = pd.read_csv(archivo_jugadores)
    jugadores_unicos = df_base['Player'].unique().tolist()
except Exception as e:
    print(f"❌ Error al leer el archivo base: {e}")
    exit()

jugadores_procesados = []
if os.path.exists(archivo_transferencias):
    df_transfers = pd.read_csv(archivo_transferencias)
    if not df_transfers.empty:
        jugadores_procesados = df_transfers['Player'].unique().tolist()
    print(f"📂 Retomando: Se saltarán {len(jugadores_procesados)} jugadores ya procesados.")
else:
    print(f"📂 Iniciando base de transferencias desde cero.")
    columnas = ['Player', 'Season', 'Date', 'Left_Club', 'Joined_Club', 'Market_Value', 'Fee']
    pd.DataFrame(columns=columnas).to_csv(archivo_transferencias, index=False)

jugadores_pendientes = [j for j in jugadores_unicos if j not in jugadores_procesados]

print(f"📊 Jugadores pendientes de procesar: {len(jugadores_pendientes)}")
if not jugadores_pendientes:
    print("✅ ¡Todas las transferencias han sido extraídas!")
    exit()

# --- 2. NAVEGADOR ---
options = Options()

try:
    driver = webdriver.Firefox(options=options)
    driver.set_script_timeout(15)
except Exception as e:
    print(f"❌ Error al iniciar Firefox: {e}")
    exit()

primer_jugador_procesado = False

# --- FUNCIÓN DE FILTRADO (El Colador) ---
def es_transferencia_real(fee_str):
    if not fee_str: 
        return False
        
    fee_lower = str(fee_str).lower()
    
    # 1. Descartar si contiene palabras relacionadas a préstamos o fichajes libres
    palabras_basura = ['free', 'libre', 'cesión', 'cesion', 'loan', 'coste', 'cost', '-', '?']
    for palabra in palabras_basura:
        if palabra in fee_lower:
            return False
            
    # 2. Descartar si no contiene ningún número (ej. si dice "Desconocido")
    if not any(char.isdigit() for char in fee_lower):
        return False
        
    return True

# --- 3. BUCLE PRINCIPAL ---
for i, jugador in enumerate(jugadores_pendientes, 1):
    print(f"\n[{i}/{len(jugadores_pendientes)}] 🔍 Analizando fichajes de: {jugador}...")
    
    try:
        search_url = f"https://www.transfermarkt.com/schnellsuche/ergebnis/schnellsuche?query={jugador.replace(' ', '+')}"
        driver.get(search_url)
        
        try:
            WebDriverWait(driver, 2.5).until(EC.presence_of_element_located((By.CLASS_NAME, "items")))
        except:
            print("   ❌ No se encontró en la búsqueda.")
            pd.DataFrame([[jugador, 'N/A', 'N/A', 'N/A', 'N/A', 'N/A', 'N/A']]).to_csv(archivo_transferencias, mode='a', header=False, index=False)
            continue
            
        links = driver.find_elements(By.XPATH, "//table[@class='items']//td[@class='hauptlink']//a")
        if not links:
            print("   ❌ Jugador no encontrado.")
            pd.DataFrame([[jugador, 'N/A', 'N/A', 'N/A', 'N/A', 'N/A', 'N/A']]).to_csv(archivo_transferencias, mode='a', header=False, index=False)
            continue
            
        perfil_url = links[0].get_attribute('href')
        player_id = perfil_url.split('/')[-1]
        
        driver.get(perfil_url)
        
        if not primer_jugador_procesado:
            print("   ⏳ ESPERANDO 4 SEGUNDOS: Acepta las cookies si aparecen.")
            time.sleep(4)
            primer_jugador_procesado = True
            
        api_url = f"https://www.transfermarkt.com/ceapi/transferHistory/list/{player_id}"
        
        script_fetch = """
        var done = arguments[arguments.length - 1];
        fetch(arguments[0])
            .then(response => response.json())
            .then(data => done(data))
            .catch(err => done({'error_interno': err.message}));
        """
        
        datos = driver.execute_async_script(script_fetch, api_url)
        
        if not datos or 'error_interno' in datos:
            print(f"   ❌ Falló la API interna: {datos.get('error_interno', 'Desconocido')}")
            pd.DataFrame([[jugador, 'N/A', 'N/A', 'N/A', 'N/A', 'N/A', 'N/A']]).to_csv(archivo_transferencias, mode='a', header=False, index=False)
            continue
            
        historial = []
        if isinstance(datos, dict):
            if 'transfers' in datos:
                historial = datos['transfers']
            elif 'transferHistory' in datos:
                historial = datos['transferHistory']
            else:
                for k, v in datos.items():
                    if isinstance(v, list):
                        historial = v
                        break
        elif isinstance(datos, list):
            historial = datos
                    
        fichajes_jugador = []
        for t in historial:
            fee = str(t.get('fee', 'N/A'))
            
            # ¡AQUÍ APLICAMOS EL FILTRO!
            if not es_transferencia_real(fee):
                continue # Saltamos esta fila y pasamos a la siguiente transferencia
                
            season = t.get('season', 'N/A')
            date = t.get('date', 'N/A')
            
            old_c = t.get('from', {})
            old_club = old_c.get('clubName') if isinstance(old_c, dict) else t.get('oldClubName', 'N/A')
            
            new_c = t.get('to', {})
            new_club = new_c.get('clubName') if isinstance(new_c, dict) else t.get('newClubName', 'N/A')
            
            market_value = t.get('marketValue', 'N/A')
            
            fichajes_jugador.append([jugador, season, date, old_club, new_club, market_value, fee])
            
        # Guardado Inmediato
        if fichajes_jugador:
            df_nuevos = pd.DataFrame(fichajes_jugador)
            df_nuevos.to_csv(archivo_transferencias, mode='a', header=False, index=False)
            print(f"   💸 Se guardaron {len(fichajes_jugador)} traspasos reales históricos.")
        else:
            print("   ⚠️ No hubo traspasos con valor económico real. (Puro humo o canterano).")
            # Dejamos registro para no volver a buscarlo
            pd.DataFrame([[jugador, 'N/A', 'N/A', 'N/A', 'N/A', 'N/A', 'N/A']]).to_csv(archivo_transferencias, mode='a', header=False, index=False)

        time.sleep(random.uniform(0.6, 1.2))

    except Exception as e:
        print(f"   ❌ Error con {jugador}: {e}")
        time.sleep(3)

driver.quit()
print("\n✅ Extracción de transferencias depurada completada. Revisa Transferencias_DB.csv")