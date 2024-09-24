import pandas as pd
import csv
# Leer el archivo CSV
# Me estoy quedando solo con las direcciones que tienen como Provincia Buenos Aires 
# Y todas las de la lista (que tambien son de Buenos Aires)
df2 = pd.read_csv('C:/Users/Usuario/Downloads/direcciones.tsv.gz',sep='\t', keep_default_na=False,)


provincias_seleccionadas = [
    'Buenos Aires Interior',
    'Bs.As. G.B.A. Sur',
    'GBA Sur',
    'Buenos Aires (fuera de GBA)',
    'GBA Oeste',
    'GBA Norte',
    'Buenos Aires',
    'Bs.As. G.B.A. Oeste',
    'Bs.As. Costa Atlántica',
    'Bs.As. G.B.A. Norte',
    'Buenos Aires Costa Atlántica'
]

# Filtrar las filas que contienen provincias permitidas
df2_filtrado = df2[df2['province'].isin(provincias_seleccionadas)].copy()

# Actualizar la columna 'provincia'
df2_filtrado.loc[:, 'province'] = 'Buenos Aires'

# Guardar el DataFrame filtrado y actualizado en un nuevo archivo CSV
df2_filtrado.to_csv('C:/Users/Usuario/Desktop/OVS-Caminero/direcciones_BsAs.csv', index=False, encoding='utf-8')

