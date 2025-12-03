import urllib.request
import json
from datetime import datetime
import sys
import tkinter as tk
from tkinter import messagebox

FECHA_EXPIRACION = datetime(2026, 1, 10, 23, 59, 59)

def verificar_fecha_web():
    try:
        url = "http://worldtimeapi.org/api/timezone/America/Lima"
        with urllib.request.urlopen(url, timeout=5) as response:
            data = json.loads(response.read().decode())
            fecha_str = data['datetime']
            fecha_actual = datetime.fromisoformat(fecha_str.replace('Z', '+00:00'))
            return fecha_actual.replace(tzinfo=None)
    except:
        return None

def verificar_fecha_local():
    return datetime.now()

def validar_licencia():
    root = tk.Tk()
    root.withdraw()

    fecha_web = verificar_fecha_web()
    fecha_local = verificar_fecha_local()

    fecha_verificada = None

    if fecha_web is not None:
        fecha_verificada = fecha_web
    else:
        fecha_verificada = fecha_local

    if fecha_verificada > FECHA_EXPIRACION:
        messagebox.showerror(
            "Licencia Expirada",
            f"Esta aplicación ha expirado.\n\n"
            f"Fecha de expiración: {FECHA_EXPIRACION.strftime('%d/%m/%Y')}\n"
            f"Fecha actual: {fecha_verificada.strftime('%d/%m/%Y %H:%M:%S')}\n\n"
            f"Por favor contacte al administrador para renovar la licencia."
        )
        root.destroy()
        sys.exit(1)

    dias_restantes = (FECHA_EXPIRACION - fecha_verificada).days

    if dias_restantes <= 7 and dias_restantes >= 0:
        messagebox.showwarning(
            "Aviso de Expiración",
            f"La licencia de esta aplicación expirará en {dias_restantes} día(s).\n\n"
            f"Fecha de expiración: {FECHA_EXPIRACION.strftime('%d/%m/%Y')}\n"
            f"Por favor contacte al administrador."
        )

    root.destroy()
    return True

if __name__ == "__main__":
    if validar_licencia():
        print("Licencia válida. Puede usar la aplicación.")
