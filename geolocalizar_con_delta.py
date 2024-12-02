import csv
import random
from tkinter import Tk, filedialog
from geolocalizador import GeolocalizadorDatosGobar


def agregar_datos_a_nuevo_csv(archivo_csv, geolocalizador):
    nuevas_filas = []

    # Leer el archivo CSV
    with open(archivo_csv, mode='r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        filas = list(reader)

    direcciones = []

    for fila in filas:
        calle = fila['calle']
        altura = fila.get('altura')

        # Saltar las filas con alturas vacías
        if not altura or altura.strip() == "":
            continue

        # Generar una altura aleatoria y sumar a la existente
        altura_sumada = int(float(altura)) + random.randint(5, 50)
        direccion = f"{calle} {altura_sumada}"

        # Agregar dirección y localidad a la lista de direcciones
        direcciones.append((direccion, fila['localidad']))

    # Usar el método `procesar_direcciones` para obtener resultados geolocalizados
    resultados = geolocalizador.procesar_direcciones(direcciones)

    # Crear nuevas filas con los resultados obtenidos
    for resultado in resultados:
        nuevas_filas.append({
            'calle': resultado['calle'],
            'altura': resultado['altura'],
            'latitud': resultado['latitud'],
            'longitud': resultado['longitud'],
            'localidad': resultado['localidad']
        })

    # Guardar los resultados en un nuevo archivo CSV
    nuevo_archivo = archivo_csv.replace('.csv', '_geolocalizado.csv')
    with open(nuevo_archivo, mode='w', encoding='utf-8', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=['calle', 'altura', 'latitud', 'longitud', 'localidad'])
        writer.writeheader()
        writer.writerows(nuevas_filas)

    print(f"Se han guardado {len(nuevas_filas)} filas nuevas en el archivo: {nuevo_archivo}")


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
