from abc import ABC, abstractmethod
import time 
import requests
import urllib.parse
import re
import json

    
class Geolocalizador(ABC):
    @abstractmethod
    def obtener_coordenadas(self, direccion, provincia, localidad):
        pass


class GeolocalizadorNominatim(Geolocalizador):
    def __init__(self, user_agent, delay):
        self.user_agent = user_agent
        self.delay = delay
    
    def obtener_coordenadas(self, direccion, localidad, provincia = None):

        direccion_codificada = urllib.parse.quote(direccion)
        localidad_codificada = urllib.parse.quote(localidad)
        url = f"https://nominatim.openstreetmap.org/search?street={direccion_codificada}&city={localidad_codificada}&format=json"
        headers = {'User-Agent': self.user_agent}

        response = requests.get(url, headers=headers)
        data = response.json()

        time.sleep(self.delay)  # Tiempo de espera entre solicitudes
        
        # Buscar la mejor dirección con base en la localidad
        mejor_direccion = self.buscar_mejor_direccion(data, localidad)
        if mejor_direccion:
            latitud = mejor_direccion['lat']
            longitud = mejor_direccion['lon']
            return latitud, longitud

        return None, None

    def buscar_mejor_direccion(self, data, localidad):
        """
        Busca el mejor resultado en los datos devueltos por Nominatim.
        """
        localidad = localidad.lower()

        return next(
            (
                direccion for direccion in data
                if localidad in direccion.get('display_name', '').lower()
            ),
            None  # Valor por defecto si no hay coincidencias
        )

class GeolocalizadorDatosGobar(Geolocalizador):
    def __init__(self, delay):
        self.delay = delay
        self.base_url = "https://apis.datos.gob.ar/georef/api/direcciones"
        
    def obtener_coordenadas(self, direccion, provincia = None, localidad = None):

        direccion_codificada = urllib.parse.quote(direccion)
        url = f"https://apis.datos.gob.ar/georef/api/direcciones?direccion={direccion_codificada}"
        response = requests.get(url)
        data = response.json()

        time.sleep(self.delay)  # Tiempo de espera entre solicitudes

        if data.get('direcciones'):
        # Busca la mejor dirección dentro de las devueltas
            mejor_direccion = self.buscar_mejor_direccion(
            direccion_original=(direccion, localidad),
            direcciones_api=data['direcciones']
        )
        if mejor_direccion:
            return mejor_direccion['latitud'], mejor_direccion['longitud']
        return None, None
    
    def procesar_direccion(self,direccion):
        """
        Realiza un preprocesamiento de la direccion para mandarla a la API.
        """
        direccion = direccion.replace('{', '').replace('}', '')
        direccion_limpia = re.sub(r'\b00+\b|\b0\b', '', direccion).strip()
        direccion_limpia = re.sub(r'[^\w\s]', '', direccion_limpia).strip()
        return direccion_limpia if direccion_limpia else None
    
    def normalizar_direcciones_por_lotes(self, direcciones):
        """
        Normaliza una lista de direcciones enviándolas en bloques de 1000 a la API de georef.
        """
        resultados = []

        for i in range(0, len(direcciones), 1000):
            lote = direcciones[i:i + 1000]
            payload = {"direcciones": []}

            # Procesar cada dirección en el lote
            for dir in lote:
                direccion_procesada = self.procesar_direccion(dir[0])
                if direccion_procesada:
                    direccion_data = {"direccion": direccion_procesada, "max": 5}
                    if dir[1]:  # Si la localidad es proporcionada, incluirla
                        direccion_data["localidad_censal"] = dir[1]
                    payload["direcciones"].append(direccion_data)

            # Si el lote no contiene direcciones, lo saltamos
            if not payload["direcciones"]:
                print(f"Lote {i // 1000 + 1} está vacío después del procesamiento.")
                continue

            # Hacer la solicitud a la API
            try:
                response = requests.post(
                    self.base_url,
                    headers={'Content-Type': 'application/json'},
                    data=json.dumps(payload)
                )

                if response.status_code == 200:
                    data = response.json()
                    resultados.extend(data.get('resultados', []))
                else:
                    print(f"Error en el lote {i // 1000 + 1}: {response.status_code}, Mensaje: {response.text}")
                    print(f"Lote que causó el error: {json.dumps(payload, indent=2)}")
            except requests.exceptions.RequestException as e:
                print(f"Excepción en el lote {i // 1000 + 1}: {e}")

        return resultados    
    
    def buscar_mejor_direccion(self, direccion_original, direcciones_api):
        """
        Para una dirección busca la mejor direccion entre la lista que devuelve la API.
        Utiliza un generador con next() para encontrar la mejor dirección.
        """
        distrito_original = direccion_original[1].lower()  # Se asume que el indice 1 es la localidad original
    
        # Buscar la mejor dirección usando un generador con next
        mejor_direccion = next(
            (
                {
                    'direccion': dir_api.get('nomenclatura'),
                    'localidad': dir_api.get('localidad_censal', {}).get('nombre'),
                    'latitud': dir_api.get('ubicacion', {}).get('lat'),
                    'longitud': dir_api.get('ubicacion', {}).get('lon'),
                }
                for dir_api in direcciones_api
                if dir_api.get('localidad_censal', {}).get('nombre', '').lower() == distrito_original
            ),
            None  # Valor por defecto si no se encuentra una coincidencia
        )
    
        return mejor_direccion


    
    def procesar_direcciones(self, direcciones):
        """
        Procesa una lista de direcciones, obteniendo la mejor dirección por cada una a traves del metodo buscar_mejor_direccion.
        """
        resultados_normalizados = self.normalizar_direcciones_por_lotes(direcciones)
        normalizadas = []

        for i, resultado in enumerate(resultados_normalizados):
            if resultado['cantidad'] > 0:
                direcciones_api = resultado['direcciones']
                direccion_original = direcciones[i]
                mejor_direccion = self.buscar_mejor_direccion(direccion_original, direcciones_api)

                if mejor_direccion:
                    normalizadas.append(mejor_direccion)
                    
        return normalizadas
        
    
