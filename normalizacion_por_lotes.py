import pandas as pd
import requests
import json
import time
import re  # Para usar expresiones regulares
from geolocalizador import GeolocalizadorDatosGobar  # Importar desde el otro archivo
import sys
import os


sys.path.append(os.path.abspath('C:/Users/Usuario/appdata/local/programs/python/python310/lib/site-packages'))

input_file = '/home/lifiano/Escritorio/Martin/OVS-caminero/direcciones_BsAs.csv'
output_file = '/home/lifiano/Escritorio/Martin/OVS-caminero/direcciones_normalizadas_por_lotes.csv'

df = pd.read_csv(input_file, sep=',', keep_default_na=False, on_bad_lines='skip')
df.columns = df.columns.str.strip()

# Filtrar direcciones no nulas y no vacías
df = df[df['address'].notna() & (df['address'].str.strip() != '')]
direcciones = df[['address', 'district']].dropna().values.tolist()
direcciones = direcciones[:1000]

# Función para procesar la dirección y eliminar cualquier altura igual a '0'
def procesar_direccion(direccion):
    direccion = direccion.replace('{', '').replace('}', '')
    direccion_limpia = re.sub(r'\b00+\b|\b0\b', '', direccion).strip()
    return direccion_limpia if direccion_limpia else None

# Función para normalizar direcciones por lotes
def normalizar_direcciones(direcciones):
    base_url = "localhost:8080/api/direcciones"
    resultados = []

    for i in range(0, len(direcciones), 1000):
        lote = direcciones[i:i + 1000]
        payload = {
            "direcciones": []
        }

        for dir in lote:
            direccion_procesada = procesar_direccion(dir[0])
            if direccion_procesada:
                direccion_data = {
                    "direccion": direccion_procesada,
                    "max": 3
                }
                if dir[1]:
                    direccion_data["localidad_censal"] = dir[1]
                payload["direcciones"].append(direccion_data)

        if not payload["direcciones"]:
            print(f"Lote {i // 900 + 1} está vacío después del procesamiento.")
            continue

        response = requests.post(base_url, headers={'Content-Type': 'application/json'}, data=json.dumps(payload))

        if response.status_code == 200:
            data = response.json()
            resultados.extend(data['resultados'])
        else:
            print(f"Error en el lote {i // 900 + 1}: {response.status_code}, Mensaje: {response.text}")
            print(f"Lote que causó el error: {payload}")

        time.sleep(0)

    return resultados

# Normalización y geolocalización
resultados_normalizados = normalizar_direcciones(direcciones)
geolocalizador = GeolocalizadorDatosGobar()

normalizadas = []
for i, resultado in enumerate(resultados_normalizados):
    if resultado['cantidad'] > 0:
        mejor_direccion = None
        mejor_score = -1
        
        for dir in resultado['direcciones']:
            provincia = dir.get('provincia', {}).get('nombre')
            if provincia and 'buenos aires' in provincia.lower():
                district_original = direcciones[i][1]
                district_api = dir.get('localidad_censal', {}).get('nombre')
                score = 1 if district_original and district_api and district_original.lower() == district_api.lower() else 0
                if score > mejor_score:
                    mejor_score = score
                    mejor_direccion = {
                        'direccion': dir.get('nomenclatura'),
                        'localidad': district_api,
                        'latitud': dir.get('ubicacion', {}).get('lat'),
                        'longitud': dir.get('ubicacion', {}).get('lon'),
                    }
        if mejor_direccion:
            normalizadas.append(mejor_direccion)

# Guardar los resultados normalizados en un archivo CSV
df_normalizado = pd.DataFrame(normalizadas)
df_normalizado = df_normalizado.drop_duplicates(subset=['direccion', 'localidad', 'latitud', 'longitud'], keep='first')
df_normalizado.to_csv(output_file, index=False)

print("Proceso completado. Resultados guardados en:", output_file)

