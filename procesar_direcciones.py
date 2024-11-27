import csv
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from geolocalizador import (
    GeolocalizadorNominatim,
    GeolocalizadorDatosGobar,
    GeolocalizadorHere,
    GeolocalizadorLocationIQ,
    GeolocalizadorOpenCage,
    GeolocalizadorPositionStack,
)
import threading

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

def procesar_direcciones(input_csv, output_csv, geolocalizador, update_status_callback):
    """
    Lee direcciones de un archivo CSV de entrada, las geolocaliza y guarda el resultado en un CSV de salida.
    """
    with open(input_csv, mode="r", newline="", encoding="latin-1") as csvfile:
        reader = csv.DictReader(csvfile, delimiter=";")
        fieldnames = ["direccion", "latitud", "longitud", "provincia", "localidad"]

        with open(output_csv, mode="w", newline="") as outputfile:
            writer = csv.DictWriter(outputfile, fieldnames=fieldnames)
            writer.writeheader()

            for i, row in enumerate(reader):
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
                # Actualizar el progreso de procesamiento
                update_status_callback(f"Procesando dirección {i + 1}...")

def iniciar_interfaz():
    """
    Crea la interfaz gráfica para seleccionar archivos y procesar direcciones con un geolocalizador.
    """
    root = tk.Tk()
    root.title("Geolocalizador con APIS")

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

    # Crear un widget para mostrar el estado de la carga
    status_label = tk.Label(root, text="", fg="blue")
    status_label.grid(row=6, column=0, columnspan=3)

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

        try:
            # Deshabilitar el botón de "Procesar" para evitar múltiples clics
            procesar_button.config(state="disabled")
            status_label.config(text="Cargando... Espere por favor...")

            # Crear instancia del geolocalizador usando el diccionario
            geolocalizador = geolocalizadores[geolocalizador_nombre.get()]()
        except KeyError:
            messagebox.showerror("Error", f"Geolocalizador '{geolocalizador_nombre.get()}' no soportado.")
            procesar_button.config(state="normal")
            return
        except Exception as e:
            messagebox.showerror("Error", f"Error al configurar el geolocalizador: {e}")
            procesar_button.config(state="normal")
            return

        # Usar threading para no bloquear la interfaz gráfica
        def procesar_en_hilo():
            try:
                procesar_direcciones(input_file.get(), output_file.get(), geolocalizador, update_status)
                messagebox.showinfo("Completado", f"El procesamiento se completó. Archivo guardado en:\n{output_file.get()}")
            except Exception as e:
                messagebox.showerror("Error", f"Error al procesar las direcciones: {e}")
            finally:
                # Restaurar el estado de la interfaz después de finalizar
                procesar_button.config(state="normal")
                status_label.config(text="")

        def update_status(status_text):
            # Esta función actualiza el estado del procesamiento
            status_label.config(text=status_text)

        # Iniciar el proceso en un hilo separado para que la interfaz gráfica no se congele
        threading.Thread(target=procesar_en_hilo, daemon=True).start()

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

    tk.Label(frame, text="Geolocalizador:").grid(row=2, column=0, sticky="w")
    ttk.Combobox(frame, textvariable=geolocalizador_nombre, values=list(geolocalizadores.keys()), state="readonly").grid(row=2, column=1)

    tk.Label(frame, text="Clave API (si aplica):").grid(row=3, column=0, sticky="w")
    tk.Entry(frame, textvariable=clave_api, width=40).grid(row=3, column=1)

    tk.Label(frame, text="Delay (segundos):").grid(row=4, column=0, sticky="w")
    tk.Entry(frame, textvariable=delay, width=10).grid(row=4, column=1, sticky="w")

    # Botón para procesar
    procesar_button = tk.Button(frame, text="Procesar", command=procesar, bg="green", fg="white")
    procesar_button.grid(row=5, column=0, columnspan=3)

    # Botón de cerrar
    tk.Button(frame, text="Cerrar", command=cerrar, bg="red", fg="white").grid(row=7, column=0, columnspan=3)

    root.mainloop()

if __name__ == "__main__":
    iniciar_interfaz()

