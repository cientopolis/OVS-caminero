import pandas as pd
from tkinter import Tk, filedialog
from geolocalizador import GeolocalizadorDatosGobar
import sys
sys.path.append("/home/lifiano/.local/lib/python3.8/site-packages")
from geopy.distance import geodesic


# Función para calcular la distancia usando geodesic en metros
def calcular_distancia_geodesic(lat1, lon1, lat2, lon2):
    # Calcular la distancia geodésica entre dos puntos en metros
    punto1 = (lat1, lon1)
    punto2 = (lat2, lon2)
    distancia = geodesic(punto1, punto2).meters  # Distancia en metros
    return round(distancia,5)


def agregar_datos_a_nuevo_csv(archivo_csv, geolocalizador):
    # Leer el archivo CSV usando pandas
    df = pd.read_csv(archivo_csv, encoding="latin-1")

    direcciones_modificadas = []

    # Lista para almacenar los resultados
    nuevas_filas = []

    for i, fila in df.iterrows():
        # CSV ingresado debe contener CALLE y ALTURA 
        calle = fila['calle']
        altura = fila.get('altura')

        # Saltar las filas con alturas vacías
        if not altura or pd.isna(altura):
            continue

        # Generar una altura aleatoria y sumar a la existente
        delta = 20
        altura_sumada = int(float(altura)) + delta

        # Crear direcciones original y modificada
        direccion_original = f"{calle} {altura}"
        direccion_modificada = f"{calle} {altura_sumada}"

        # Agregar dirección modificada a la lista de direcciones para geolocalización
        direcciones_modificadas.append((direccion_modificada, fila['localidad']))

        # Preparar datos para la nueva fila, conservando las coordenadas originales
        nuevas_filas.append({
            'direccion_original': direccion_original,
            'direccion_modificada': direccion_modificada,
            'localidad': fila['localidad'],
            'latitud_original': fila.get('latitud'),  # Conservar latitud original
            'longitud_original': fila.get('longitud')  # Conservar longitud original
        })

    # Obtener geolocalización para direcciones modificadas
    resultados_modificados = geolocalizador.procesar_direcciones(direcciones_modificadas)

    # Crear un diccionario para mapear las direcciones modificadas a sus coordenadas
    coordenadas_dict = {}
    for resultado in resultados_modificados:
        if resultado:
            direccion = f"{resultado['calle']} {resultado['altura']}"
            coordenadas_dict[direccion] = {
                'latitud': resultado['latitud'],
                'longitud': resultado['longitud']
            }

    # Contador para las direcciones no geolocalizadas
    no_geolocalizadas = 0

    # Crear un DataFrame de las nuevas filas
    df_nuevas_filas = pd.DataFrame(nuevas_filas)

    # Agregar las nuevas coordenadas y calcular la distancia
    for i, fila in df_nuevas_filas.iterrows():
        direccion_modificada = fila['direccion_modificada']
        
        # Verificar si la dirección modificada está en el diccionario de coordenadas
        if direccion_modificada in coordenadas_dict:
            coordenadas = coordenadas_dict[direccion_modificada]
            df_nuevas_filas.at[i, 'latitud_con_delta'] = coordenadas['latitud']
            df_nuevas_filas.at[i, 'longitud_con_delta'] = coordenadas['longitud']

            # Calcular la distancia entre las coordenadas originales y las modificadas
            lat1 = fila['latitud_original']
            lon1 = fila['longitud_original']
            lat2 = coordenadas['latitud']
            lon2 = coordenadas['longitud']

            # Verificar que ambas coordenadas no sean None antes de calcular la distancia
            if pd.notna(lat1) and pd.notna(lon1) and pd.notna(lat2) and pd.notna(lon2):
                distancia = calcular_distancia_geodesic(lat1, lon1, lat2, lon2)
                df_nuevas_filas.at[i, 'distancia_delta_metros'] = distancia  # Guardar la distancia en metros
            else:
                df_nuevas_filas.at[i, 'distancia_delta_metros'] = None
        else:
            # Si no hay resultado para la fila, asignar valores nulos
            df_nuevas_filas.at[i, 'latitud_con_delta'] = None
            df_nuevas_filas.at[i, 'longitud_con_delta'] = None
            df_nuevas_filas.at[i, 'distancia_delta_metros'] = None
            # Incrementar el contador de direcciones no geolocalizadas
            no_geolocalizadas += 1

    # Guardar los resultados en un nuevo archivo CSV
    nuevo_archivo = archivo_csv.replace('.csv', '_geolocalizado.csv')
    df_nuevas_filas.to_csv(nuevo_archivo, index=False, encoding="latin-1")

    print(f"Se han guardado {len(df_nuevas_filas)} filas nuevas en el archivo: {nuevo_archivo}")
    print(f"Total de direcciones no geolocalizadas: {no_geolocalizadas}")


# Selección del archivo CSV
def seleccionar_archivo_csv():
    Tk().withdraw()
    archivo = filedialog.askopenfilename(filetypes=[("Archivos CSV", "*.csv")])
    return archivo


if __name__ == "__main__":
    archivo_csv = seleccionar_archivo_csv()
    if archivo_csv:
        geolocalizador = GeolocalizadorDatosGobar(0)
        agregar_datos_a_nuevo_csv(archivo_csv, geolocalizador)
    else:
        print("No se seleccionó ningún archivo.")
