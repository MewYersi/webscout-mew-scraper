import pandas as pd
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import os
import re

def limpiar_dinero(valor):
    if pd.isna(valor) or str(valor) == '0' or valor == 'N/A' or valor == '-' or valor == '?':
        return 0
    valor_str = str(valor).lower().replace('€', '').replace(' ', '').replace(',', '.')
    numeros = re.findall(r"[-+]?\d*\.\d+|\d+", valor_str)
    if not numeros: return 0
    cantidad = float(numeros[0])
    if 'm' in valor_str: return int(cantidad * 1000000)
    elif 'k' in valor_str: return int(cantidad * 1000)
    else: return int(cantidad)
# ==========================================
# 1. CONFIGURACIÓN INICIAL Y MODELOS
# ==========================================
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///scoutmew.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class Jugador(db.Model):
    __tablename__ = 'jugadores'
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False, index=True) # Indexado para cruzar datos rápido
    nacion = db.Column(db.String(10))
    edad = db.Column(db.Integer)
    club = db.Column(db.String(100))
    posicion = db.Column(db.String(10))
    minutos = db.Column(db.Integer)
    liga = db.Column(db.String(50))      
    temporada = db.Column(db.String(20)) 

class Valoracion(db.Model):
    __tablename__ = 'valoraciones'
    id = db.Column(db.Integer, primary_key=True)
    jugador_id = db.Column(db.Integer, db.ForeignKey('jugadores.id'))
    rol_principal = db.Column(db.String(20))
    rtg_principal = db.Column(db.Float)
    valor_deportivo = db.Column(db.Float)
    precio_mercado = db.Column(db.Integer) # ¡Añadido! Valor en euros de esa temporada
    rol_2 = db.Column(db.String(20))
    rtg_2 = db.Column(db.Float)
    rol_3 = db.Column(db.String(20))
    rtg_3 = db.Column(db.Float)

class EstadisticasFBref(db.Model):
    __tablename__ = 'estadisticas_fbref'
    id = db.Column(db.Integer, primary_key=True)
    jugador_id = db.Column(db.Integer, db.ForeignKey('jugadores.id'))
    datos_crudos = db.Column(db.JSON)

# NUEVA TABLA: Historial Financiero
class Transferencia(db.Model):
    __tablename__ = 'transferencias'
    id = db.Column(db.Integer, primary_key=True)
    # Lo vinculamos por nombre porque un jugador tiene múltiples temporadas, 
    # pero es la misma persona física.
    jugador_nombre = db.Column(db.String(100), index=True) 
    temporada = db.Column(db.String(20))
    fecha = db.Column(db.String(20))
    club_origen = db.Column(db.String(100))
    club_destino = db.Column(db.String(100))
    coste_texto = db.Column(db.String(20)) # Ej. "€35.00m"
    coste_num = db.Column(db.Integer)      # Ej. 35000000