class GeolocalizadorHere(Geolocalizador):
    def __init__(self, api_key, delay):
        self.api_key = api_key
        self.delay = delay

    def obtener_coordenadas(self, direccion, provincia, localidad):

        direccion_completa = f"{direccion}, {localidad}, {provincia}"
        direccion_codificada = urllib.parse.quote(direccion_completa)
        url = f"https://geocode.search.hereapi.com/v1/geocode?q={direccion_codificada}&apiKey={self.api_key}"
        response = requests.get(url)
        data = response.json()

        time.sleep(self.delay)  # Tiempo de espera entre solicitudes
        
        if not data.get('items'):
            raise Exception("No se encontraron resultados para la dirección proporcionada.")

        # Buscar la mejor dirección
        mejor_direccion = self.buscar_mejor_direccion(data['items'], localidad)

        if mejor_direccion:
            latitud = mejor_direccion['position']['lat']
            longitud = mejor_direccion['position']['lng']
            return latitud, longitud
        else:
            raise Exception("No se encontró una dirección que coincida con la localidad proporcionada.")        

    def buscar_mejor_direccion(self, data, localidad):
        """
        Busca la primera dirección que coincida con la localidad en los resultados.
        """
        localidad = localidad.lower()
        
        for direccion in data:
            # Extraer la localidad del resultado actual
            localidad_resultado = direccion.get('address', {}).get('city', '').lower()
            
            if localidad and localidad == localidad_resultado:
                return direccion  # Devolver el primer resultado coincidente

        return None  # Si no hay coincidencias, devuelve None
    
