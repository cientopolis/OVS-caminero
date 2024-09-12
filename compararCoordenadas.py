import csv
from geopy.distance import geodesic
import os

def comparar_coordenadas(input_csv, output_csv):
    umbral_metros = 200  # Define el umbral en metros

    try:
        with open(input_csv, mode='r', newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile, delimiter=';')  # Especifica el delimitador correcto
            fieldnames = reader.fieldnames + ['Distancia', 'Estan cerca']  # Agregamos columnas para distancia y cerca

            with open(output_csv, mode='w', newline='', encoding='utf-8') as outfile:
                # Usamos quotechar='"' para forzar las comillas alrededor de los campos
                writer = csv.DictWriter(outfile, fieldnames=fieldnames, delimiter=';', quotechar='"', quoting=csv.QUOTE_MINIMAL)
                writer.writeheader()

                for row in reader:
                    try:
                        # Obtener y limpiar coordenadas, eliminando comillas y espacios en blanco
                        latitud = row.get('Latitud', '').strip().strip('"')
                        longitud = row.get('Longitud', '').strip().strip('"')
                        latitud_delta = row.get('latituddelta', '').strip().strip('"')
                        longitud_delta = row.get('longituddelta', '').strip().strip('"')

                        # Verificar que las coordenadas no estén vacías y sean números válidos
                        if not (latitud and longitud and latitud_delta and longitud_delta):
                            raise ValueError("Coordenadas vacías o inválidas")
                        
                        # Convertir coordenadas a flotantes
                        coord1 = (float(latitud), float(longitud))
                        coord2 = (float(latitud_delta), float(longitud_delta))
                        
                        # Calculamos la distancia en metros entre las dos coordenadas
                        distancia = geodesic(coord1, coord2).meters

                        # Redondeamos la distancia a 2 decimales
                        distancia_formateada = f'{distancia:.2f}'

                        # Determinamos si las direcciones están cerca del umbral
                        estan_cerca = 'Si' if distancia <= umbral_metros else 'No'

                    except (ValueError, TypeError, KeyError) as e:
                        print(f"Error procesando fila {row}: {e}")
                        distancia_formateada = 'inf'  # Si ocurre algún error, asumimos que están muy lejos
                        estan_cerca = 'No'  # Consideramos que no están cerca si hay un error

                    # Agregamos los datos al archivo de salida
                    row['Distancia'] = distancia_formateada
                    row['Estan cerca'] = estan_cerca
                    writer.writerow(row)
                    print(f"Fila procesada: {row}")  # Mensaje de depuración

        print(f"Archivo de salida '{output_csv}' creado exitosamente en {os.path.abspath(output_csv)}")
    
    except Exception as e:
        print(f"Error al procesar archivos: {e}")

if __name__ == "__main__":
    # Reemplaza con tus rutas
    comparar_coordenadas('C:/Users/Usuario/direccionesConDelta.csv', 'C:/Users/Usuario/resultado.csv')
