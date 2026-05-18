import sqlite3
import pandas as pd

print("🔍 INICIANDO DIAGNÓSTICO DE LA TUBERÍA DE DATOS...\n")

# 1. Revisar el archivo de origen (CSV)
try:
    df = pd.read_csv('Scouting_Database_con_TM.csv')
    columnas = df.columns.tolist()
    print("📄 1. REVISIÓN DEL CSV ORIGINAL:")
    
    # Buscamos cómo se llama realmente la columna de dinero
    cols_mercado = [c for c in columnas if 'market' in c.lower() or 'valor' in c.lower() or 'value' in c.lower() or 'precio' in c.lower()]
    print(f"   Columnas relacionadas con dinero encontradas: {cols_mercado}")
    
    # Intentamos ver qué dato crudo tiene Mbappé
    mbappe_row = df[df['Player'].str.contains('Mbapp', case=False, na=False)].iloc[0]
    col_correcta = cols_mercado[0] if cols_mercado else "Ninguna"
    print(f"   Dato crudo de Mbappé en la columna '{col_correcta}': {mbappe_row.get(col_correcta, 'No encontrado')}")
    
except Exception as e:
    print(f"   ❌ Error leyendo CSV: {e}")

# 2. Revisar la Base de Datos (SQLite)
try:
    print("\n🗄️ 2. REVISIÓN DE LA BASE DE DATOS (scoutmew.db):")
    # Nos conectamos a tu base de datos en la carpeta instance
    conn = sqlite3.connect('instance/scoutmew.db')
    cur = conn.cursor()
    
    # Buscamos a Mbappé cruzando la tabla de jugadores y valoraciones
    cur.execute("""
        SELECT j.nombre, j.temporada, v.precio_mercado 
        FROM jugadores j 
        JOIN valoraciones v ON j.id = v.jugador_id 
        WHERE j.nombre LIKE '%Mbapp%' AND j.temporada = '2021'
    """)
    resultado = cur.fetchone()
    
    if resultado:
        print(f"   Registro encontrado -> Nombre: {resultado[0]} | Temporada: {resultado[1]} | Precio guardado: {resultado[2]}")
    else:
        print("   ⚠️ No se encontró a Mbappé en la temporada 2021 en la BD.")
        
except Exception as e:
    print(f"   ❌ Error leyendo Base de Datos: {e}")