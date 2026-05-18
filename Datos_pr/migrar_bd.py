import pandas as pd
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import os

# Configuración inicial
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///scoutmew.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class Jugador(db.Model):
    __tablename__ = 'jugadores'
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
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
    # ELIMINADO: precio_mercado
    rol_2 = db.Column(db.String(20))
    rtg_2 = db.Column(db.Float)
    rol_3 = db.Column(db.String(20))
    rtg_3 = db.Column(db.Float)

class EstadisticasFBref(db.Model):
    __tablename__ = 'estadisticas_fbref'
    id = db.Column(db.Integer, primary_key=True)
    jugador_id = db.Column(db.Integer, db.ForeignKey('jugadores.id'))
    datos_crudos = db.Column(db.JSON)

# ==========================================
# 2. PROCESO DE MIGRACIÓN MAESTRA
# ==========================================
def migrar_datos():
    csv_file = 'Scouting_Database_Final.csv'
    
    if not os.path.exists(csv_file):
        print(f"❌ Error: No encuentro el archivo {csv_file}")
        return

    print("📊 Cargando Base de Datos Maestra de Europa...")
    df = pd.read_csv(csv_file)
    df = df.fillna(0)

    # Nombres de las columnas que nuestro motor añadió al final y NO son estadísticas FBref
    columnas_metadata = ['Valor_Deportivo', 'Rol_Principal', 'RTG_Principal', 'Rol_2', 'RTG_2', 'Rol_3', 'RTG_3', 'Rank']

    with app.app_context():
        print("🏗️ Limpiando y recreando tablas...")
        db.drop_all()
        db.create_all()

        print(f"🚀 Migrando {len(df)} registros (esto puede tardar un poco)...")
        
        for index, row in df.iterrows():
            # 1. Crear Jugador
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
            db.session.flush() 
            
            # 2. Guardar Valoración
            nueva_valoracion = Valoracion(
                jugador_id=nuevo_jugador.id,
                rol_principal=row['Rol_Principal'],
                rtg_principal=row['RTG_Principal'],
                valor_deportivo=row['Valor_Deportivo'], # Tomamos el único valor monetario
                rol_2=str(row.get('Rol_2', '')),
                rtg_2=row.get('RTG_2', 0),
                rol_3=str(row.get('Rol_3', '')),
                rtg_3=row.get('RTG_3', 0)
            )
            db.session.add(nueva_valoracion)
            
            # 3. Guardar el bloque JSON (Filtrado de forma segura)
            bloque_bruto = row.loc['Gls':].to_dict()
            bloque_stats = {k: v for k, v in bloque_bruto.items() if k not in columnas_metadata}

            nuevas_stats = EstadisticasFBref(
                jugador_id=nuevo_jugador.id,
                datos_crudos=bloque_stats
            )
            db.session.add(nuevas_stats)

            if index % 500 == 0 and index > 0:
                db.session.commit()
                print(f"✅ {index} filas procesadas...")

        db.session.commit()
        print("\n✨ ¡MIGRACIÓN TOTAL COMPLETADA! ✨")
        print(f"Archivo: {csv_file} -> scoutmew.db")

if __name__ == '__main__':
    migrar_datos()