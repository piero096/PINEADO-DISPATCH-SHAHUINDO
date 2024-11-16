import subprocess
import tkinter as tk
from tkinter import messagebox
import threading

proceso_ping = None

def iniciar_ping():
    global proceso_ping  

    ip = entry_ip.get()

    if not ip:
        messagebox.showerror("Error", "Por favor ingrese una IP válida.")
        return

    correctos = 0
    perdidos = 0

    output_text.delete(1.0, tk.END)
    output_text.insert(tk.END, f"Iniciando ping a {ip}...\n")

    def ping():
        nonlocal correctos, perdidos

        global proceso_ping 
        proceso_ping = subprocess.Popen(["ping", ip, "-t"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

        try:
            while True:
                line = proceso_ping.stdout.readline()
                if line == '':
                    break

                output_text.insert(tk.END, line)
                output_text.yview(tk.END) 

                if "TTL" in line:
                    correctos += 1
                elif "Tiempo de espera agotado para esta solicitud." in line:
                    perdidos += 1

            total_paquetes = correctos + perdidos
            if total_paquetes > 0:
                porcentaje_correctos = (correctos / total_paquetes) * 100
                porcentaje_perdidos = (perdidos / total_paquetes) * 100
            else:
                porcentaje_correctos = 0
                porcentaje_perdidos = 0

            output_text.insert(tk.END, "\nResumen del ping:\n")
            output_text.insert(tk.END, f"Paquetes correctos: {correctos}\n")
            output_text.insert(tk.END, f"Paquetes perdidos: {perdidos}\n")
            output_text.insert(tk.END, f"Porcentaje de paquetes correctos: {porcentaje_correctos:.2f}%\n")
            output_text.insert(tk.END, f"Porcentaje de paquetes perdidos: {porcentaje_perdidos:.2f}%\n")

        except KeyboardInterrupt:
            output_text.insert(tk.END, "\nProceso de ping detenido.")
        finally:
            ping_process = None 

    threading.Thread(target=ping, daemon=True).start()

def detener_ping():
    global proceso_ping  
    if proceso_ping is not None:
        proceso_ping.terminate() 
        output_text.insert(tk.END, "\nProceso de ping detenido por el usuario.\n")
        proceso_ping = None 
    else:
        output_text.insert(tk.END, "\nNo hay un ping en curso para detener.\n")

ventana = tk.Tk()
ventana.title("PING_IP - BY PIERO LAVY")

label = tk.Label(ventana, text="Ingresa la IP a hacer ping:")
label.pack(pady=10)

entry_ip = tk.Entry(ventana, width=30)
entry_ip.pack(pady=10)

btn_iniciar = tk.Button(ventana, text="Iniciar Ping", command=iniciar_ping)
btn_iniciar.pack(pady=10)

btn_detener = tk.Button(ventana, text="Detener Ping", command=detener_ping)
btn_detener.pack(pady=10)

output_text = tk.Text(ventana, height=15, width=70)
output_text.pack(pady=10)
ventana.mainloop()