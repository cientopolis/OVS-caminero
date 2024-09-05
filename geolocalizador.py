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
        # Implementa aquí la lógica para usar la API de datos.gob.ar
    
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
    