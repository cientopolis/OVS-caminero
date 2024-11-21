import csv
import os
import sys
sys.path.append('/home/lifiano/.local/lib/python3.8/site-packages')
from geopy.distance import geodesic
import statistics  # Para calcular la mediana

def comparar_coordenadas(input_csv, output_csv):
    umbral_metros = 200  # Define el umbral en metros
    total_cercanas = 0  # Contador de direcciones que están cerca
    distancias = []  # Lista para almacenar todas las distancias calculadas

    try:
        with open(input_csv, mode='r', newline='', encoding='utf-8') as csvfile:
            # Usamos ',' como delimitador de campos y '"' como delimitador de cadenas
            reader = csv.DictReader(csvfile, delimiter=',', quotechar='"') 
            fieldnames = reader.fieldnames + ['Distancia', 'Estan cerca']

            with open(output_csv, mode='w', newline='', encoding='utf-8') as outfile:
                writer = csv.DictWriter(outfile, fieldnames=fieldnames, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
                writer.writeheader()

                for row in reader:
                    try:
                        # Obtener coordenadas
                        latitud = row.get('latitud')
                        longitud = row.get('longitud')
                        latitud_delta = row.get('latitud_verificada')
                        longitud_delta = row.get('longitud_verificada')

                        if not (latitud and longitud and latitud_delta and longitud_delta):
                            raise ValueError("Coordenadas vacías o inválidas")
                        
                        coord1 = (float(latitud), float(longitud))
                        coord2 = (float(latitud_delta), float(longitud_delta))
                        
                        distancia = geodesic(coord1, coord2).meters
                        distancia_formateada = f'{distancia:.2f} metros'

                        # Guardar la distancia en la lista
                        distancias.append(distancia)

                        # Determinamos si las direcciones están cerca del umbral
                        estan_cerca = 'Si' if distancia <= umbral_metros else 'No'

                        # Incrementamos el contador si están cerca
                        if estan_cerca == 'Si':
                            total_cercanas += 1

                    except (ValueError, TypeError, KeyError) as e:
                        print(f"Error procesando fila {row}: {e}")
                        distancia_formateada = 'inf'
                        estan_cerca = 'No'

                    row['Distancia'] = distancia_formateada
                    row['Estan cerca'] = estan_cerca
                    writer.writerow(row)
                    print(f"Fila procesada: {row}")

                # Calcular la mediana de las distancias si hay datos
                mediana = statistics.median(distancias) if distancias else 0
                print(f"Mediana calculada: {mediana:.2f} metros")

                # Agregar una fila final con el total de direcciones cercanas
                total_row = {field: '' for field in fieldnames}
                total_row['Distancia'] = 'Total cercanas'
                total_row['Estan cerca'] = total_cercanas
                writer.writerow(total_row)

                # Agregar una fila con la mediana de las distancias
                mediana_row = {field: '' for field in fieldnames}
                mediana_row['Distancia'] = 'Mediana'
                mediana_row['Estan cerca'] = f'{mediana:.2f} metros'
                writer.writerow(mediana_row)

        print(f"Archivo de salida '{output_csv}' creado exitosamente en {os.path.abspath(output_csv)}")
    
    except Exception as e:
        print(f"Error al procesar archivos: {e}")

if __name__ == "__main__":
    comparar_coordenadas('/home/lifiano/Escritorio/Martin/OVS-caminero/direccionesVerificadas.csv', '/home/lifiano/Escritorio/Martin/OVS-caminero/distanciaDirecciones.csv')
