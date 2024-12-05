# REDES DE BALANCEO - PROCESOS ESTOCASTICOS

![image](https://github.com/user-attachments/assets/d39d1978-0a96-4fcf-9d61-30d69f8d9380)


Este proyecto es una aplicación que utiliza Python y Tkinter para crear una interfaz gráfica de usuario (GUI). El objetivo principal del código es realizar un balanceo de carga de tareas en estaciones, de acuerdo con ciertas reglas. A continuación, se explica el funcionamiento d los principales componentes del código.

## Estructura del proyecto

El proyecto se organiza de la siguiente forma:
- **main.py**: Archivo principal que inicializa y ejecuta la aplicación.
- **ui.py**: Contiene la clase `App` que maneja la interfaz gráfica.
- **utils.py**: Contiene funciones auxiliares que soportan la lógica del balanceo de carga.

## Descripción de la lógica del código

### 1. Inicialización de la aplicación

En el archivo **main.py**, se importa la clase `App` de **ui.py** y se crea la ventana principal utilizando `Tk()` de Tkinter. Luego, se pasa la ventana al objeto `App`, que maneja la interfaz gráfica y los eventos.

```python
from tkinter import Tk
from ui import App
if __name__ == "__main__":
    root = Tk() # Crea la ventana principal
    app = App(root) # Inicializa la aplicación con la ventana
    root.mainloop() # Ejecuta el ciclo principal de la GUI
```

### 2. Estructura de la interfaz gráfica (GUI)

El archivo **ui.py** contiene la clase `App`, que es responsable de la creación de los elementos visuales de la GUI, como botones, etiquetas, y tablas para mostrar los resultados. La interfaz permite al usuario ingresar datos y ver los resultados del balanceo de tareas en tiempo real.

```python
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
        # Resto de elementos como botones, etiquetas y demas.
```

### 3. Lógica del balanceo de carga de tareas

En **utils.py**, se implementa la lógica principal del balanceo de carga de tareas. Esta lógica utiliza los siguientes pasos:
* **Filtrado de tareas factibles:** Antes de asignar una tarea a una estación, se filtran las tareas que son factibles, es decir, aquellas que no han sido asignadas previamente y que tienen todas sus precedencias completadas.
* **Orden de ejecución:** Las tareas se ordenan en función de su tiempo de ejecución, de modo que se priorizan las tareas con mayor duración si el tiempo restante en la estación lo permite.
* **Asignación de tareas:** Una vex filtradas y ordenadas las tareas, se asignan las estaciones siempre que el tiempo de ejecución de la tarea sea menor o igual al tiempo restante de la estación.

```python
def assign_tasks_to_stations(tasks, cycle_time, precedence_rules):
    stations = []
    current_station = []
    current_time = 0

    while tasks:
        feasible_tasks = [
            task for task in tasks
            if all(pre in [t[0] for s in stations for t in s] or pre in [t[0] for t in current_station]
                   for pre in precedence_rules.get(task[0], []))
        ]
    # Lógica para asignar la tarea
```

### 4. Procesamiento de datos

El código también procesa y organiza los datos en una tabla que muestra las tareas asignadas, el tiempo restante, las tareas factibles, y otra métricas de la ejecución.
Este procesamiento incluye:
* La visualización de las tareas asignadas en cada estación.
* El manejo de las condiciones de precedencia de las tareas.
* La actualización de los valores de la tabla a medida que se van asignando tareas.

```python
self.table.insert(
    "",
    tk.END,
    values=( # Valores que se muestran en cada fila
        row['station'],  # Número de estación
        row['task_name'],  # Nombre de la tarea
        row['task_time'],  # Tiempo de la tarea
        row['remaining'],  # Tiempo restante de ciclo
        row['feasible_tasks_str'],  # Tareas fáctibles para la siguiente iteración
        row['tasks_with_max_time_str'],  # Tareas con mayor tiempo (factibles)
        row['selected_task'],  # Tarea seleccionada
    )
)
```

### 5. Consideraciones y mejoras futuras

* **Manejo de errores:** Actualmente, el código no incluye un manejo robusto de errores. No tiene validaciones y mensajes de error para mejorar la experiencia del usuario
* **Optimización:** El algoritmo de asignaci+on de tareas puede ser optimizado para manejar casos más complehor con más tareas y estaciónes.

## Conclusión

Este proyecto utiliza una estructura sencilla para implementar un balanceo de carga de tareas utilizando reglas de precedencia y un ciclo de tiempo fijo. A través de la interfaz gráfica, el usuario puede ver en tiempo real cómo se asignan las tareas a las estaciones, optimizando el uso del tiempo disponible.
