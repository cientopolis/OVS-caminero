# OVS-caminero

Este proyecto toma direcciones y las georreferencia utilizando diversas librerías de Python. Tenemos 3 scripts: El script 'procesar_direcciones.py' permite al usuario seleccionar un archivo csv y la API con la que desea georreferenciar las direcciones. El script 'georreferenciar_direcciones.py' se encarga de la conversión de direcciones a coordenadas geográficas por lotes utilizando la API Georef de DatosGobAr permitiendo al usuario seleccionar la cantidad de direcciones que quiere convertir a coordenadas. El script 'geolocalizar_con_delta.py' toma las direcciones y le suma 20 a las alturas de las mismas para la posterior georreferenciación.

## Requisitos

Tenes que tener Python 3.8 o superior instalado. Podés verificar tu versión de Python con:

python --version

- Dependencias listadas en el archivo `requirements.txt`:

    - pandas
    - geopy
    - tkinter
    - requests
    - pytz
    - numpy
    - y otras necesarias para el proyecto.

## Instalación

### 1. Clona el repositorio

Primero, clona el repositorio a tu máquina local:

git clone https://github.com/cientopolis/OVS-caminero
cd OVS-caminero

### 2. Crea un entorno virtual (opcional, pero recomendado)
Para evitar conflictos con otras librerías, creá un entorno virtual:

python3 -m venv venv

### 3. Activá el entorno virtual
Dependiendo de tu sistema operativo, activa el entorno virtual:

En Linux/macOS:

source venv/bin/activate

En Windows:

.\venv\Scripts\activate

### 4. Instalá las dependencias
Instalá las librerías necesarias listadas en el archivo requirements.txt:

pip install -r requirements.txt

### 5. Ejecutá el proyecto
Una vez instaladas las dependencias, ya se puede ejecutar el cualquiera de los tres scripts con:

python procesar_direcciones.py
python georreferenciar_direcciones.py
geolocalizar_con_delta.py

## Uso

### procesar_direcciones.py
Requiere que el csv ingresado contenga las columnas dirección, provincia y localidad.

### georreferenciar_direcciones.py
Requiere que el csv ingresado contenga las columnas address y district.

### geolocalizar_con_delta.py
Requiere que el csv ingresado contenga calle y altura.
