import pandas as pd
import sys
sys.path.append('C:/Users/Usuario/Desktop/OVS-caminero')
from geolocalizador import GeolocalizadorDatosGobar

# Configuraciones de pandas para visualizar los datos completos
pd.set_option('display.max_rows', None)
pd.set_option('display.max_columns', None)
pd.set_option('display.max_colwidth', None)
pd.set_option('display.expand_frame_repr', False)


# Cargar los datos del CSV con el delimitador correcto (coma en este caso)
df1 = pd.read_csv('C:/Users/Usuario/Desktop/OVS-caminero/direcciones_BsAs.csv', sep=',', keep_default_na=False, on_bad_lines='skip')


df1.columns = df1.columns.str.strip()  # Eliminar espacios en blanco
df1.rename(columns={'province;': 'province'}, inplace=True)  


# Crear una instancia del geolocalizador
geolocalizador = GeolocalizadorDatosGobar()
    

# Extraer las primeras 100 filas
df_muestra = df1.head(8000)

# Guardar la muestra en un nuevo archivo CSV
df_muestra.to_csv('C:/Users/Usuario/Desktop/OVS-caminero/direcciones_BsAs_muestra.csv', index=False)


# Normalizar cada dirección y crear una nueva columna con los resultados
df1['direccion_normalizada'] = df_muestra.apply(
    lambda row: geolocalizador.normalizar_direccion(row['address'], row['province'], row['district']),
    axis=1
)
# Guardar el DataFrame actualizado
df1.to_csv('C:/Users/Usuario/Desktop/OVS-caminero/direcciones_BsAs_normalizadas.csv', index=False)

estadisticas = geolocalizador.obtener_estadisticas()
print(f"Total de solicitudes: {estadisticas['total_solicitudes']}")
print(f"Solicitudes exitosas: {estadisticas['solicitudes_exitosas']}")