class GeolocalizadorLocationIQ(Geolocalizador):
    def __init__(self, api_key, delay):
        self.api_key = api_key
        self.delay = delay

    def obtener_coordenadas(self, direccion, provincia, localidad):

        
        direccion_completa = f"{direccion}, {localidad}, {provincia}"
        direccion_codificada = urllib.parse.quote(direccion_completa)
        url = f"https://us1.locationiq.com/v1/search.php?key={self.api_key}&q={direccion_codificada}&format=json"
        response = requests.get(url)
        data = response.json()

        time.sleep(self.delay)  # Tiempo de espera entre solicitudes
        
        # Filtrar y obtener la mejor dirección
        mejor_direccion = self.buscar_mejor_direccion(data, localidad)
        if mejor_direccion:
            latitud = mejor_direccion['lat']
            longitud = mejor_direccion['lon']
            return latitud, longitud
        return None, None
    
    def buscar_mejor_direccion(self, data, localidad):
        """
        Busca la mejor dirección en los resultados de LocationIQ que coincida con la localidad esperada.
        """
        localidad = localidad.lower() if localidad else None

        # Filtrar por coincidencia en 'address' dentro de los resultados devueltos
        mejor_direccion = next(
            (
                direccion for direccion in data
                if localidad in direccion.get('display_name', '').lower()
            ),
            None  # Si no hay coincidencias, devuelve None
        )
        return mejor_direccion


class GeolocalizadorOpenCage(Geolocalizador):
    def __init__(self, api_key, delay):
        self.api_key = api_key
        self.delay = delay

    def obtener_coordenadas(self, direccion, provincia, localidad):

        direccion_completa = f"{direccion}, {localidad}, {provincia}"
        direccion_codificada = urllib.parse.quote(direccion_completa)
        url = f"https://api.opencagedata.com/geocode/v1/json?q={direccion_codificada}&key={self.api_key}"
        response = requests.get(url)
        data = response.json()

        time.sleep(self.delay)  # Tiempo de espera entre solicitudes
        
        # Filtrar y obtener la mejor dirección
        mejor_direccion = self.buscar_mejor_direccion(data.get('results', []), localidad)
        if mejor_direccion:
            latitud = mejor_direccion['geometry']['lat']
            longitud = mejor_direccion['geometry']['lng']
            return latitud, longitud
        return None, None
    
    def buscar_mejor_direccion(self, resultados, localidad):
        """
        Busca la mejor dirección en los resultados de OpenCage que coincida con la localidad esperada.
        """
        localidad = localidad.lower() 

        # Filtrar por coincidencia en 'components' dentro de los resultados devueltos
        mejor_direccion = next(
            (
                resultado for resultado in resultados
                if localidad in resultado.get('formatted', '').lower()
            ),
            None  # Si no hay coincidencias, devuelve None
        )
        return mejor_direccion

class GeolocalizadorPositionStack(Geolocalizador):
    def __init__(self, api_key, delay):
        self.api_key = api_key
        self.delay = delay

    def obtener_coordenadas(self, direccion, provincia, localidad):

        direccion_completa = f"{direccion}, {localidad}, {provincia}"
        direccion_codificada = urllib.parse.quote(direccion_completa)
        url = f"http://api.positionstack.com/v1/forward?access_key={self.api_key}&query={direccion_codificada}"
        response = requests.get(url)
        data = response.json()

        time.sleep(self.delay)  # Tiempo de espera entre solicitudes
        
        # Verificamos que la clave data de PositionStack exista y no esté vacía para que no haya error
        if 'data' in data and data['data']:
            mejor_direccion = self.buscar_mejor_direccion(data['data'], localidad)
            if mejor_direccion:
                return mejor_direccion['latitude'], mejor_direccion['longitude']
        
        return None, None
    def buscar_mejor_direccion(self, resultados, localidad):
        """
        Busca la mejor dirección basada en la localidad especificada.
        """
        localidad = localidad.lower()
        
        # Filtra los resultados que coincidan con la localidad
        mejor_direccion = next(
            (resultado for resultado in resultados
             if localidad and localidad in (resultado.get('locality', '').lower() or
                                            resultado.get('region', '').lower())),
            None  # Devuelve None si no hay coincidencias
        )

        # Devuelve el mejor resultado o el primero si no hay coincidencias exactas
        return mejor_direccion