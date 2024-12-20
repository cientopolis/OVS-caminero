import tkinter as tk
from tkinter import filedialog, messagebox
import csv
from geolocalizador import (
    GeolocalizadorNominatim,
    GeolocalizadorDatosGobar,
    GeolocalizadorHere,
    GeolocalizadorLocationIQ,
    GeolocalizadorOpenCage,
    GeolocalizadorPositionStack,
)

def seleccionar_archivo_entrada():
    return filedialog.askopenfilename(
        title="Seleccionar archivo CSV de entrada",
        filetypes=[("Archivos CSV", "*.csv")],
    )

def seleccionar_archivo_salida():
    return filedialog.asksaveasfilename(
        title="Guardar archivo CSV de salida",
        defaultextension=".csv",
        filetypes=[("Archivos CSV", "*.csv")],
    )

def procesar_direcciones(input_csv, output_csv, geolocalizador):
    """
    Lee direcciones de un archivo CSV de entrada, las geolocaliza y guarda el resultado en un CSV de salida.
    """
    with open(input_csv, mode="r", newline="",encoding="latin-1") as csvfile:
        reader = csv.DictReader(csvfile, delimiter=";")
        fieldnames = ["direccion", "latitud", "longitud", "provincia", "localidad"]

        with open(output_csv, mode="w", newline="") as outputfile:
            writer = csv.DictWriter(outputfile, fieldnames=fieldnames)
            writer.writeheader()

            for row in reader:
                direccion = row["direccion"]
                provincia = row["provincia"]
                localidad = row["localidad"]
                try:
                    lat, lon = geolocalizador.obtener_coordenadas(direccion, provincia, localidad)
                    writer.writerow({
                        "direccion": direccion,
                        "latitud": lat,
                        "longitud": lon,
                        "provincia": provincia,
                        "localidad": localidad,
                    })
                except Exception:
                    writer.writerow({
                        "direccion": direccion,
                        "latitud": None,
                        "longitud": None,
                        "provincia": provincia,
                        "localidad": localidad,
                    })

def iniciar_interfaz():
    """
    Crea la interfaz gráfica para seleccionar archivos y procesar direcciones con un geolocalizador.
    """
    root = tk.Tk()
    root.title("Geolocalizador CSV")

    input_file = tk.StringVar()
    output_file = tk.StringVar()
    geolocalizador_nombre = tk.StringVar(value="Nominatim")  # Valor inicial predeterminado
    clave_api = tk.StringVar()
    delay = tk.DoubleVar(value=1.0)

    # Diccionario de geolocalizadores
    geolocalizadores = {
        "Nominatim": lambda: GeolocalizadorNominatim("MyApp", delay.get()),
        "DatosGobAr": lambda: GeolocalizadorDatosGobar(delay.get()),
        "Here": lambda: GeolocalizadorHere(clave_api.get(), delay.get()),
        "LocationIQ": lambda: GeolocalizadorLocationIQ(clave_api.get(), delay.get()),
        "OpenCage": lambda: GeolocalizadorOpenCage(clave_api.get(), delay.get()),
        "PositionStack": lambda: GeolocalizadorPositionStack(clave_api.get(), delay.get()),
    }

    geolocalizadores_con_clave = {"Here", "LocationIQ", "OpenCage", "PositionStack"}

    def seleccionar_input():
        archivo = seleccionar_archivo_entrada()
        if archivo:
            input_file.set(archivo)

    def seleccionar_output():
        archivo = seleccionar_archivo_salida()
        if archivo:
            output_file.set(archivo)

    def procesar():
        if not input_file.get():
            messagebox.showerror("Error", "Debe seleccionar un archivo de entrada.")
            return
        if not output_file.get():
            messagebox.showerror("Error", "Debe seleccionar un archivo de salida.")
            return
        if geolocalizador_nombre.get() in geolocalizadores_con_clave and not clave_api.get():
            messagebox.showerror("Error", "Debe ingresar la clave API para el geolocalizador seleccionado.")
            return

        # Obtener el geolocalizador seleccionado directamente
        selected_geolocalizador = geolocalizador_nombre.get()
        print(f"Geolocalizador seleccionado: '{selected_geolocalizador}'")  # Debugging line

        if selected_geolocalizador not in geolocalizadores:
            messagebox.showerror("Error", f"El geolocalizador '{selected_geolocalizador}' no está disponible.")
            return

        try:
            # Crear instancia del geolocalizador usando el diccionario
            geolocalizador = geolocalizadores[selected_geolocalizador]()

            # Verificar si la creación fue exitosa
            print(f"Geolocalizador '{selected_geolocalizador}' creado exitosamente.")  # Debugging line
        except KeyError as e:
            messagebox.showerror("Error", f"Geolocalizador '{selected_geolocalizador}' no soportado. Error: {e}")
            return
        except Exception as e:
            messagebox.showerror("Error", f"Error al configurar el geolocalizador: {str(e)}")
            return

        try:
            procesar_direcciones(input_file.get(), output_file.get(), geolocalizador)
            messagebox.showinfo("Completado", f"El procesamiento se completó. Archivo guardado en:\n{output_file.get()}")
        except Exception as e:
            messagebox.showerror("Error", f"Error al procesar las direcciones: {e}")

    def seleccionar_geolocalizador(nombre):
        geolocalizador_nombre.set(nombre)

    def cerrar():
        root.quit()  # Detiene el bucle principal de la interfaz
        root.destroy()  # Cierra la ventana correctamente

    # Diseño de la interfaz
    frame = tk.Frame(root, padx=10, pady=10)
    frame.grid(row=0, column=0, sticky="nsew")

    tk.Label(frame, text="Archivo de entrada:").grid(row=0, column=0, sticky="w")
    tk.Entry(frame, textvariable=input_file, width=40).grid(row=0, column=1)
    tk.Button(frame, text="Seleccionar", command=seleccionar_input).grid(row=0, column=2)

    tk.Label(frame, text="Archivo de salida:").grid(row=1, column=0, sticky="w")
    tk.Entry(frame, textvariable=output_file, width=40).grid(row=1, column=1)
    tk.Button(frame, text="Seleccionar", command=seleccionar_output).grid(row=1, column=2)

    tk.Label(frame, text="Seleccionar Geolocalizador:").grid(row=2, column=0, sticky="w")
    
    # Botones para seleccionar el geolocalizador
    botones_geolocalizadores = [
        ("Nominatim", "Nominatim"),
        ("DatosGobAr", "DatosGobAr"),
        ("Here", "Here"),
        ("LocationIQ", "LocationIQ"),
        ("OpenCage", "OpenCage"),
        ("PositionStack", "PositionStack")
    ]
    
    for idx, (label, nombre) in enumerate(botones_geolocalizadores):
        tk.Button(frame, text=label, command=lambda nombre=nombre: seleccionar_geolocalizador(nombre)).grid(row=2 + idx, column=1)

    tk.Label(frame, text="Clave API (si aplica):").grid(row=8, column=0, sticky="w")
    tk.Entry(frame, textvariable=clave_api, width=40).grid(row=8, column=1)

    tk.Label(frame, text="Delay (segundos):").grid(row=9, column=0, sticky="w")
    tk.Entry(frame, textvariable=delay, width=10).grid(row=9, column=1, sticky="w")

    tk.Button(frame, text="Procesar", command=procesar, bg="green", fg="white").grid(row=10, column=0, columnspan=3)

    # Botón de cerrar
    tk.Button(frame, text="Cerrar", command=cerrar, bg="red", fg="white").grid(row=11, column=0, columnspan=3)

    root.mainloop()

if __name__ == "__main__":
    iniciar_interfaz()
