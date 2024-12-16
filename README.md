# OVS-caminero

Este proyecto toma direcciones y las georreferencia utilizando diversas librerías de Python. Tenemos 3 scripts: El script 'procesar_direcciones.py' permite al usuario seleccionar un archivo csv y la API con la que desea georreferenciar las direcciones. El script 'georreferenciar_direcciones.py' se encarga de la conversión de direcciones a coordenadas geográficas por lotes utilizando la API Georef de DatosGobAr permitiendo al usuario seleccionar la cantidad de direcciones que quiere convertir a coordenadas. El script 'geolocalizar_con_delta.py' toma las direcciones y le suma 20 a las alturas de las mismas para la posterior georreferenciación.

## Requisitos

Tenes que tener Python 3.8 o superior instalado. Podés verificar tu versión de Python con:

```bash
python --version

- Dependencias listadas en el archivo `requirements.txt`:

    - pandas
    - geopy
    - tkinter
    - requests
    - pytz
    - numpy
    - y otras necesarias para el proyecto.

## **Instalación**

Sigue estos pasos para configurar el entorno y ejecutar el proyecto.

### 1. Clona el repositorio

Primero, clona el repositorio a tu máquina local:

```bash
git clone https://github.com/tu_usuario/tu_repositorio.git
cd tu_repositorio