# ==========================================
# 2. PROCESO DE MIGRACIÓN MAESTRA
# ==========================================
def migrar_datos():
    csv_maestro = 'Scouting_Database_con_TM.csv'
    csv_fichajes = 'Transferencias_DB_Limpio.csv'
    
    if not os.path.exists(csv_maestro):
        print(f"❌ Error: No encuentro el archivo maestro {csv_maestro}")
        return

    with app.app_context():
        print("🏗️ Destruyendo base de datos antigua y creando la nueva arquitectura...")
        db.drop_all()
        db.create_all()

        # --- FASE 1: MIGRACIÓN DE RENDIMIENTO Y VALOR DE MERCADO ---
        print(f"\n📊 [1/2] Cargando Base de Datos Maestra de Europa ({csv_maestro})...")
        df_maestro = pd.read_csv(csv_maestro)
        df_maestro = df_maestro.fillna(0)

        # Metadatos que no deben ir al JSON (ajusta si tienes columnas nuevas en tu CSV)
        columnas_metadata = ['Valor_Deportivo', 'Rol_Principal', 'RTG_Principal', 'Rol_2', 'RTG_2', 'Rol_3', 'RTG_3', 'Rank', 'TM_Value']
        
        print(f"🚀 Migrando {len(df_maestro)} temporadas de jugadores...")
        
        for index, row in df_maestro.iterrows():
            nuevo_jugador = Jugador(
                nombre=row['Player'],
                nacion=row['Nation'],
                edad=int(row['Age']),
                club=row['Squad'],
                posicion=row['Pos'],
                minutos=int(row['Min']),
                liga=row['League'],
                temporada=str(row['Szn'])
            )
            db.session.add(nuevo_jugador)
            db.session.flush() # Obtenemos el ID temporalmente sin hacer el commit completo
            
            # Intenta obtener el Market_Value si existe, si no, guarda 0
            # Si en tu CSV se llama distinto, cambia 'Market_Value' por tu nombre de columna
            precio_final = limpiar_dinero(row.get('TM_Value', 0))

            nueva_valoracion = Valoracion(
                jugador_id=nuevo_jugador.id,
                rol_principal=row['Rol_Principal'],
                rtg_principal=row['RTG_Principal'],
                valor_deportivo=row['Valor_Deportivo'],
                precio_mercado=precio_final,
                rol_2=str(row.get('Rol_2', '')),
                rtg_2=row.get('RTG_2', 0),
                rol_3=str(row.get('Rol_3', '')),
                rtg_3=row.get('RTG_3', 0)
            )
            db.session.add(nueva_valoracion)
            
            # Guardar el bloque JSON de FBref puro
            bloque_bruto = row.loc['Gls':].to_dict()
            bloque_stats = {k: v for k, v in bloque_bruto.items() if k not in columnas_metadata}

            nuevas_stats = EstadisticasFBref(
                jugador_id=nuevo_jugador.id,
                datos_crudos=bloque_stats
            )
            db.session.add(nuevas_stats)

            if index % 1000 == 0 and index > 0:
                db.session.commit()
                print(f"   ✅ {index} perfiles procesados...")

        db.session.commit()
        print("✨ ¡Tabla de Rendimiento Completada!")

        # --- FASE 2: MIGRACIÓN DE TRANSFERENCIAS FINANCIERAS ---
        if os.path.exists(csv_fichajes):
            print(f"\n💸 [2/2] Cargando Historial Financiero ({csv_fichajes})...")
            df_fichajes = pd.read_csv(csv_fichajes)
            
            # Limpiamos los NaN
            df_fichajes = df_fichajes.fillna({'Fee_Num': 0, 'Fee': 'N/A', 'Date': ''})
            
            # NUEVA FUNCIÓN INTELIGENTE: Clasificador Verano/Invierno
            def calcular_temporada_rendimiento(temp_fichaje, fecha_fichaje):
                try:
                    # 1. Extraemos el mes del fichaje (formato DD/MM/YYYY)
                    mes = 0
                    if fecha_fichaje:
                        partes = str(fecha_fichaje).split('/')
                        if len(partes) >= 2:
                            mes = int(partes[1])
                    
                    # 2. Obtenemos el año base de la temporada (Ej: "21/22" -> 2021)
                    año_base = 0
                    if '/' in str(temp_fichaje):
                        año_inicio = int(str(temp_fichaje).split('/')[0])
                        año_base = 2000 + año_inicio
                    elif len(str(temp_fichaje)) == 4:
                        año_base = int(temp_fichaje)
                    else:
                        return str(temp_fichaje)

                    # 3. Lógica de Mercado de Pases:
                    # Si es Enero, Febrero o Marzo (Invierno), el fichaje corresponde a la temporada actual.
                    if 1 <= mes <= 3:
                        return str(año_base) 
                    # Si es Verano (Julio, Agosto, etc.), el fichaje corresponde a la temporada PASADA.
                    else:
                        return str(año_base - 1)
                except Exception as e:
                    print(f"Error al calcular temporada para {temp_fichaje}: {e}")
                    return str(temp_fichaje)

            print(f"🚀 Migrando {len(df_fichajes)} transacciones monetarias con análisis de ventanas...")
            
            for index, row in df_fichajes.iterrows():
                if int(row['Fee_Num']) > 0:
                    
                    # APLICAMOS EL CÁLCULO CON LA FECHA INCLUIDA
                    temp_rendimiento = calcular_temporada_rendimiento(row['Season'], row['Date'])

                    nueva_transferencia = Transferencia(
                        jugador_nombre=row['Player'],
                        temporada=temp_rendimiento, # Guarda 2020 (Verano) o 2021 (Invierno)
                        fecha=str(row['Date']),
                        club_origen=str(row['Left_Club']),
                        club_destino=str(row['Joined_Club']),
                        coste_texto=str(row['Fee']),
                        coste_num=int(row['Fee_Num'])
                    )
                    db.session.add(nueva_transferencia)
            
            db.session.commit()
            print("✨ ¡Tabla de Transferencias Completada y Alineada al Rendimiento!")
        else:
            print(f"\n⚠️ Aviso: No se encontró el archivo {csv_fichajes}.")
            
        print("\n🏆 ¡MIGRACIÓN TOTAL COMPLETADA CON ÉXITO! 🏆")
        print("La base de datos scoutmew.db ha sido reconstruida con la nueva arquitectura financiera.")

if __name__ == '__main__':
    migrar_datos()