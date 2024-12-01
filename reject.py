import tkinter as tk
from tkinter import messagebox
import subprocess
import threading
import re
from datetime import datetime
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import os


class PingApp:
    def __init__(self, master, log_area, promedios_area, results):
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
        self.results = results
        self.proceso_ping = None
        self.hora_inicio = None
        self.correctos = 0
        self.perdidos = 0
        self.ip = ""

        self.label = tk.Label(master, text="Ingresa la IP a hacer ping:")
        self.label.pack(pady=10)

        self.entry_ip = tk.Entry(master, width=30)
        self.entry_ip.insert(0, "10.72.14.")  # Establecer el valor predeterminado
        self.entry_ip.pack(pady=10)

        # Etiqueta para mostrar el nombre de la excavadora
        self.label_nombre_equipo = tk.Label(master, text="Equipo: Desconocido")
        self.label_nombre_equipo.pack(pady=10)

        self.btn_iniciar = tk.Button(master, text="Iniciar Ping", command=self.iniciar_ping)
        self.btn_iniciar.pack(pady=10)

        self.btn_detener = tk.Button(master, text="Detener Ping", command=self.detener_ping, state=tk.DISABLED)
        self.btn_detener.pack(pady=10)

        self.output_text = tk.Text(master, height=15, width=70)
        self.output_text.pack(pady=10)

        # Interceptar el cierre de la ventana
        self.master.protocol("WM_DELETE_WINDOW", self.on_closing)

    def on_closing(self):
        # Al cerrar la ventana principal, detenemos el ping si está en curso
        if self.proceso_ping is not None:
            self.proceso_ping.terminate()
            self.output_text.insert(tk.END, "\nPing detenido al cerrar la ventana.\n")
        self.master.destroy()

    def iniciar_ping(self):
        if self.proceso_ping is not None:
            messagebox.showerror("Error", "Ya hay un ping en curso.")
            return

        self.ip = self.entry_ip.get()
        if not self.ip:
            messagebox.showerror("Error", "Por favor ingrese una IP válida.")
            return

        nombre_equipo = self.nombres_equipos.get(self.ip, "Desconocido")

        # Actualizar el texto con el nombre de la excavadora
        self.label_nombre_equipo.config(text=f"Equipo: {nombre_equipo}")

        self.correctos = 0
        self.perdidos = 0
        self.hora_inicio = datetime.now()

        self.btn_detener.config(state=tk.NORMAL)

        self.output_text.delete(1.0, tk.END)
        self.output_text.insert(tk.END, f"Iniciando ping a {self.ip} ({nombre_equipo})...\n")

        def ping():
            creation_flags = 0
            if os.name == 'nt':  # Windows
                creation_flags = subprocess.CREATE_NO_WINDOW

            self.proceso_ping = subprocess.Popen(
                ["ping", self.ip, "-t"] if os.name == 'nt' else ["ping", self.ip],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                creationflags=creation_flags
            )

            try:
                while True:
                    line = self.proceso_ping.stdout.readline()
                    if line == '':
                        break

                    self.output_text.insert(tk.END, line)
                    self.output_text.yview(tk.END)

                    match = re.search(r"(time|tiempo)[=<](\d+)ms", line, re.IGNORECASE)
                    if match:
                        tiempo = int(match.group(2))
                        if tiempo < 50:
                            self.correctos += 1
                        else:
                            self.perdidos += 1
                    elif "tiempo de espera agotado" in line.lower() or "request timed out" in line.lower():
                        self.perdidos += 1
            finally:
                self.proceso_ping = None

        threading.Thread(target=ping, daemon=True).start()

    def detener_ping(self):
        if self.proceso_ping is not None:
            self.proceso_ping.terminate()
            hora_fin = datetime.now()
            duracion = hora_fin - self.hora_inicio

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

    ips = [result['ip'] for result in results]
    nombres = [result['nombre'] for result in results]
    correctos = [result['correctos'] for result in results]
    perdidos = [result['perdidos'] for result in results]

    # Calcular los promedios
    promedio_correctos = sum(correctos) / len(correctos) if correctos else 0
    promedio_perdidos = sum(perdidos) / len(perdidos) if perdidos else 0

    # Crear la ventana para los gráficos
    new_window = tk.Toplevel(ventana_principal)
    new_window.title("Gráficos de Resultados de Ping")

    # Crear un Canvas para permitir el desplazamiento
    canvas_frame = tk.Frame(new_window)
    canvas_frame.pack(fill=tk.BOTH, expand=True)

    canvas = tk.Canvas(canvas_frame)
    scrollbar = tk.Scrollbar(canvas_frame, orient="vertical", command=canvas.yview)
    canvas.configure(yscrollcommand=scrollbar.set)

    scrollbar.pack(side="right", fill="y")
    canvas.pack(side="left", fill=tk.BOTH, expand=True)

    # Crear un frame dentro del canvas para los gráficos
    graphics_frame = tk.Frame(canvas)
    canvas.create_window((0, 0), window=graphics_frame, anchor="nw")

    # Crear el primer gráfico (Resultados de Ping por IP)
    fig1, ax1 = plt.subplots(figsize=(10, 6))

    bar_width = 0.35
    index = range(len(ips))

    # Colores personalizados para las barras
    color_correctos = '#4CAF50'  # Verde
    color_perdidos = '#F44336'  # Rojo

    # Crear las barras
    bar1 = ax1.bar(index, correctos, bar_width, label='% < 50ms', color=color_correctos, edgecolor='black', hatch='//')
    bar2 = ax1.bar([i + bar_width for i in index], perdidos, bar_width, label='% >= 50ms o sin respuesta', color=color_perdidos, edgecolor='black', hatch='\\')

    # Mostrar los valores encima de las barras
    def add_labels(bars, data):
        for bar, value in zip(bars, data):
            height = bar.get_height()
            ax1.text(bar.get_x() + bar.get_width() / 2, height + 0.5, f'{value:.2f}%', ha='center', va='bottom', fontsize=10)

    add_labels(bar1, correctos)
    add_labels(bar2, perdidos)

    # Establecer etiquetas y título
    ax1.set_xlabel('Equipos', fontsize=12)
    ax1.set_ylabel('Porcentaje', fontsize=12)
    ax1.set_title('Resultados de Ping por IP', fontsize=14, fontweight='bold')
    ax1.set_xticks([i + bar_width / 2 for i in index])
    ax1.set_xticklabels(nombres, rotation=45, ha='right', fontsize=10)
    ax1.legend(title="Resultados", title_fontsize='13', fontsize=11)

    # Mejorar el diseño con una cuadrícula
    ax1.grid(True, linestyle='--', alpha=0.7)

    # Mejorar el estilo de los ejes
    ax1.tick_params(axis='both', which='major', labelsize=10)

    # Crear el canvas para el gráfico de resultados y empaquetarlo
    canvas1 = FigureCanvasTkAgg(fig1, master=graphics_frame)
    canvas1.draw()
    canvas1.get_tk_widget().pack(pady=10)

    # Crear el gráfico de promedios en la misma ventana
    fig2, ax2 = plt.subplots(figsize=(10, 6))

    # Datos para el gráfico de promedios
    promedios_ips = ['Promedio']
    promedios_correctos = [promedio_correctos]
    promedios_perdidos = [promedio_perdidos]

    # Crear las barras para el gráfico de promedios
    bar1_avg = ax2.bar(promedios_ips, promedios_correctos, color=color_correctos, edgecolor='black', label='% < 50ms Promedio', hatch='//')
    bar2_avg = ax2.bar([x + bar_width for x in range(len(promedios_ips))], promedios_perdidos, color=color_perdidos, edgecolor='black', label='% >= 50ms o sin respuesta Promedio', hatch='\\')

    # Mostrar los valores encima de las barras
    def add_labels_promedio(bars, data):
        for bar, value in zip(bars, data):
            height = bar.get_height()
            ax2.text(bar.get_x() + bar.get_width() / 2, height + 0.5, f'{value:.2f}%', ha='center', va='bottom', fontsize=10)

    add_labels_promedio(bar1_avg, promedios_correctos)
    add_labels_promedio(bar2_avg, promedios_perdidos)

    # Establecer etiquetas y título
    ax2.set_xlabel('Promedio', fontsize=12)
    ax2.set_ylabel('Porcentaje', fontsize=12)
    ax2.set_title('Promedio de Resultados de Ping', fontsize=14, fontweight='bold')
    ax2.set_xticks([x + bar_width / 2 for x in range(len(promedios_ips))])
    ax2.set_xticklabels(promedios_ips, rotation=45, ha='right', fontsize=10)
    ax2.legend(title="Promedios", title_fontsize='13', fontsize=11)

    # Mejorar el diseño con una cuadrícula
    ax2.grid(True, linestyle='--', alpha=0.7)

    # Mejorar el estilo de los ejes
    ax2.tick_params(axis='both', which='major', labelsize=10)

    # Crear el canvas para el gráfico de promedios y empaquetarlo
    canvas2 = FigureCanvasTkAgg(fig2, master=graphics_frame)
    canvas2.draw()
    canvas2.get_tk_widget().pack(pady=10)

    # Actualizar el área de desplazamiento para que se ajuste al contenido
    graphics_frame.update_idletasks()
    canvas.config(scrollregion=canvas.bbox("all"))

    # Asegurar que no se modifica la ventana principal
    new_window.protocol("WM_DELETE_WINDOW", lambda: new_window.destroy())


def generar_nueva_ventana():
    nueva_ventana = tk.Toplevel(ventana_principal)
    nueva_app = PingApp(nueva_ventana, log_area, promedios_area, results)


ventana_principal = tk.Tk()
ventana_principal.title("Gestión de Ventanas de Ping")

results = []

log_area = tk.Text(ventana_principal, height=10, width=70)
log_area.pack(pady=10)

promedios_area = tk.Text(ventana_principal, height=5, width=70)
promedios_area.pack(pady=10)

btn_generar_ventana = tk.Button(ventana_principal, text="Generar Nueva Ventana de Ping", command=generar_nueva_ventana)
btn_generar_ventana.pack(pady=10)

btn_calcular_promedio = tk.Button(ventana_principal, text="Calcular Promedio de Pings", command=calcular_promedio)
btn_calcular_promedio.pack(pady=10)

btn_limpiar = tk.Button(ventana_principal, text="Limpiar Log y Resultados", command=limpiar_log)
btn_limpiar.pack(pady=10)

btn_generar_grafico = tk.Button(ventana_principal, text="Generar Gráfico de Resultados", command=generar_grafico)
btn_generar_grafico.pack(pady=10)

ventana_principal.mainloop()#original
