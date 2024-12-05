import tkinter as tk
from tkinter import messagebox
from tkinter import ttk
import os
import sys
import matplotlib.pyplot as plt
import networkx as nx
from utils import *
import math

class App:
    def __init__(self, root):
        self.root = root
        self.root.title("Balanceo de Líneas de Producción")
        self.root.minsize(1000, 1000)
        if getattr(sys, 'frozen', False):
            base_path = sys._MEIPASS
        else:
            base_path = os.path.dirname(os.path.abspath(__file__))
        
        icon_path = os.path.join(base_path, 'img', 'icono.ico')
        self.root.iconbitmap(icon_path)

        # Paleta de colores
        self.bg_color = "#F5F5F5"
        self.primary_color = "coral2"
        self.secondary_color = "#2F4F4F"
        self.button_hover = "#FF7F50"

        self.root.configure(bg = self.bg_color)

        self.style = ttk.Style()
        self.style.theme_use("clam")
        self.style.configure(
            "TButton",
            background = self.primary_color,
            foreground = "white",
            font = ("Roboto", 12),
            borderwidth = 1,
        )
        self.style.map(
            "TButton",
            background = [("active", self.button_hover)],
            foreground = [("active", "white")],
        )
        self.style.configure(
            "TLabel",
            background = self.bg_color,
            foreground = self.secondary_color,
            font = ("Roboto", 11),
        )
        
        self.tasks = []
        self.precedence_rules = {}
        
        self.create_widgets()
    
    def create_widgets(self):
        container = tk.Frame(self.root, bg = self.root["bg"])
        container.place(relx = 0.5, rely = 0.5, anchor = "center")

        # Entrada de datos
        ttk.Label(container, text = "Tiempo de producción (seg): ").grid(row = 0, column = 0, sticky = tk.W, pady = 5)
        self.production_time = ttk.Entry(container)
        self.production_time.grid(row = 0, column = 1, pady = 5)

        ttk.Label(container, text = "Producción requerida (uds): ").grid(row = 1, column = 0, sticky = tk.W, pady = 5)
        self.required_production = ttk.Entry(container)
        self.required_production.grid(row = 1, column = 1, pady = 5)

        ttk.Label(container, text = "Tarea: ").grid(row = 2, column = 0, sticky = tk.W, pady = 5)
        self.task_name = ttk.Entry(container)
        self.task_name.grid(row = 2, column = 1, pady = 5)

        ttk.Label(container, text = "Tiempo (seg): ").grid(row = 3, column = 0, sticky = tk.W, pady = 5)
        self.task_time = ttk.Entry(container)
        self.task_time.grid(row = 3, column = 1, pady = 5)

        ttk.Label(container, text = "Precedencias (coma separadas): ").grid(row = 4, column = 0, sticky = tk.W, pady = 5)
        self.task_precedence = ttk.Entry(container)
        self.task_precedence.grid(row = 4, column = 1, pady = 5)

        ttk.Button(container, text = "Agregar Tarea", command = self.add_task).grid(row = 5, column = 0, columnspan = 2, pady = 10)

        ttk.Button(container, text = "Calcular", command = self.calculate).grid(row = 6, column = 0, columnspan = 2, pady = 10)

        # Botón para reiniciar el programa
        ttk.Button(container, text="Reiniciar Programa", command = self.restart).grid(row = 7, column = 0, columnspan = 2, pady = 10)
        
        # Resultados
        self.results = tk.Text(container, height = 15, width = 80, bg = "white", fg = self.secondary_color, font = ("Roboto", 10))
        self.results.grid(row = 8, column = 0, columnspan = 2, pady = 10)

        # Tabla
        self.table = ttk.Treeview(container, columns=("Estación", "Tarea", "Tiempo Tarea", "Tiempo Restante", "Tareas Factibles", "Tareas con Mayor Tiempo", "Selección"), show="headings", height=15)
        self.table.grid(row = 9, column = 0, columnspan = 2, padx = 10, pady = 10)

        self.table.heading("Estación", text="Estación")
        self.table.heading("Tarea", text="Tarea")
        self.table.heading("Tiempo Tarea", text="Tiempo Tarea")
        self.table.heading("Tiempo Restante", text="Tiempo Restante")
        self.table.heading("Tareas Factibles", text="Tareas Factibles")
        self.table.heading("Tareas con Mayor Tiempo", text="Tareas con Mayor Tiempo")
        self.table.heading("Selección", text="Selección")

        self.table.column("Estación", width=80)
        self.table.column("Tarea", width=100)
        self.table.column("Tiempo Tarea", width=100)
        self.table.column("Tiempo Restante", width=130)
        self.table.column("Tareas Factibles", width=180)
        self.table.column("Tareas con Mayor Tiempo", width=180)
        self.table.column("Selección", width=120)

    def add_task(self):
        # Obtenemos datos ingresados por el ususario
        task = self.task_name.get().strip()
        if task in [t[0] for t in self.tasks]:
            messagebox.showerror("Error", f"La tarea '{task}' ya existe.")
            return
        
        try:
            time = int(self.task_time.get().strip())
        except ValueError:
            messagebox.showerror("Error", "El tiempo debe ser un número entero.")
            return
        
        precedences = [p.strip() for p in self.task_precedence.get().split(",") if p.strip()]
        
        for pre in precedences:
            if pre not in [t[0] for t in self.tasks]:
                messagebox.showerror("Error", f"La tarea predecesora '{pre}' no existe.")
                return

        # Guardamos la tarea y sus precedencias
        self.tasks.append((task, time))
        self.precedence_rules[task] = precedences
        
        # Mostramos la tarea agregada
        self.results.insert(tk.END, f"Tarea '{task}' con tiempo {time} seg y precedencias {precedences} agregada.\n")

        #Limpiamos campos
        self.task_name.delete(0, tk.END)
        self.task_time.delete(0, tk.END)
        self.task_precedence.delete(0, tk.END)

    def calculate(self):
        try:
            try:
                production_time = float(self.production_time.get())
                required_production = float(self.required_production.get())
            except ValueError:
                messagebox.showerror("Error", "El tiempo de producción y la producción requerida deben ser números enteros.")
                return
            
            if production_time <= 0 or required_production <= 0:
                messagebox.showerror("Error", "El tiempo de producción y la producción requerida deben ser mayores a cero.")
                return

            production_time = math.ceil(production_time)  # Redondeamos hacia arriba
            required_production = math.ceil(required_production)
            
            # Cálculos
            try:
                cycle_time = calculate_cycle_time(production_time, required_production)
            except ZeroDivisionError:
                messagebox.showerror("Error", "No se puede calcular el tiempo de ciclo porque la producción requerida es cero.")
                return

            task_times = [t[1] for t in self.tasks]

            if not task_times or all(time <= 0 for time in task_times):
                messagebox.showerror("Error", "Debe haber al menos una tarea con un tiempo válido mayor a cero.")
                return

            min_stations = math.ceil(calculate_min_stations(task_times, cycle_time))
            stations = []
            assigned_tasks = []

            for station_index in range(1, min_stations + 1):
                remaining_time = cycle_time
                station_tasks = []
                
                while remaining_time > 0:
                    feasible_tasks = [
                        task[0]
                        for task in self.tasks
                        if task[0] not in assigned_tasks
                        and all(pre in assigned_tasks for pre in self.precedence_rules.get(task[0], [])) and
                        task[1] <= remaining_time
                    ]
                    
                    
                    if not feasible_tasks:
                        break;
                    
                    tasks_with_max_time = sorted(
                        [(task, time) for task, time in self.tasks if task in feasible_tasks],
                        key=lambda x: x[1],
                        reverse=True
                    )
                    
                    best_task, task_time = tasks_with_max_time[0]
                    
                    if task_time <= remaining_time:
                        station_tasks.append((best_task, task_time))
                        assigned_tasks.append(best_task)
                        remaining_time -= task_time
                        
                    else:
                        break
                                        
                stations.append(station_tasks)

            for row in self.table.get_children():
                self.table.delete(row)

            efficiency = calculate_efficiency(task_times, cycle_time, stations)
            
            # Mostramos resultados
            self.results.insert(tk.END, "\n=== Resultados ===\n")
            self.results.insert(tk.END, f"Tiempo de ciclo: {cycle_time:.2f} seg\n")
            self.results.insert(tk.END, f"Estaciones mínimas: {math.ceil(min_stations)} ({min_stations:.2f})\n")
            self.results.insert(tk.END, f"Eficiencia: {efficiency:.2f}%\n")
            
            assigned_tasks = []
            
            for i, station in enumerate(stations, start=1):
                print(f"Estación {i}: {station}")
                station_tasks_str = ", ".join([f"{t[0]} ({t[1]} seg)" for t in station])
                self.results.insert(tk.END, f"Estación {i}: {station_tasks_str}\n")
                
                remaining = cycle_time
                
                station_rows = []
                
                for task_index, (task_name, task_time) in enumerate(station):
                    
                    feasible_tasks = [
                        task[0]
                        for task in self.tasks
                        if task[0] not in assigned_tasks and 
                        all(pre in assigned_tasks for pre in self.precedence_rules.get(task[0], [])) and
                        task[1] <= remaining
                    ]
                    
                    tasks_with_max_time = [
                        task [0]
                        for task in sorted(
                        [(task, time) for task, time in self.tasks if task in feasible_tasks],
                        key=lambda x: x[1],
                        reverse=True
                        )
                    ]
                    
                    feasible_tasks_str = ", ".join(feasible_tasks) if feasible_tasks else "-"
                    tasks_with_max_time_str = ", ".join(tasks_with_max_time) if tasks_with_max_time else "-"
                    selected_task = tasks_with_max_time[0] if tasks_with_max_time else "-"
                    
                    if task_time <= remaining:
                        assigned_tasks.append(task_name)
                        remaining -= task_time
                        
                    else:
                        break

                    station_rows.append({
                        'station': i,
                        'task_name': task_name,
                        'task_time': task_time,
                        'remaining': remaining,
                        'feasible_tasks_str': feasible_tasks_str,
                        'tasks_with_max_time_str': tasks_with_max_time_str,
                        'selected_task': selected_task
                    })
                
                for task_index in range(len(station_rows) - 1):
                    station_rows[task_index]['feasible_tasks_str'] = station_rows[task_index + 1]['feasible_tasks_str']
                    station_rows[task_index]['tasks_with_max_time_str'] = station_rows[task_index + 1]['tasks_with_max_time_str']
                    station_rows[task_index]['selected_task'] = station_rows[task_index + 1]['selected_task']

                if station_rows:
                    last_row = station_rows[-1]
                    last_row['feasible_tasks_str'] = "-"
                    last_row['tasks_with_max_time_str'] = "-"
                    last_row['selected_task'] = "-"

                for row in station_rows:
                    self.table.insert(
                        "",
                        tk.END,
                        values=(
                            row['station'],  
                            row['task_name'],  
                            row['task_time'],  
                            row['remaining'],  
                            row['feasible_tasks_str'],  
                            row['tasks_with_max_time_str'],  
                            row['selected_task'],  
                        )
                    )
                
            # Mostramos diagrama de precedencia
            self.show_precedence_diagram()
        
        except Exception as e:
            messagebox.showerror("Error", f"Ocurrió un error durante el cálculo: {str(e)}")

    def show_precedence_diagram(self):
        G = nx.DiGraph()
        for task, precedences in self.precedence_rules.items():
            for pre in precedences:
                G.add_edge(pre, task)
        
        pos = nx.planar_layout(G)
        nx.draw(G, pos, with_labels = True, node_size = 2000, node_color = "skyblue")
        manager = plt.get_current_fig_manager()
        manager.set_window_title("Diagrama de Precedencia")
        plt.show()
    
    def restart(*args):
        answer = messagebox.askyesno("Reiniciar", "¿Estás seguro de que quieres reiniciar el programa?")
        if answer:
            python = sys.executable
            os.execl(python, python, *sys.argv)
    
