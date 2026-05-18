import pandas as pd
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import os

# Configuración inicial para poder usar la Base de Datos
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///scoutmew.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# ==========================================
# 1. DEFINICIÓN DE LAS 3 TABLAS
# ==========================================
class Jugador(db.Model):
    __tablename__ = 'jugadores'
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    nacion = db.Column(db.String(10))
    edad = db.Column(db.Integer)
    club = db.Column(db.String(100))
    posicion = db.Column(db.String(10))
    minutos = db.Column(db.Integer)

class Valoracion(db.Model):
    __tablename__ = 'valoraciones'
    id = db.Column(db.Integer, primary_key=True)
    jugador_id = db.Column(db.Integer, db.ForeignKey('jugadores.id'))
    rol_principal = db.Column(db.String(20))
    rtg_principal = db.Column(db.Float)
    valor_deportivo = db.Column(db.Float)
    precio_mercado = db.Column(db.Float)
    rol_2 = db.Column(db.String(20))
    rtg_2 = db.Column(db.Float)
    rol_3 = db.Column(db.String(20))
    rtg_3 = db.Column(db.Float)

class EstadisticasFBref(db.Model):
    __tablename__ = 'estadisticas_fbref'
    id = db.Column(db.Integer, primary_key=True)
    jugador_id = db.Column(db.Integer, db.ForeignKey('jugadores.id'))
    
    # MAGIA PURA: Una sola columna JSON que guardará TODAS tus +90 estadísticas
    datos_crudos = db.Column(db.JSON)
# ==========================================
# 2. PROCESO ETL (Extraer y Cargar)
# ==========================================
def migrar_datos():
    csv_file = 'Premier_Valuation_Model_Final2.csv'
    
    if not os.path.exists(csv_file):
        print(f"❌ No se encontró el archivo: {csv_file}")
        return

    print("📊 Leyendo el CSV Maestro...")
    df = pd.read_csv(csv_file)
    
    # Rellenar valores nulos (NaN) con 0 para evitar errores en la BD
    df = df.fillna(0)

    # Entramos al contexto de la aplicación para interactuar con la BD
    with app.app_context():
        # Borramos la BD anterior si existe y la creamos desde cero limpia
        db.drop_all()
        db.create_all()
        print("🏗️ Tablas creadas en scoutmew.db")

        print("🚀 Insertando jugadores (Esto tomará unos segundos)...")
        
        for index, row in df.iterrows():
            # 1. Crear el Jugador (Identidad Básica)
            nuevo_jugador = Jugador(
                nombre=row['Player'],
                nacion=row['Nation'],
                edad=int(row['Age']),
                club=row['Squad'],
                posicion=row['Pos'],
                minutos=int(row['Min'])
            )
            db.session.add(nuevo_jugador)
            db.session.flush() # Importante: Obtenemos el ID generado antes del commit final
            
            # 2. Crear su Valoración (Tu modelo matemático)
            nueva_valoracion = Valoracion(
                jugador_id=nuevo_jugador.id,
                rol_principal=row['Rol_Principal'],
                rtg_principal=row['RTG_Principal'],
                valor_deportivo=row.get('Valor_Deportivo', 0),
                precio_mercado=row['Precio_Mercado'],
                rol_2=str(row.get('Rol_2', '')),
                rtg_2=row.get('RTG_2', 0),
                rol_3=str(row.get('Rol_3', '')),
                rtg_3=row.get('RTG_3', 0)
            )
            db.session.add(nueva_valoracion)
            
            # 3. Crear sus Estadísticas (Datos crudos)
            
            # Le decimos a Pandas: "Corta la fila desde la columna 'Gls' hasta 'AerialWon%'"
            # y conviértelo en un diccionario de Python al instante.
            bloque_estadisticas = row.loc['Gls':'AerialWon%'].to_dict()

            nuevas_estadisticas = EstadisticasFBref(
                jugador_id=nuevo_jugador.id,
                datos_crudos=bloque_estadisticas
            )
            db.session.add(nuevas_estadisticas)

        # Guardamos todos los cambios en la base de datos de un solo golpe
        db.session.commit()
        print("✅ ¡Migración completada con éxito! La base de datos está lista para Flask.")

if __name__ == '__main__':
    migrar_datos()