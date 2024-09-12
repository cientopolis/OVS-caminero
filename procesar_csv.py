import csv
import sys
sys.path.append('C:/Users/Usuario/Desktop/OVS-caminero')
import csv
from geolocalizador import GeolocalizadorNominatim, GeolocalizadorDatosGobar, GeolocalizadorHere, GeolocalizadorLocationIQ, GeolocalizadorOpenCage, GeolocalizadorPositionStack

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
    # ANDAN TODOS: Nominatim (a veces falla por 403, algo del user agent) 
    #              DatosGobAr 
    #              Here
    #              LocationIQ
    #              OpenCage
    #              PositionStack
    
    
    #geolocalizador = GeolocalizadorNominatim('My geolocalizador')
    geolocalizador = GeolocalizadorDatosGobar()
    #geolocalizador = GeolocalizadorHere('WVGOKd5D1jL7mKdGX72JwyLDBLnyVjbVEup57gClXT4')
    #geolocalizador = GeolocalizadorLocationIQ('pk.ba47f83040b10421760894962582fcfc')
    #geolocalizador = GeolocalizadorOpenCage('6590cde716274d6fa8073f08c1b072e6')
    #geolocalizador = GeolocalizadorPositionStack('e665bce8e383c3af9321bfe5ba8dc7b0')
    
    procesar_direcciones('C:/Users/Usuario/Desktop/OVS-caminero/direccionesCSV.csv', 'C:/Users/Usuario/Desktop/OVS-caminero/direcciones_geolocalizadas.csv', geolocalizador)
