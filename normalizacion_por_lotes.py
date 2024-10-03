import pandas as pd
import requests
import json
import time
import re  # Para usar expresiones regulares
from geolocalizador import GeolocalizadorDatosGobar  # Importar desde el otro archivo
import sys
import os

sys.path.append(os.path.abspath('C:/Users/Usuario/appdata/local/programs/python/python310/lib/site-packages'))
import jwt

key = 'YXNkc2Rhc2RmYXNkZmFzZmRhc2RmYXNk'
message = {'iss': key}
secret = 'dnVvODY4Yzc2bzhzNzZqOG83czY4b2Nq'
token = jwt.encode(message, secret, algorithm='HS256')

print(token)

input_file = 'C:/Users/Usuario/Desktop/ovs-caminero/direcciones_BsAs.csv'
output_file = 'C:/Users/Usuario/Desktop/ovs-caminero/direcciones_normalizadas_por_lotes.csv'

df = pd.read_csv(input_file, sep=',', keep_default_na=False, on_bad_lines='skip')
df.columns = df.columns.str.strip()
df.rename(columns={'province;': 'province'}, inplace=True)

# Filtrar direcciones no nulas y no vacías
df = df[df['address'].notna() & (df['address'].str.strip() != '')]
direcciones = df[['address', 'district']].dropna().values.tolist()

direcciones = direcciones[:50000]

# Función para procesar la dirección y eliminar cualquier altura igual a '0'
#def procesar_direccion(direccion):
#   direccion = direccion.replace('{', '').replace('}', '')
#   return re.sub(r'\b00\b|\b0\b|\b000\b|\b0000\b', '', direccion).strip()

def procesar_direccion(direccion):
    # Eliminar llaves y limpiar la dirección
    direccion = direccion.replace('{', '').replace('}', '')
    
    # Eliminar ceros sueltos o secuencias de ceros
    direccion_limpia = re.sub(r'\b00+\b|\b0\b', '', direccion).strip()
    
    # Verificar si la dirección está vacía después del procesamiento
    if not direccion_limpia:
        return None  # Si está vacía, retornar None
    
    return direccion_limpia  # Retornar la dirección limpia si no está vacía

# Función para normalizar direcciones por lotes
def normalizar_direcciones(direcciones):
    base_url = "https://apis.datos.gob.ar/georef/api/direcciones"
    resultados = []

    for i in range(0, len(direcciones), 300):
        lote = direcciones[i:i+300]
        payload = {
            "direcciones": []
        }

        for dir in lote:
            direccion_procesada = procesar_direccion(dir[0])  # Procesar cada dirección
            if direccion_procesada:  # Verificar que la dirección no esté vacía
                payload["direcciones"].append({"direccion": direccion_procesada})

        if not payload["direcciones"]:  # Si no hay direcciones válidas en el lote, continuar
            print(f"Lote {i // 500 + 1} está vacío después del procesamiento.")
            continue

        response = requests.post(base_url, headers={'Content-Type': 'application/json', 'Authorization': 'Bearer {}'.format(token)}, data=json.dumps(payload))
        
        # Verificar la respuesta de la API
        if response.status_code == 200:
            data = response.json()
            resultados.extend(data['resultados'])
        else:
            # Imprimir el lote que causó el error
            print(f"Error en el lote {i // 500 + 1}: {response.status_code}, Mensaje: {response.text}")
            print(f"Lote que causó el error: {payload}")  # Imprimir el contenido del lote en caso de error
        
        time.sleep(1)
    
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
                district_api = dir.get('localidad', {}).get('nombre')
                score = 1 if district_original and district_api and district_original.lower() == district_api.lower() else 0
                if score > mejor_score:
                    mejor_score = score
                    mejor_direccion = {
                        'direccion': geolocalizador.construir_direccion_normalizada(dir),
                        'localidad': district_original,
                        'latitud': dir.get('ubicacion', {}).get('lat'),
                        'longitud': dir.get('ubicacion', {}).get('lon'),
                    }
        if mejor_direccion:
            normalizadas.append(mejor_direccion)

# Guardar los resultados normalizados en un archivo CSV
df_normalizado = pd.DataFrame(normalizadas)
df_normalizado.to_csv(output_file, index=False)

print("Proceso completado. Resultados guardados en:", output_file)
