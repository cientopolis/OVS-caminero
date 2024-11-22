import pandas as pd
import tkinter as tk
from tkinter import filedialog, simpledialog
from geolocalizador import GeolocalizadorDatosGobar

# Función para seleccionar un archivo de entrada
def seleccionar_archivo_entrada():
    root = tk.Tk()
    root.withdraw()  # Ocultar la ventana principal
    archivo = filedialog.askopenfilename(title="Seleccionar archivo CSV de direcciones", filetypes=[("CSV files", "*.csv")])
    return archivo

# Función para seleccionar un archivo de salida
def seleccionar_archivo_salida():
    root = tk.Tk()
    root.withdraw()  # Ocultar la ventana principal
    archivo = filedialog.asksaveasfilename(title="Guardar archivo CSV de direcciones normalizadas", defaultextension=".csv", filetypes=[("CSV files", "*.csv")])
    return archivo

# Función para pedir al usuario el número de direcciones a procesar
def obtener_numero_direcciones_maximas():
    root = tk.Tk()
    root.withdraw()  # Ocultar la ventana principal
    max_direcciones = simpledialog.askinteger("Cantidad de direcciones", "¿Cuántas direcciones deseas procesar?", minvalue=1)
    return max_direcciones

# Seleccionar el archivo de entrada
input_file = seleccionar_archivo_entrada()
if not input_file:
    print("No se seleccionó un archivo de entrada. El script se detendrá.")
    exit()

# Seleccionar el archivo de salida
output_file = seleccionar_archivo_salida()
if not output_file:
    print("No se seleccionó un archivo de salida. El script se detendrá.")
    exit()

# Cargar los datos desde el archivo CSV de entrada
df = pd.read_csv(input_file, sep=',', keep_default_na=False, on_bad_lines='skip')
df.columns = df.columns.str.strip()

# Filtrar direcciones no nulas y no vacías
df = df[df['address'].notna() & (df['address'].str.strip() != '')]
direcciones = df[['address', 'district']].dropna().values.tolist()

# Obtener el número de direcciones a procesar
max_direcciones = obtener_numero_direcciones_maximas()

# Limitar las direcciones a procesar
direcciones = direcciones[:max_direcciones] if max_direcciones else direcciones

# Crear instancia del geolocalizador
geolocalizador = GeolocalizadorDatosGobar(0)

# Procesar direcciones
normalizadas = geolocalizador.procesar_direcciones(direcciones)

# Convertir el resultado a DataFrame
df_normalizadas = pd.DataFrame(normalizadas)

# Escribir el resultado en un nuevo archivo CSV
df_normalizadas.to_csv(output_file, index=False)

print(f"Direcciones normalizadas guardadas en: {output_file}")