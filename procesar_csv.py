import csv
from geolocalizador import GeolocalizadorNominatim, GeolocalizadorDatosGobar, GeolocalizadorHere

def procesar_direcciones(input_csv, output_csv, geolocalizador):
    with open(input_csv, mode='r', newline='') as csvfile:
        reader = csv.DictReader(csvfile, delimiter=';')  # Especifica el delimitador correcto
        fieldnames = ['direccion', 'latitud', 'longitud','provincia','localidad']
        
        with open(output_csv, mode='w', newline='') as outputfile:
            writer = csv.DictWriter(outputfile, fieldnames=fieldnames)
            writer.writeheader()
            
            for row in reader:
                direccion = row['direccion']
                provincia = row['provincia']
                localidad = row['localidad']
                try:
                    lat, lon = geolocalizador.obtener_coordenadas(direccion,provincia,localidad)
                    writer.writerow({
                        'direccion': direccion,
                        'latitud': lat,
                        'longitud': lon,
                        'provincia': provincia,
                        'localidad': localidad
                    })
                except Exception as e:
                    writer.writerow({
                       'direccion': direccion,
                       'latitud': None,
                       'longitud': None,
                        'provincia': None,
                        'localidad': None
                   })


if __name__ == "__main__":
    # Ejemplo de uso:
    #geolocalizador = GeolocalizadorNominatim('My geolocalizador')
    geolocalizador = GeolocalizadorDatosGobar()
    #geolocalizador = GeolocalizadorHere('WVGOKd5D1jL7mKdGX72JwyLDBLnyVjbVEup57gClXT4')
    procesar_direcciones('direccionesCSV.csv', 'direcciones_geolocalizadas.csv', geolocalizador)

