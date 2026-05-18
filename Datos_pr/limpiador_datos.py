import pandas as pd
import re

print("🧼 Iniciando la Lavadora de Datos Financieros...")

archivo_entrada = 'Transferencias_DB.csv'
archivo_salida = 'Transferencias_DB_Limpio.csv'

# Función matemática para convertir texto a número puro
def limpiar_dinero(valor):
    # Si está vacío o es un texto inválido, devolvemos 0
    if pd.isna(valor) or valor == 'N/A' or valor == '-' or valor == '?':
        return 0
        
    # Convertimos a minúsculas y quitamos el símbolo de euro y espacios
    valor_str = str(valor).lower().replace('€', '').replace(' ', '')
    
    # Algunos sistemas europeos usan coma para decimales (ej. 1,50m), lo pasamos a punto
    valor_str = valor_str.replace(',', '.')
    
    # Extraemos solo la parte numérica usando Expresiones Regulares
    numeros = re.findall(r"[-+]?\d*\.\d+|\d+", valor_str)
    
    if not numeros:
        return 0
        
    cantidad = float(numeros[0])
    
    # Multiplicador lógico
    if 'm' in valor_str:
        return int(cantidad * 1000000)
    elif 'k' in valor_str:
        return int(cantidad * 1000)
    else:
        return int(cantidad) # Por si algún dato ya venía limpio

try:
    # 1. Cargamos el CSV
    df = pd.read_csv(archivo_entrada)
    print(f"📊 Archivo cargado con {len(df)} transferencias.")
    
    # 2. Aplicamos la lavadora a las columnas de dinero
    print("⚙️ Limpiando columna: Market_Value...")
    df['Market_Value_Num'] = df['Market_Value'].apply(limpiar_dinero)
    
    print("⚙️ Limpiando columna: Fee...")
    df['Fee_Num'] = df['Fee'].apply(limpiar_dinero)
    
    # 3. Guardamos el resultado (dejamos las columnas originales por si quieres revisarlas)
    df.to_csv(archivo_salida, index=False)
    print(f"✅ ¡Éxito! Archivo guardado como {archivo_salida}.")
    
except FileNotFoundError:
    print(f"❌ Error: No se encontró el archivo {archivo_entrada}.")
except Exception as e:
    print(f"❌ Error inesperado: {e}")