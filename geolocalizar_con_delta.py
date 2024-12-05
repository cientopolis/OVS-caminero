import csv
from tkinter import Tk, filedialog
from geolocalizador import GeolocalizadorDatosGobar


def agregar_datos_a_nuevo_csv(archivo_csv, geolocalizador):
    nuevas_filas = []

    # Leer el archivo CSV
    with open(archivo_csv, mode="r", newline="",encoding="latin-1") as file:
        reader = csv.DictReader(file)
        filas = list(reader)

    direcciones_modificadas = []

    for fila in filas:
        calle = fila['calle']
        altura = fila.get('altura')

        # Saltar las filas con alturas vacías
        if not altura or altura.strip() == "":
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
    print(resultados_modificados)
    # Agregar las nuevas coordenadas al conjunto de datos
    for i, fila in enumerate(nuevas_filas):
        if i < len(resultados_modificados) and resultados_modificados[i] is not None:
            resultado_modificado = resultados_modificados[i]
            fila.update({
                'latitud_con_delta': resultado_modificado['latitud'],
                'longitud_con_delta': resultado_modificado['longitud']
            })
        else:
            # Si no hay resultado para la fila, asignar valores nulos
            fila.update({
                'latitud_con_delta': None,
                'longitud_con_delta': None
            })


    # Guardar los resultados en un nuevo archivo CSV
    nuevo_archivo = archivo_csv.replace('.csv', '_geolocalizado.csv')
    with open(nuevo_archivo, mode='w', encoding='latin-1', newline='') as file:
        fieldnames = [
            'direccion_original', 'direccion_modificada', 
            'latitud_original', 'longitud_original', 
            'latitud_con_delta', 'longitud_con_delta', 'localidad'
        ]
        writer = csv.DictWriter(file, fieldnames=fieldnames)
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
