# ⚽ SVD: Sistema de Valoración Deportiva

> **Nota del Autor:** Este es un proyecto de tesis de carácter exploratorio y analítico. Aunque la plataforma base es completamente funcional, el sistema sigue en desarrollo (Work in Progress). SVD está abierto a sugerencias, mejoras y contribuciones de la comunidad con interes por la ciencia de datos en el fútbol.

Una plataforma avanzada construida para evaluar, comparar y descubrir talento futbolístico. SVD procesa datos de más de 1,500 jugadores de las grandes ligas utilizando un algoritmo propio basado en percentiles y estadística avanzada. Su objetivo principal es calcular el rendimiento real en el campo frente al valor de mercado, facilitando decisiones estratégicas y procesos de scouting.

## 🌟 Funcionalidades Detalladas


### 📊 Dashboard y Visión Macro
* **Métricas Globales:** Monitoreo del "Universo Data" procesado y el valor volumétrico total del mercado analizado.
* **Análisis de Eficiencia por Liga:** Evaluación del rendimiento deportivo promedio (RTG) contrastando las 5 grandes ligas (Big Five) mediante gráficos de barras.
* **Top Valor Deportivo:** Clasificación automática de los jugadores élite categorizados por su impacto en el campo (Ataque, Creación, Médula y Defensa).

<img width="1844" height="973" alt="Screenshot_2026-08-21_20 02 54" src="https://github.com/user-attachments/assets/10824c8c-fa16-476e-bc8b-1cc327a26070" />

<img width="1838" height="955" alt="Screenshot_2026-08-21_20 03 01" src="https://github.com/user-attachments/assets/2210a86b-fdb9-4390-a4b5-78dabbcc18ba" />


### 🔬 Análisis de Perfil Microscópico

<img width="800" height="421" alt="Kooha-2026-08-21-20-38-17online-video-cutter com-ezgif com-video-to-gif-converter" src="https://github.com/user-attachments/assets/c307a05c-e9f2-4834-b5b2-1f99261d5534" />



* **Desglose de Producción (por 90 min):** Evaluación de métricas avanzadas (Goles Esperados - npxG, Asistencias Esperadas - xA, Acciones de Creación) normalizadas por el tiempo de juego real.

<img width="800" height="421" alt="Kooha-2026-08-21-20-38-17online-video-cutter com1-ezgif com-video-to-gif-converter" src="https://github.com/user-attachments/assets/1db3c2db-1f7b-4c03-93ab-f559a370a5d6" />


* **Evolución-Trayectoria y comparacion posicional:** Gráficos de líneas que contrastan el rendimiento estadístico histórico del jugador frente a las fluctuaciones de su valor de mercado a lo largo del tiempo. Ademas de compartiva con otros jugadores con graficos estadísticos


<img width="800" height="421" alt="Kooha-2026-08-21-20-38-17online-video-cutter com2-ezgif com-video-to-gif-converter" src="https://github.com/user-attachments/assets/bdab34a8-4df0-4a3d-9ff6-c0987bec3baf" />

*  **Búsqueda de Similitudes (Clones):** Motor de recomendación que busca perfiles con una huella estadística casi idéntica (ej. 98% de similitud) pero con un valor de mercado inferior, identificando verdaderas ineficiencias y oportunidades de mercado.





### ⚔️ Comparativa H2H (Head-to-Head) y Scatter Analítico

<img width="800" height="421" alt="Kooha-2026-08-21-20-38-17online-video-cutter com4-ezgif com-video-to-gif-converter" src="https://github.com/user-attachments/assets/3017b2fb-e919-449f-9e0a-ae8bfab4cee0" />

* **Matrices Tácticas en Radar:** Comparación visual simultánea de múltiples jugadores, superponiendo su rendimiento táctico (ej. acciones defensivas, intercepciones, despejes).
* **Desglose de Percentiles:** Barras de progreso que muestran el ranking exacto de un jugador en métricas clave frente al resto de futbolistas evaluados en su misma posición.

<img width="800" height="421" alt="Kooha-2026-08-21-20-38-17online-video-cutter com3-ezgif com-video-to-gif-converter" src="https://github.com/user-attachments/assets/6c8f4717-5d05-495b-94a9-17a3800a3f35" />


* **Scatter de analisis estadistico:** Libertad total de explorar cualquier estadistica o parametro en base a posicion y minutos, tomando a toda la base de datos de la temporada a elección

## 🚀 Próximos Pasos y Contribuciones
Al ser un proyecto de investigación abierto, el modelo de valoración deportiva está en constante calibración. Los siguientes pasos incluyen:
* Adicion de la posicion de Portero.
* Ampliar el set de datos estadísticos.
* ¡Pull Requests son bienvenidos! Si te interesa el análisis de datos deportivos, siéntete libre de hacer un fork, proponer mejoras o abrir *issues* para discutir la metodología.

## 🛠️ Stack Tecnológico
* **Backend & Datos:** Python, Flask, Pandas, Numpy.
* **Base de Datos:** SQLite / SQLAlchemy.
* **Frontend UI/UX:** HTML, JavaScript, CSS (Tailwind CSS).

## ⚙️ Instalación Local
Para correr el entorno exploratorio en tu máquina:

1. Clona este repositorio:
`git clone https://github.com/MewYersi/webscout-mew-scraper.git`
2. Activa tu entorno virtual (recomendado).
3. Instala las dependencias de Python:
`pip install -r requirements.txt`
4. Inicia el servidor de Flask:
`python app.py` 
*(Nota: Si deseas modificar la interfaz, requerirás ejecutar `npm run dev` para compilar los cambios de Tailwind).*
