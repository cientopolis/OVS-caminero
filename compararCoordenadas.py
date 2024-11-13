import csv
import os
import sys
from geopy.distance import geodesic

sys.path.append('/home/lifiano/.local/lib/python3.8/site-packages')

def comparar_coordenadas(input_csv, output_csv):
    umbral_metros = 200  # Define el umbral en metros

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
                        distancia_formateada = f'{distancia:.2f}'

                        estan_cerca = 'Si' if distancia <= umbral_metros else 'No'

                    except (ValueError, TypeError, KeyError) as e:
                        print(f"Error procesando fila {row}: {e}")
                        distancia_formateada = 'inf'
                        estan_cerca = 'No'

                    row['Distancia'] = distancia_formateada
                    row['Estan cerca'] = estan_cerca
                    writer.writerow(row)
                    print(f"Fila procesada: {row}")

        print(f"Archivo de salida '{output_csv}' creado exitosamente en {os.path.abspath(output_csv)}")
    
    except Exception as e:
        print(f"Error al procesar archivos: {e}")

if __name__ == "__main__":
    comparar_coordenadas('/home/lifiano/Escritorio/Martin/OVS-caminero/direccionesVerificadas.csv', '/home/lifiano/Escritorio/Martin/OVS-caminero/distanciaDirecciones.csv')
