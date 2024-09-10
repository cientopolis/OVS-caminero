from abc import ABC, abstractmethod

class Geolocalizador(ABC):
    @abstractmethod
    def obtener_coordenadas(self, direccion,provincia,localidad):
        pass

class GeolocalizadorNominatim(Geolocalizador):
    def __init__(self, user_agent):
        self.user_agent= user_agent

    def obtener_coordenadas(self, direccion,provincia,localidad):
        # Implementa aquí la lógica para usar la API Nominatim
       
        import requests
        import urllib.parse
        
        direccion_codificada = urllib.parse.quote(direccion)
        url = f"https://nominatim.openstreetmap.org/search?street={direccion_codificada}&city={localidad}&format=json"
        response = requests.get(url)
        data = response.json()
        latitud = data[0]['lat']
        longitud = data[0]['lon']
        return latitud, longitud

class GeolocalizadorDatosGobar(Geolocalizador):
    def __init__(self):
        pass

    def obtener_coordenadas(self, direccion,provincia,localidad):
        # Implementa la lógica para usar la API de datos.gob.ar
    
        import requests
        import urllib.parse
        direccion_codificada = urllib.parse.quote(direccion)
        url = f"https://apis.datos.gob.ar/georef/api/direcciones?direccion={direccion_codificada}&provincia={provincia}&localidad={localidad}"
        response = requests.get(url)
        data = response.json()
        return data['direcciones'][0]['ubicacion']['lat'],data['direcciones'][0]['ubicacion']['lon']

class GeolocalizadorHere(Geolocalizador):
    def __init__(self, api_key):
        self.api_key = api_key

    def obtener_coordenadas(self, direccion, provincia, localidad):
        # Implementa la lógica para usar la API de Here
        
        import requests
        import urllib.parse

        direccion_completa = f"{direccion}, {localidad}, {provincia}"
        direccion_codificada = urllib.parse.quote(direccion_completa)
        url = f"https://geocode.search.hereapi.com/v1/geocode?q={direccion_codificada}&apiKey={self.api_key}"
        
        response = requests.get(url)
        data = response.json()
        latitud = data['items'][0]['position']['lat']
        longitud = data['items'][0]['position']['lng']
        return latitud, longitud
    
class GeolocalizadorLocationIQ(Geolocalizador):
    def __init__(self, api_key):
        self.api_key = api_key

    def obtener_coordenadas(self, direccion, provincia, localidad):
        # Implementa la lógica para usar la API de LocationIQ
        
        import requests
        import urllib.parse
        
        direccion_completa = f"{direccion}, {localidad}, {provincia}"
        direccion_codificada = urllib.parse.quote(direccion_completa)
        url = f"https://us1.locationiq.com/v1/search.php?key={self.api_key}&q={direccion_codificada}&format=json"

        # Hacer la solicitud a la API
        response = requests.get(url)
        data = response.json()
        latitud = data[0]['lat']
        longitud = data[0]['lon']
        return latitud, longitud
    
class GeolocalizadorOpenCage(Geolocalizador):
    
    def __init__(self, api_key):
        self.api_key = api_key

    def obtener_coordenadas(self, direccion, provincia, localidad):
        # Implementa la lógica para usar la API de OpenCage
        
        import requests
        import urllib.parse
        direccion_completa = f"{direccion}, {localidad}, {provincia}"
        direccion_codificada = urllib.parse.quote(direccion_completa)
        url = f"https://api.opencagedata.com/geocode/v1/json?q={direccion_codificada}&key={self.api_key}"
        
        # Hacer la solicitud a la API
        response = requests.get(url)
        data = response.json()
        latitud = data['results'][0]['geometry']['lat']
        longitud = data['results'][0]['geometry']['lng']
        return latitud, longitud

class GeolocalizadorPositionStack(Geolocalizador):
    
    def __init__(self, api_key):
        self.api_key = api_key

    def obtener_coordenadas(self, direccion, provincia, localidad):
        # Implementa la lógica para usar la API PositionStack
        
        import requests
        import urllib.parse
        
        direccion_completa = f"{direccion}, {localidad}, {provincia}"
        direccion_codificada = urllib.parse.quote(direccion_completa)
        url = f"http://api.positionstack.com/v1/forward?access_key={self.api_key}&query={direccion_codificada}"
        
        # Hacer la solicitud a la API
        response = requests.get(url)
        data = response.json()
        latitud = data['data'][0]['latitude']
        longitud = data['data'][0]['longitude']
        return latitud, longitud
        