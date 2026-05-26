import sqlite3
import pandas as pd
import os

def clasificar_fichaje(svd, costo_real):
    """
    Clasifica la transferencia según la varianza entre el Algoritmo (SVD) y la Realidad.
    """
    desviacion = ((svd - costo_real) / costo_real) * 100
    
    if -15 <= desviacion <= 15:
        return "🟢 Categoría A: Tasación de Precisión", desviacion
    elif desviacion > 30:
        return "💎 Categoría B: Ineficiencia Explotada (Gema)", desviacion
    elif desviacion < -40:
        return "🔴 Categoría C: Riesgo de Sobreprecio (Burbuja)", desviacion
    elif desviacion > 15:
        return "🔵 Negocio Favorable (Leve Gema)", desviacion
    else: # Entre -40 y -15
        return "🟠 Ligero Sobreprecio", desviacion

def analizar_cohorte_traspasos():
    print("🔍 Iniciando Auditoría de Traspasos (Cohorte de Validación)...")
    
    db_path = 'scoutmew.db'
    if not os.path.exists(db_path):
        db_path = '../scoutmew.db' 
        if not os.path.exists(db_path):
            print("❌ Error: No se encontró scoutmew.db")
            return

    # 1. Extraer SOLO a los jugadores que SÍ fueron traspasados (coste_num > 0)
    conn = sqlite3.connect(db_path)
    query = """
    SELECT 
        j.nombre, 
        j.temporada, 
        v.rtg_principal, 
        v.valor_deportivo, 
        t.coste_num as costo_real,
        t.club_destino
    FROM jugadores j
    JOIN valoraciones v ON j.id = v.jugador_id
    -- Usamos INNER JOIN para descartar instantáneamente a los que no se movieron
    JOIN transferencias t ON j.nombre = t.jugador_nombre AND j.temporada = t.temporada
    WHERE t.coste_num > 0
    """
    df_traspasos = pd.read_sql_query(query, conn)
    conn.close()

    if df_traspasos.empty:
        print("⚠️ No se encontraron traspasos en la base de datos.")
        return

    reporte_final = []
    temporadas = sorted(df_traspasos['temporada'].unique())

    # 2. Embudo Invertido: Sacar a los mejores TRASPASADOS por temporada
    for temp in temporadas:
        df_temp = df_traspasos[df_traspasos['temporada'] == temp].copy()
        
        # Filtramos a los 68 mejores fichajes de esta temporada específica
        # (Si en alguna temporada necesitas 69 para llegar a 342, puedes cambiar el número aquí)
        top_traspasos_temp = df_temp.nlargest(68, 'rtg_principal')
        
        for _, row in top_traspasos_temp.iterrows():
            svd = row['valor_deportivo']
            costo = row['costo_real']
            
            categoria, desv_pct = clasificar_fichaje(svd, costo)
            
            reporte_final.append({
                'Temporada': temp,
                'Jugador': row['nombre'],
                'Destino': row['club_destino'],
                'RTG': round(row['rtg_principal'], 1),
                'SVD (€M)': round(svd / 1_000_000, 1),
                'Costo Real (€M)': round(costo / 1_000_000, 1),
                'Desviación %': round(desv_pct, 1),
                'Clasificación': categoria
            })

    # 3. Presentación de Resultados
    df_reporte = pd.DataFrame(reporte_final)
    
    # Si quieres forzar que la tabla final tenga exactamente 342 registros a nivel global 
    # en caso de que alguna temporada tuviera menos de 68 traspasos de élite:
    # df_reporte = df_reporte.nlargest(342, 'RTG')
    
    print(f"\n📊 Se aislaron exactamente {len(df_reporte)} transacciones de élite.\n")
    
    # Imprimir un conteo rápido de qué tan bien le fue al modelo
    print("--- RESUMEN DE CATEGORÍAS GERENCIALES ---")
    print(df_reporte['Clasificación'].value_counts().to_string())
    print("-" * 41)

    # Guardar el reporte en CSV
    archivo_salida = 'Auditoria_Traspasos_Elite.csv'
    df_reporte.to_csv(archivo_salida, index=False, encoding='utf-8')
    print(f"\n💾 Reporte detallado listo para tu tesis: {archivo_salida}")

if __name__ == '__main__':
    analizar_cohorte_traspasos()