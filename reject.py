import tkinter as tk
from tkinter import messagebox
import subprocess
import threading
import re
from datetime import datetime
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg


class PingApp:
    def __init__(self, master, log_area, promedios_area, results):
        # Diccionario de IPs y nombres de equipos
        self.nombres_equipos = {
            "10.72.14.81": "EX 002",
            "10.72.14.82": "EX 003",
            "10.72.14.83": "EX 004",
            "10.72.14.84": "EX 005",
            "10.72.14.85": "EX 006",
            "10.72.14.86": "EX 066",
            "10.72.14.87": "EX 070",
            "10.72.14.88": "EX 071"
        }

        self.master = master
        self.log_area = log_area
        self.promedios_area = promedios_area
        self.results = results  # Lista para almacenar los resultados
        self.proceso_ping = None
        self.hora_inicio = None
        self.correctos = 0
        self.perdidos = 0
        self.ip = ""

        self.label = tk.Label(master, text="Ingresa la IP a hacer ping:")
        self.label.pack(pady=10)

        self.entry_ip = tk.Entry(master, width=30)
        self.entry_ip.pack(pady=10)

        self.btn_iniciar = tk.Button(master, text="Iniciar Ping", command=self.iniciar_ping)
        self.btn_iniciar.pack(pady=10)

        self.btn_detener = tk.Button(master, text="Detener Ping", command=self.detener_ping, state=tk.DISABLED)
        self.btn_detener.pack(pady=10)

        self.output_text = tk.Text(master, height=15, width=70)
        self.output_text.pack(pady=10)

    def iniciar_ping(self):
        if self.proceso_ping is not None:
            messagebox.showerror("Error", "Ya hay un ping en curso.")
            return

        self.ip = self.entry_ip.get()
        if not self.ip:
            messagebox.showerror("Error", "Por favor ingrese una IP válida.")
            return

        # Buscar nombre en el diccionario
        nombre_equipo = self.nombres_equipos.get(self.ip, "Desconocido")

        self.correctos = 0
        self.perdidos = 0
        self.hora_inicio = datetime.now()

        self.btn_detener.config(state=tk.NORMAL)

        self.output_text.delete(1.0, tk.END)
        self.output_text.insert(tk.END, f"Iniciando ping a {self.ip} ({nombre_equipo})...\n")

        def ping():
            self.proceso_ping = subprocess.Popen(
                ["ping", self.ip, "-t"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                creationflags=subprocess.CREATE_NO_WINDOW
            )

            try:
                while True:
                    line = self.proceso_ping.stdout.readline()
                    if line == '':
                        break

                    self.output_text.insert(tk.END, line)
                    self.output_text.yview(tk.END)

                    match = re.search(r"tiempo[=<](\d+)ms", line)
                    if match:
                        tiempo = int(match.group(1))
                        if tiempo < 50:
                            self.correctos += 1
                        else:
                            self.perdidos += 1
                    elif "Tiempo de espera agotado" in line or "Request timed out" in line:
                        self.perdidos += 1
            finally:
                self.proceso_ping = None

        threading.Thread(target=ping, daemon=True).start()

    def detener_ping(self):
        if self.proceso_ping is not None:
            self.proceso_ping.terminate()
            hora_fin = datetime.now()
            duracion = hora_fin - self.hora_inicio

            # Obtener el nombre del equipo si existe
            nombre_equipo = self.nombres_equipos.get(self.ip, "Desconocido")

            self.output_text.insert(tk.END, "\nProceso de ping detenido por el usuario.\n")

            total_paquetes = self.correctos + self.perdidos
            if total_paquetes > 0:
                porcentaje_correctos = (self.correctos / total_paquetes) * 100
                porcentaje_perdidos = (self.perdidos / total_paquetes) * 100
            else:
                porcentaje_correctos = 0
                porcentaje_perdidos = 0

            self.output_text.insert(tk.END, f"\nDesde: {self.hora_inicio.strftime('%Y-%m-%d %H:%M:%S')}\n")
            self.output_text.insert(tk.END, f"Hasta: {hora_fin.strftime('%Y-%m-%d %H:%M:%S')}\n")
            self.output_text.insert(tk.END, f"% < 50ms: {porcentaje_correctos:.2f}%\n")
            self.output_text.insert(tk.END, f"% >= 50ms o sin respuesta: {porcentaje_perdidos:.2f}%\n")

            self.log_area.insert(tk.END, f"--- Resultados de Ping para IP: {self.ip} ({nombre_equipo}) ---\n")
            self.log_area.insert(tk.END, f"Desde: {self.hora_inicio.strftime('%Y-%m-%d %H:%M:%S')}\n")
            self.log_area.insert(tk.END, f"Hasta: {hora_fin.strftime('%Y-%m-%d %H:%M:%S')}\n")
            self.log_area.insert(tk.END, f"% < 50ms: {porcentaje_correctos:.2f}%\n")
            self.log_area.insert(tk.END, f"% >= 50ms o sin respuesta: {porcentaje_perdidos:.2f}%\n\n")

            # Agregar resultados a la lista global
            self.results.append({
                'ip': self.ip,
                'nombre': self.nombres_equipos.get(self.ip, 'Desconocido'),
                'correctos': porcentaje_correctos,
                'perdidos': porcentaje_perdidos
            })

            self.btn_detener.config(state=tk.DISABLED)

            self.proceso_ping = None
        else:
            self.output_text.insert(tk.END, "\nNo hay un ping en curso para detener.\n")


def limpiar_log():
    log_area.delete(1.0, tk.END)
    promedios_area.delete(1.0, tk.END)


def calcular_promedio():
    log_text = log_area.get(1.0, tk.END)
    total_correctos = 0
    total_perdidos = 0
    conteos = 0

    for line in log_text.splitlines():
        if "--- Resultados de Ping para IP:" in line:
            conteos += 1
        if "% < 50ms" in line:
            match = re.search(r"% < 50ms: (\d+.\d+)%", line)
            if match:
                total_correctos += float(match.group(1))
        if "% >= 50ms o sin respuesta" in line:
            match = re.search(r"% >= 50ms o sin respuesta: (\d+.\d+)%", line)
            if match:
                total_perdidos += float(match.group(1))

    if conteos > 0:
        promedio_correctos = total_correctos / conteos
        promedio_perdidos = total_perdidos / conteos
        promedios_area.delete(1.0, tk.END)
        promedios_area.insert(tk.END, f"Promedio % < 50ms: {promedio_correctos:.2f}%\n")
        promedios_area.insert(tk.END, f"Promedio % >= 50ms: {promedio_perdidos:.2f}%\n")
    else:
        promedios_area.delete(1.0, tk.END)
        promedios_area.insert(tk.END, "No hay datos suficientes.\n")


def generar_grafico():
    if not results:
        messagebox.showerror("Error", "No hay resultados para mostrar.")
        return

    # Datos para graficar
    ips = [result['ip'] for result in results]
    nombres = [result['nombre'] for result in results]
    correctos = [result['correctos'] for result in results]
    perdidos = [result['perdidos'] for result in results]

    fig, ax = plt.subplots()

    bar_width = 0.35
    index = range(len(ips))

    bar1 = ax.bar(index, correctos, bar_width, label='% < 50ms')
    bar2 = ax.bar([i + bar_width for i in index], perdidos, bar_width, label='% >= 50ms o sin respuesta')

    ax.set_xlabel('IP')
    ax.set_ylabel('Porcentaje')
    ax.set_title('Resultados de Ping por IP')
    ax.set_xticks([i + bar_width / 2 for i in index])
    ax.set_xticklabels(nombres, rotation=45, ha='right')
    ax.legend()

    # Mostrar el gráfico en Tkinter
    new_window = tk.Toplevel(ventana_principal)
    new_window.title("Gráfico de Resultados de Ping")
    canvas = FigureCanvasTkAgg(fig, master=new_window)
    canvas.draw()
    canvas.get_tk_widget().pack()

def generar_nueva_ventana():
    nueva_ventana = tk.Toplevel(ventana_principal)
    nueva_app = PingApp(nueva_ventana, log_area, promedios_area, results)


ventana_principal = tk.Tk()
ventana_principal.title("Gestión de Ventanas de Ping")

results = []  # Lista global para almacenar los resultados de todas las ventanas

log_area = tk.Text(ventana_principal, height=10, width=70)
log_area.pack(pady=10)

promedios_area = tk.Text(ventana_principal, height=5, width=70)
promedios_area.pack(pady=10)

btn_limpiar = tk.Button(ventana_principal, text="Limpiar Log y Resultados", command=limpiar_log)
btn_limpiar.pack(pady=10)

btn_calcular_promedio = tk.Button(ventana_principal, text="Calcular Promedio de Pings", command=calcular_promedio)
btn_calcular_promedio.pack(pady=10)

btn_generar_ventana = tk.Button(ventana_principal, text="Generar Nueva Ventana de Ping", command=generar_nueva_ventana)
btn_generar_ventana.pack(pady=10)

btn_generar_grafico = tk.Button(ventana_principal, text="Generar Gráfico de Resultados", command=generar_grafico)
btn_generar_grafico.pack(pady=10)

ventana_principal.mainloop()
