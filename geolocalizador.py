from abc import ABC, abstractmethod
import time 
def limpiar_calle(calle):
        import re
        """
        Función auxiliar para eliminar números no deseados al principio de una calle.
        """
        if not isinstance(calle, str):
            return ''  # Si 'calle' no es un string, devolver cadena vacía
            # Eliminar números al inicio de la calle que no corresponden a una altura
        return re.sub(r'^\d+\s', '', calle)
class Geolocalizador(ABC):
    @abstractmethod
    def obtener_coordenadas(self, direccion, provincia, localidad):
        pass

class GeolocalizadorNominatim(Geolocalizador):
    def __init__(self, user_agent, delay=2):
        self.user_agent = user_agent
        self.delay = delay

    def obtener_coordenadas(self, direccion, provincia, localidad):
        import requests
        import urllib.parse
        
        direccion_codificada = urllib.parse.quote(direccion)
        url = f"https://nominatim.openstreetmap.org/search?street={direccion_codificada}&city={localidad}&format=json"
        response = requests.get(url)
        data = response.json()
        
        time.sleep(self.delay)  # Tiempo de espera entre solicitudes
        
        latitud = data[0]['lat']
        longitud = data[0]['lon']
        return latitud, longitud

class GeolocalizadorDatosGobar(Geolocalizador):
    def __init__(self, delay=0):
        self.delay = delay
        self.total_solicitudes = 0  # Inicializar contador de solicitudes totales
        self.solicitudes_exitosas = 0  # Inicializar contador de solicitudes exitosas

    def obtener_coordenadas(self, direccion, provincia, localidad):
        import requests
        import urllib.parse
        direccion_codificada = urllib.parse.quote(direccion)
        url = f"https://apis.datos.gob.ar/georef/api/direcciones?direccion={direccion_codificada}"
        response = requests.get(url)
        data = response.json()

        time.sleep(self.delay)  # Tiempo de espera entre solicitudes

        if data['direcciones']:
           return data['direcciones'][0]['ubicacion']['lat'], data['direcciones'][0]['ubicacion']['lon']
        else:
           # Manejo del caso cuando no se encuentran direcciones
           return None, None

    def construir_direccion_normalizada(self,data):
        
        # Obtener los campos de la respuesta
        calle = data.get('calle', {}).get('nombre', '')
        altura = data.get('altura', {}).get('valor', '')
        calle_cruce_1 = data.get('calle_cruce_1', {}).get('nombre', '')
        calle_cruce_2 = data.get('calle_cruce_2', {}).get('nombre', '')
        
        calle = limpiar_calle(calle)
        calle_cruce_1 = limpiar_calle(calle_cruce_1)
        calle_cruce_2 = limpiar_calle(calle_cruce_2)
        
        # Construir la dirección completa
        direccion_completa = calle

        if altura:
            direccion_completa += f" {altura}"
            # Solo agregar "entre" si ambos cruces están presentes
        if calle_cruce_1 and calle_cruce_2:
            direccion_completa += f" entre {calle_cruce_1} y {calle_cruce_2}"
            # Si solo está presente uno de los cruces
        elif calle_cruce_1:
            direccion_completa += f" y {calle_cruce_1}"
        elif calle_cruce_2:
            direccion_completa += f" y {calle_cruce_2}"
        # Verificar si hay un número no deseado al principio de la dirección
        # Eliminamos números al inicio que no correspondan a una altura real
        return direccion_completa

    def normalizar_direccion(self,direccion, provincia=None, distrito=None):
        import requests
        url = "https://apis.datos.gob.ar/georef/api/direcciones"
        params = {
            'direccion': direccion,
            'provincia': provincia,
            'departamento': distrito
            }
        self.total_solicitudes += 1
        response = requests.get(url,params)
        # Modificación en el archivo geolocalizador.py
        
        if response.status_code != 200:
            return None  # Manejo de errores en caso de que la solicitud falle
        
        data = response.json()

        if not data['direcciones']:  # Si no hay direcciones en la respuesta
            return None
        self.solicitudes_exitosas += 1
        return self.construir_direccion_normalizada(data['direcciones'][0])
    def obtener_estadisticas(self):
        return {
        'total_solicitudes': self.total_solicitudes,
        'solicitudes_exitosas': self.solicitudes_exitosas
        }
    


    
class GeolocalizadorHere(Geolocalizador):
    def __init__(self, api_key, delay=1):
        self.api_key = api_key
        self.delay = delay

    def obtener_coordenadas(self, direccion, provincia, localidad):
        import requests
        import urllib.parse
        
        direccion_completa = f"{direccion}, {localidad}, {provincia}"
        direccion_codificada = urllib.parse.quote(direccion_completa)
        url = f"https://geocode.search.hereapi.com/v1/geocode?q={direccion_codificada}&apiKey={self.api_key}"
        response = requests.get(url)
        data = response.json()

        time.sleep(self.delay)  # Tiempo de espera entre solicitudes
        
        latitud = data['items'][0]['position']['lat']
        longitud = data['items'][0]['position']['lng']
        return latitud, longitud

class GeolocalizadorLocationIQ(Geolocalizador):
    def __init__(self, api_key, delay=1):
        self.api_key = api_key
        self.delay = delay

    def obtener_coordenadas(self, direccion, provincia, localidad):
        import requests
        import urllib.parse
        
        direccion_completa = f"{direccion}, {localidad}, {provincia}"
        direccion_codificada = urllib.parse.quote(direccion_completa)
        url = f"https://us1.locationiq.com/v1/search.php?key={self.api_key}&q={direccion_codificada}&format=json"
        response = requests.get(url)
        data = response.json()

        time.sleep(self.delay)  # Tiempo de espera entre solicitudes
        
        latitud = data[0]['lat']
        longitud = data[0]['lon']
        return latitud, longitud

class GeolocalizadorOpenCage(Geolocalizador):
    def __init__(self, api_key, delay=1):
        self.api_key = api_key
        self.delay = delay

    def obtener_coordenadas(self, direccion, provincia, localidad):
        import requests
        import urllib.parse
        
        direccion_completa = f"{direccion}, {localidad}, {provincia}"
        direccion_codificada = urllib.parse.quote(direccion_completa)
        url = f"https://api.opencagedata.com/geocode/v1/json?q={direccion_codificada}&key={self.api_key}"
        response = requests.get(url)
        data = response.json()

        time.sleep(self.delay)  # Tiempo de espera entre solicitudes
        
        latitud = data['results'][0]['geometry']['lat']
        longitud = data['results'][0]['geometry']['lng']
        return latitud, longitud

class GeolocalizadorPositionStack(Geolocalizador):
    def __init__(self, api_key, delay=1):
        self.api_key = api_key
        self.delay = delay

    def obtener_coordenadas(self, direccion, provincia, localidad):
        import requests
        import urllib.parse
        
        direccion_completa = f"{direccion}, {localidad}, {provincia}"
        direccion_codificada = urllib.parse.quote(direccion_completa)
        url = f"http://api.positionstack.com/v1/forward?access_key={self.api_key}&query={direccion_codificada}"
        response = requests.get(url)
        data = response.json()

        time.sleep(self.delay)  # Tiempo de espera entre solicitudes
        
        latitud = data['data'][0]['latitude']
        longitud = data['data'][0]['longitude']
        return latitud, longitud
