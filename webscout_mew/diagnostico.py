import sqlite3
import os

print("🔍 DIAGNÓSTICO DEFINITIVO EN LA WEB...\n")

db_path = 'instance/scoutmew.db'

if not os.path.exists(db_path):
    print(f"❌ ERROR: No se encuentra la base de datos en {db_path}")
else:
    try:
        conn = sqlite3.connect(db_path)
        cur = conn.cursor()

        # 1. Verificar el esquema de la tabla
        cur.execute("PRAGMA table_info(valoraciones)")
        columnas = [col[1] for col in cur.fetchall()]
        
        if 'precio_mercado' not in columnas:
            print("❌ ERROR FATAL: La columna 'precio_mercado' NO EXISTE en la base de datos local.")
        else:
            print("✅ La columna 'precio_mercado' existe en la base de datos local.")
            
            # 2. Consultar el dato real de Mbappé
            cur.execute("""
                SELECT j.nombre, j.temporada, v.valor_deportivo, v.precio_mercado
                FROM jugadores j
                JOIN valoraciones v ON j.id = v.jugador_id
                WHERE j.nombre LIKE '%Mbapp%' AND j.temporada = '2021'
            """)
            resultado = cur.fetchone()

            if resultado:
                print(f"\n📊 EXTRACCIÓN DE DATOS DE LA BD (instance/scoutmew.db):")
                print(f"   Jugador: {resultado[0]} ({resultado[1]})")
                print(f"   Valor Deportivo: {resultado[2]}")
                print(f"   Precio de Mercado: {resultado[3]}")

                if resultado[3] == 0 or resultado[3] is None:
                    print("\n⚠️ CONCLUSIÓN A: El HTML y app.py están bien. El problema es que el archivo .db copiado guardó un 0 o un Null en lugar de los millones.")
                else:
                    print("\n⚠️ CONCLUSIÓN B: La base de datos tiene los millones correctamente guardados. El problema está atrapado en app.py, SQLAlchemy o el Caché del navegador.")
            else:
                print("❌ No se encontró a Mbappé en la BD local.")

    except Exception as e:
        print(f"❌ Error leyendo BD: {e}")