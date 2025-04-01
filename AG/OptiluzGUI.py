import tkinter as tk
from tkinter import ttk, messagebox
from OptiluzGA import OptiluzGA
from OptiluzInput import OptiluzInput

class OptiluzGUI(tk.Tk):
    """
    Interfaz gráfica para ingresar los datos de entrada de OptiLuz,
    ejecutar el algoritmo genético y mostrar los resultados y gráficas.
    """
    def __init__(self):
        super().__init__()
        self.title("OptiLuz - Datos de Entrada")
        self.geometry("450x700")
        self.create_widgets()

    def create_widgets(self):
        frame = ttk.Frame(self)
        frame.pack(padx=10, pady=10, fill="both", expand=True)
        self.entries = {}
        row = 0

        # Lista de campos: (etiqueta, clave)
        campos = [
            ("Superficie del aula (m²):", "superficie"),
            ("Cantidad de ventanas:", "ventanas"),
            ("Coeficiente de Transmisión Térmica:", "coeficiente"),
            ("Temperatura Exterior (°C):", "temp_ext"),
            ("Temperatura Interior Deseada (°C):", "temp_int"),
            ("Humedad Relativa (%):", "humedad"),
            ("Carga Térmica (W) por Equipos:", "carga"),
            ("Nivel de Iluminación Recomendado (lux):", "lux")
        ]
        for texto, key in campos:
            ttk.Label(frame, text=texto).grid(row=row, column=0, sticky="w", pady=5)
            self.entries[key] = ttk.Entry(frame)
            self.entries[key].grid(row=row, column=1, pady=5)
            row += 1

        # Tipo de iluminación instalada (opciones)
        ttk.Label(frame, text="Tipo de Iluminación Instalada:").grid(row=row, column=0, sticky="w", pady=5)
        self.entries["tipo_iluminacion"] = ttk.Combobox(frame,
                                                        values=["LED", "Fluorescente", "Incandescente"],
                                                        state="readonly")
        self.entries["tipo_iluminacion"].grid(row=row, column=1, pady=5)
        self.entries["tipo_iluminacion"].current(0)
        row += 1

        # Eficiencia lumínica de las lámparas (lm/W)
        ttk.Label(frame, text="Eficiencia Lumínica (lm/W):").grid(row=row, column=0, sticky="w", pady=5)
        self.entries["eficiencia"] = ttk.Entry(frame)
        self.entries["eficiencia"].grid(row=row, column=1, pady=5)
        row += 1

        # Cantidad de lámparas instaladas
        ttk.Label(frame, text="Cantidad de Lámparas Instaladas:").grid(row=row, column=0, sticky="w", pady=5)
        self.entries["lamparas"] = ttk.Entry(frame)
        self.entries["lamparas"].grid(row=row, column=1, pady=5)
        row += 1

        # Potencia de cada lámpara (W)
        ttk.Label(frame, text="Potencia de Cada Lámpara (W):").grid(row=row, column=0, sticky="w", pady=5)
        self.entries["potencia_lampara"] = ttk.Entry(frame)
        self.entries["potencia_lampara"].grid(row=row, column=1, pady=5)
        row += 1

        # Factor de ponderación α
        ttk.Label(frame, text="Factor de Ponderación α:").grid(row=row, column=0, sticky="w", pady=5)
        self.entries["alpha"] = ttk.Entry(frame)
        self.entries["alpha"].grid(row=row, column=1, pady=5)
        row += 1

        # Factor de ponderación β
        ttk.Label(frame, text="Factor de Ponderación β:").grid(row=row, column=0, sticky="w", pady=5)
        self.entries["beta"] = ttk.Entry(frame)
        self.entries["beta"].grid(row=row, column=1, pady=5)
        row += 1

        # Botón para iniciar la optimización
        submit_button = ttk.Button(frame, text="Iniciar Optimización", command=self.submit)
        submit_button.grid(row=row, column=0, columnspan=2, pady=15)

    def submit(self):
        """
        Recoge los datos ingresados, crea el objeto de entrada, instancia y ejecuta el
        algoritmo genético. Los resultados y gráficas se muestran al finalizar la evolución.
        """
        try:
            data = OptiluzInput(
                superficie = float(self.entries["superficie"].get()),
                ventanas = int(self.entries["ventanas"].get()),
                coeficiente = float(self.entries["coeficiente"].get()),
                temp_ext = float(self.entries["temp_ext"].get()),
                temp_int = float(self.entries["temp_int"].get()),
                humedad = float(self.entries["humedad"].get()),
                carga = float(self.entries["carga"].get()),
                lux = float(self.entries["lux"].get()),
                tipo_iluminacion = self.entries["tipo_iluminacion"].get(),
                eficiencia = float(self.entries["eficiencia"].get()),
                lamparas = int(self.entries["lamparas"].get()),
                potencia_lampara = float(self.entries["potencia_lampara"].get()),
                alpha = float(self.entries["alpha"].get()),
                beta = float(self.entries["beta"].get())
            )
            # Muestra confirmación con los datos ingresados
            messagebox.showinfo("Datos Recibidos", f"Se han recibido los siguientes datos:\n\n{data}")
            print(data)
            
            # Instanciar el algoritmo genético y ejecutar la evolución
            ga = OptiluzGA(data, pop_size=20)  # Puedes ajustar el tamaño de la población
            ga.run_evolution(generations=50, mutation_rate=0.1, tournament_size=3)
            
        except Exception as e:
            messagebox.showerror("Error", f"Error al procesar los datos: {e}")