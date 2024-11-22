from cx_Freeze import setup, Executable

setup(
    name="Georreferenciar Direcciones",
    version="1.0",
    description="Georreferenciar Direcciones",
    executables=[Executable("georreferenciar_direcciones.py", base="Win32GUI")]
)
