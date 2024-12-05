import pandas as pd
import tkinter as tk
from tkinter import filedialog, simpledialog, messagebox
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
def obtener_numero_direcciones_maximas(total_direcciones):
    root = tk.Tk()
    root.withdraw()  # Ocultar la ventana principal
    
    # Preguntar al usuario si desea procesar todo el archivo o un número limitado
    respuesta = messagebox.askyesno(
        "Procesar todas las direcciones",
        f"El archivo contiene {total_direcciones} direcciones. ¿Querés procesarlas todas?"
    )
    
    if respuesta:  # Si el usuario elige procesar todo
        return total_direcciones  # Devolvemos el total
    
    # Si no, pedimos un número específico
    max_direcciones = simpledialog.askinteger(
        "Cantidad de direcciones",
        "¿Cuántas direcciones querés procesar?",
        minvalue=1,
        maxvalue=total_direcciones
    )
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
direcciones = df[['address', 'district']].dropna().drop_duplicates().values.tolist()


# Calcular total de direcciones disponibles
total_direcciones = len(direcciones)

# Obtener el número de direcciones a procesar
max_direcciones = obtener_numero_direcciones_maximas(total_direcciones)

# Limitar las direcciones a procesar a lo que quiera el usuario
direcciones = direcciones[:max_direcciones] if max_direcciones else direcciones

# Crear instancia del geolocalizador
geolocalizador = GeolocalizadorDatosGobar(0)

# Procesar direcciones
normalizadas = geolocalizador.procesar_direcciones(direcciones)


# Convertir el resultado a DataFrame
df_normalizadas = pd.DataFrame(normalizadas)
df_normalizadas = df_normalizadas.drop_duplicates()

# Escribir el resultado en un nuevo archivo CSV
df_normalizadas.to_csv(output_file, index=False)

# Mostrar un mensaje de confirmación
root = tk.Tk()
root.withdraw()  # Ocultar la ventana principal
messagebox.showinfo("Finalizado", f"Direcciones con coordenadas guardadas en: {output_file}")

