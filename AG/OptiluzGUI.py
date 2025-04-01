import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from OptiluzGA import OptiluzGA
from OptiluzInput import OptiluzInput

class OptiluzGUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("OptiLuz - Optimización de Consumo Energético")
        self.geometry("900x700")
        self.config(padx=15, pady=15)
        self.resizable(True, True)
        
        # Crear estilo para los widgets
        self.style = ttk.Style()
        self.style.configure("TFrame", padding=5)
        self.style.configure("Header.TLabel", font=("Arial", 12, "bold"))
        self.style.configure("TButton", font=("Arial", 10))
        
        # Inicializar pestañas
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill="both", expand=True)
        
        # Pestaña de entrada de datos
        self.input_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.input_tab, text="Datos de Entrada")
        
        # Pestaña de resultados
        self.results_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.results_tab, text="Resultados")
        
        # Crear widgets de entrada
        self.create_input_widgets()
        
        # Crear área de resultados (inicialmente vacía)
        self.create_results_area()

    def create_input_widgets(self):
        # Crear un canvas con scrollbar para la sección de entrada
        canvas = tk.Canvas(self.input_tab)
        scrollbar = ttk.Scrollbar(self.input_tab, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Frame principal
        main_frame = ttk.Frame(scrollable_frame)
        main_frame.pack(padx=10, pady=10, fill="both", expand=True)
        
        self.entries = {}
        row = 0
        
        # Título
        title_label = ttk.Label(main_frame, text="OptiLuz - Optimizador de Eficiencia Energética", 
                               style="Header.TLabel")
        title_label.grid(row=row, column=0, columnspan=3, pady=10)
        row += 1
        
        # Descripción
        desc_text = ("Ingrese los datos del aula para optimizar la selección de aire acondicionado, "
                    "iluminación, aislamiento térmico y capacidad recomendada.")
        desc_label = ttk.Label(main_frame, text=desc_text, wraplength=400)
        desc_label.grid(row=row, column=0, columnspan=3, pady=5)
        row += 1
        
        # Separador
        ttk.Separator(main_frame, orient='horizontal').grid(
            row=row, column=0, columnspan=3, sticky='ew', pady=10)
        row += 1
        
        # ---- Sección de características del aula ----
        section_label = ttk.Label(main_frame, text="Características del Aula", 
                                 style="Header.TLabel")
        section_label.grid(row=row, column=0, columnspan=3, sticky="w", pady=5)
        row += 1
        
        # Crea un frame para la sección
        aula_frame = ttk.LabelFrame(main_frame, text="Datos Físicos")
        aula_frame.grid(row=row, column=0, columnspan=3, sticky="ew", padx=5, pady=5)
        
        # Campos de características del aula
        aula_campos = [
            ("Superficie del aula (m²):", "superficie", "50"),
            ("Cantidad de ventanas:", "ventanas", "4"),
            ("Coeficiente de Transmisión Térmica:", "coeficiente", "1.2")
        ]
        
        aula_row = 0
        for texto, key, default in aula_campos:
            ttk.Label(aula_frame, text=texto).grid(row=aula_row, column=0, sticky="w", pady=5, padx=5)
            self.entries[key] = ttk.Entry(aula_frame)
            self.entries[key].insert(0, default)
            self.entries[key].grid(row=aula_row, column=1, pady=5, padx=5, sticky="ew")
            aula_row += 1
        
        row += 1
        
        # ---- Sección de factores térmicos ----
        section_label = ttk.Label(main_frame, text="Factores Térmicos y Climatización", 
                                 style="Header.TLabel")
        section_label.grid(row=row, column=0, columnspan=3, sticky="w", pady=5)
        row += 1
        
        # Crea un frame para la sección
        termica_frame = ttk.LabelFrame(main_frame, text="Condiciones Térmicas")
        termica_frame.grid(row=row, column=0, columnspan=3, sticky="ew", padx=5, pady=5)
        
        # Campos de factores térmicos
        termica_campos = [
            ("Temperatura Exterior (°C):", "temp_ext", "30"),
            ("Temperatura Interior Deseada (°C):", "temp_int", "18"),
            ("Humedad Relativa (%):", "humedad", "60"),
            ("Carga Térmica (W) por Equipos:", "carga", "5000")
        ]
        
        termica_row = 0
        for texto, key, default in termica_campos:
            ttk.Label(termica_frame, text=texto).grid(row=termica_row, column=0, sticky="w", pady=5, padx=5)
            self.entries[key] = ttk.Entry(termica_frame)
            self.entries[key].insert(0, default)
            self.entries[key].grid(row=termica_row, column=1, pady=5, padx=5, sticky="ew")
            termica_row += 1
        
        row += 1
        
        # ---- Sección de factores de iluminación ----
        section_label = ttk.Label(main_frame, text="Factores de Iluminación", 
                                 style="Header.TLabel")
        section_label.grid(row=row, column=0, columnspan=3, sticky="w", pady=5)
        row += 1
        
        # Crea un frame para la sección
        iluminacion_frame = ttk.LabelFrame(main_frame, text="Iluminación Actual")
        iluminacion_frame.grid(row=row, column=0, columnspan=3, sticky="ew", padx=5, pady=5)
        
        # Nivel de iluminación
        ttk.Label(iluminacion_frame, text="Nivel de Iluminación Recomendado (lux):").grid(
            row=0, column=0, sticky="w", pady=5, padx=5)
        self.entries["lux"] = ttk.Entry(iluminacion_frame)
        self.entries["lux"].insert(0, "300")
        self.entries["lux"].grid(row=0, column=1, pady=5, padx=5, sticky="ew")
        
        # Tipo de iluminación instalada
        ttk.Label(iluminacion_frame, text="Tipo de Iluminación Instalada:").grid(
            row=1, column=0, sticky="w", pady=5, padx=5)
        self.entries["tipo_iluminacion"] = ttk.Combobox(
            iluminacion_frame, values=["LED", "Fluorescente", "Incandescente"], state="readonly")
        self.entries["tipo_iluminacion"].grid(row=1, column=1, pady=5, padx=5, sticky="ew")
        self.entries["tipo_iluminacion"].current(0)
        
        # Eficiencia lumínica
        ttk.Label(iluminacion_frame, text="Eficiencia Lumínica (lm/W):").grid(
            row=2, column=0, sticky="w", pady=5, padx=5)
        self.entries["eficiencia"] = ttk.Entry(iluminacion_frame)
        self.entries["eficiencia"].insert(0, "100")
        self.entries["eficiencia"].grid(row=2, column=1, pady=5, padx=5, sticky="ew")
        
        # Lámparas
        ttk.Label(iluminacion_frame, text="Cantidad de Lámparas Instaladas:").grid(
            row=3, column=0, sticky="w", pady=5, padx=5)
        self.entries["lamparas"] = ttk.Entry(iluminacion_frame)
        self.entries["lamparas"].insert(0, "10")
        self.entries["lamparas"].grid(row=3, column=1, pady=5, padx=5, sticky="ew")
        
        # Potencia
        ttk.Label(iluminacion_frame, text="Potencia de Cada Lámpara (W):").grid(
            row=4, column=0, sticky="w", pady=5, padx=5)
        self.entries["potencia_lampara"] = ttk.Entry(iluminacion_frame)
        self.entries["potencia_lampara"].insert(0, "20")
        self.entries["potencia_lampara"].grid(row=4, column=1, pady=5, padx=5, sticky="ew")
        
        row += 1
        
        # ---- Sección de parámetros del algoritmo ----
        section_label = ttk.Label(main_frame, text="Parámetros del Algoritmo", 
                                 style="Header.TLabel")
        section_label.grid(row=row, column=0, columnspan=3, sticky="w", pady=5)
        row += 1
        
        # Crea un frame para la sección
        params_frame = ttk.LabelFrame(main_frame, text="Configuración")
        params_frame.grid(row=row, column=0, columnspan=3, sticky="ew", padx=5, pady=5)
        
        # Factor α
        ttk.Label(params_frame, text="Factor de Ponderación α (consumo energético):").grid(
            row=0, column=0, sticky="w", pady=5, padx=5)
        self.entries["alpha"] = ttk.Entry(params_frame)
        self.entries["alpha"].insert(0, "0.8")
        self.entries["alpha"].grid(row=0, column=1, pady=5, padx=5, sticky="ew")
        
        # Factor β
        ttk.Label(params_frame, text="Factor de Ponderación β (confort):").grid(
            row=1, column=0, sticky="w", pady=5, padx=5)
        self.entries["beta"] = ttk.Entry(params_frame)
        self.entries["beta"].insert(0, "0.2")
        self.entries["beta"].grid(row=1, column=1, pady=5, padx=5, sticky="ew")
        
        # Tamaño de población
        ttk.Label(params_frame, text="Tamaño de Población:").grid(
            row=2, column=0, sticky="w", pady=5, padx=5)
        self.entries["pop_size"] = ttk.Entry(params_frame)
        self.entries["pop_size"].insert(0, "20")
        self.entries["pop_size"].grid(row=2, column=1, pady=5, padx=5, sticky="ew")
        
        # Generaciones
        ttk.Label(params_frame, text="Número de Generaciones:").grid(
            row=3, column=0, sticky="w", pady=5, padx=5)
        self.entries["generations"] = ttk.Entry(params_frame)
        self.entries["generations"].insert(0, "50")
        self.entries["generations"].grid(row=3, column=1, pady=5, padx=5, sticky="ew")
        
        # Tasa de mutación
        ttk.Label(params_frame, text="Tasa de Mutación:").grid(
            row=4, column=0, sticky="w", pady=5, padx=5)
        self.entries["mutation_rate"] = ttk.Entry(params_frame)
        self.entries["mutation_rate"].insert(0, "0.1")
        self.entries["mutation_rate"].grid(row=4, column=1, pady=5, padx=5, sticky="ew")
        
        row += 1
        
        # Botón para iniciar la optimización
        btn_frame = ttk.Frame(main_frame)
        btn_frame.grid(row=row, column=0, columnspan=3, pady=20)
        
        submit_button = ttk.Button(
            btn_frame, text="Iniciar Optimización", command=self.submit, width=25)
        submit_button.pack(side="left", padx=10)
        
        reset_button = ttk.Button(
            btn_frame, text="Restablecer Valores", command=self.reset_values, width=25)
        reset_button.pack(side="right", padx=10)

    def create_results_area(self):
        """Crea el área donde se mostrarán los resultados de la optimización"""
        # Contenedor principal para los resultados
        results_container = ttk.Frame(self.results_tab)
        results_container.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Área de texto para resultados numéricos
        results_frame = ttk.LabelFrame(results_container, text="Resultados Optimizados")
        results_frame.pack(fill="x", padx=5, pady=5)
        
        self.results_text = scrolledtext.ScrolledText(results_frame, wrap=tk.WORD, height=10)
        self.results_text.pack(fill="both", expand=True, padx=5, pady=5)
        self.results_text.config(state=tk.DISABLED)
        
        # Frame para las gráficas
        self.graphs_container = ttk.Notebook(results_container)
        self.graphs_container.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Añadimos pestañas para cada tipo de gráfica
        self.fitness_tab = ttk.Frame(self.graphs_container)
        self.comparison_tab = ttk.Frame(self.graphs_container)
        self.luminosidad_tab = ttk.Frame(self.graphs_container)
        self.temperatura_tab = ttk.Frame(self.graphs_container)
        self.espacio_tab = ttk.Frame(self.graphs_container)
        self.temp_aula_tab = ttk.Frame(self.graphs_container)  # Nueva pestaña para temperatura del aula
        
        self.graphs_container.add(self.fitness_tab, text="Evolución Fitness")
        self.graphs_container.add(self.comparison_tab, text="Comparación Consumo")
        self.graphs_container.add(self.luminosidad_tab, text="Luminosidad")
        self.graphs_container.add(self.temperatura_tab, text="Temperatura")
        self.graphs_container.add(self.espacio_tab, text="Espacio/Persona")
        self.graphs_container.add(self.temp_aula_tab, text="Temperatura Aula")  # Añadir nueva pestaña
        
        # Botón para guardar resultados
        btn_frame = ttk.Frame(results_container)
        btn_frame.pack(fill="x", padx=5, pady=10)
        
        save_button = ttk.Button(
            btn_frame, text="Guardar Resultados", command=self.save_results, width=20)
        save_button.pack(side="right", padx=10)
        
        return_button = ttk.Button(
            btn_frame, text="Volver a Datos", 
            command=lambda: self.notebook.select(self.input_tab), width=20)
        return_button.pack(side="left", padx=10)

    def reset_values(self):
        """Restablece los valores de entrada a los predeterminados"""
        defaults = {
            "superficie": "50",
            "ventanas": "4",
            "coeficiente": "1.2",
            "temp_ext": "30",
            "temp_int": "22",
            "humedad": "60",
            "carga": "5000",
            "lux": "300",
            "tipo_iluminacion": "LED",
            "eficiencia": "100",
            "lamparas": "10",
            "potencia_lampara": "20",
            "alpha": "0.8",
            "beta": "0.2",
            "pop_size": "20",
            "generations": "50",
            "mutation_rate": "0.1"
        }
        
        for key, value in defaults.items():
            if key in self.entries:
                if key == "tipo_iluminacion":
                    self.entries[key].current(0)
                else:
                    self.entries[key].delete(0, tk.END)
                    self.entries[key].insert(0, value)
                    
        messagebox.showinfo("Valores Restablecidos", 
                           "Se han restablecido todos los valores a los predeterminados.")

    def validate_inputs(self):
        """Valida que todos los valores de entrada sean correctos"""
        try:
            # Validar que no haya campos vacíos
            for key, entry in self.entries.items():
                if key != "tipo_iluminacion" and not entry.get().strip():
                    messagebox.showerror("Error", f"El campo '{key}' no puede estar vacío")
                    return False
            
            # Validar que los valores numéricos sean números positivos
            numeric_fields = ["superficie", "ventanas", "coeficiente", "temp_ext", "temp_int", 
                             "humedad", "carga", "lux", "eficiencia", "lamparas", 
                             "potencia_lampara", "alpha", "beta", "pop_size", 
                             "generations", "mutation_rate"]
            
            for field in numeric_fields:
                value = self.entries[field].get()
                if field in ["ventanas", "lamparas", "pop_size", "generations"]:
                    # Campos que deben ser enteros positivos
                    value = int(value)
                    if value <= 0:
                        messagebox.showerror("Error", f"El valor de '{field}' debe ser un entero positivo")
                        return False
                else:
                    # Campos que deben ser números positivos
                    value = float(value)
                    if value <= 0:
                        messagebox.showerror("Error", f"El valor de '{field}' debe ser un número positivo")
                        return False
            
            # Validar que alpha y beta sumen 1
            alpha = float(self.entries["alpha"].get())
            beta = float(self.entries["beta"].get())
            if not 0.99 <= alpha + beta <= 1.01:  # Permitir un pequeño margen de error
                messagebox.showwarning("Advertencia", 
                                     "Los factores α y β deberían sumar aproximadamente 1.0")
                # No retornamos False aquí, es solo una advertencia
            
            return True
            
        except ValueError as e:
            messagebox.showerror("Error", f"Error en la conversión de valores: {e}")
            return False
        except Exception as e:
            messagebox.showerror("Error", f"Error inesperado: {e}")
            return False

    def submit(self):
        """
        Recoge los datos ingresados, valida, crea el objeto de entrada, 
        instancia y ejecuta el algoritmo genético.
        """
        if not self.validate_inputs():
            return
            
        try:
            # Recoger los datos validados
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
            
            # Parámetros del algoritmo
            pop_size = int(self.entries["pop_size"].get())
            generations = int(self.entries["generations"].get())
            mutation_rate = float(self.entries["mutation_rate"].get())
            
            # Mostrar mensaje de procesamiento
            self.config(cursor="wait")
            message_window = tk.Toplevel(self)
            message_window.title("Procesando")
            message_window.geometry("300x100")
            message_window.transient(self)
            message_window.grab_set()
            
            message_label = ttk.Label(
                message_window, 
                text="Ejecutando la optimización...\nEsto puede tardar unos segundos.",
                wraplength=280)
            message_label.pack(expand=True, fill="both", padx=20, pady=20)
            
            # Actualizar la ventana
            self.update_idletasks()
            
            # Instanciar el algoritmo genético con los parámetros ingresados
            ga = OptiluzGA(data, pop_size=pop_size)
            
            # Configurar para capturar las gráficas en lugar de mostrarlas directamente
            self.capture_plots(ga, generations, mutation_rate)
            
            # Cerrar la ventana de mensaje y restaurar el cursor
            message_window.destroy()
            self.config(cursor="")
            
            # Cambiar a la pestaña de resultados
            self.notebook.select(self.results_tab)
            
        except Exception as e:
            messagebox.showerror("Error", f"Error al procesar los datos: {e}")
            self.config(cursor="")

    def capture_plots(self, ga, generations, mutation_rate):
        """
        Ejecuta el algoritmo genético y captura las gráficas para mostrarlas en la interfaz
        en lugar de abrirlas directamente.
        """
        # Sobreescribir temporalmente las funciones de gráficas para capturarlas
        original_plot_fitness = ga.plot_fitness
        original_plot_comparison = ga.plot_comparison
        original_plot_luminosidad = ga.plot_luminosidad
        original_plot_temperatura = ga.plot_temperatura
        original_plot_espacio_persona = ga.plot_espacio_persona
        original_plot_avg_temperature = ga.plot_avg_temperature
        
        # Variables para guardar las figuras
        self.fitness_fig = None
        self.comparison_fig = None
        self.luminosidad_fig = None
        self.temperatura_fig = None
        self.espacio_fig = None
        self.temp_aula_fig = None
        
        # Redefinir plot_fitness
        def captured_plot_fitness():
            self.fitness_fig = plt.figure(figsize=(8, 5))
            plt.plot(ga.fitness_history, marker='o', linestyle='-', color='b')
            plt.xlabel("Generaciones")
            plt.ylabel("Fitness (Menor es Mejor)")
            plt.title("Evolución de la Función de Fitness")
            plt.grid(True)
            plt.close()  # No mostrar, solo guardar la figura
        
        # Redefinir plot_comparison
        def captured_plot_comparison(consumo_antes, consumo_despues):
            self.comparison_fig = plt.figure(figsize=(6, 5))
            labels = ["Consumo Base", "Consumo Óptimo"]
            valores = [consumo_antes, consumo_despues]
            plt.bar(labels, valores, color=['red', 'green'])
            plt.xlabel("Estado")
            plt.ylabel("Consumo Energético (kWh)")
            plt.title("Comparación de Consumo Energético")
            plt.close()  # No mostrar, solo guardar la figura
        
        # Redefinir plot_luminosidad
        def captured_plot_luminosidad():
            self.luminosidad_fig = plt.figure(figsize=(8, 5))
            p_luz_vals = [sol['P_luz'] for sol in ga.best_solution_history]
            plt.plot(p_luz_vals, marker='o')
            plt.title("Evolución de la Luminosidad (Potencia de Iluminación)")
            plt.xlabel("Generaciones")
            plt.ylabel("P_luz (W)")
            plt.grid(True)
            plt.close()  # No mostrar, solo guardar la figura
        
        # Redefinir plot_temperatura
        def captured_plot_temperatura():
            self.temperatura_fig = plt.figure(figsize=(8, 5))
            u_vals = [sol['U'] for sol in ga.best_solution_history]
            plt.plot(u_vals, marker='o')
            plt.title("Evolución de la 'Temperatura' (Coef. U)")
            plt.xlabel("Generaciones")
            plt.ylabel("U (Coef. Transmisión Térmica)")
            plt.grid(True)
            plt.close()  # No mostrar, solo guardar la figura
        
        # Redefinir plot_espacio_persona
        def captured_plot_espacio_persona():
            self.espacio_fig = plt.figure(figsize=(8, 5))
            A = ga.input_data.superficie
            espacios = []
            for sol in ga.best_solution_history:
                n = sol['N_personas']
                if n != 0:
                    espacios.append(A / n)
                else:
                    espacios.append(A)  # Si n=0, evitamos división por cero
            plt.plot(espacios, marker='o')
            plt.title("Evolución del Espacio por Persona (m²/persona)")
            plt.xlabel("Generaciones")
            plt.ylabel("m²/persona")
            plt.grid(True)
            plt.close()  # No mostrar, solo guardar la figura
            
        # Redefinir plot_avg_temperature
        def captured_plot_avg_temperature():
            try:
                self.temp_aula_fig = plt.figure(figsize=(8, 5))
                
                # Asegurarnos de que temperature_history tiene datos
                if not hasattr(ga, 'temperature_history') or not ga.temperature_history:
                    # Crear un historial de temperaturas basado en el historial de soluciones
                    temps = []
                    for sol in ga.best_solution_history:
                        temp = ga.calculate_avg_temperature(sol)
                        temps.append(temp)
                    
                    generaciones = range(len(temps))
                    plt.plot(generaciones, temps, marker='o', linestyle='-', color='#FF7043')
                    
                    # Añadir temperatura final
                    if temps:
                        plt.axhline(y=temps[-1], color='red', linestyle='--', 
                                label=f'Temperatura final: {temps[-1]:.2f} °C')
                else:
                    # Usar el historial existente
                    generaciones = range(len(ga.temperature_history))
                    plt.plot(generaciones, ga.temperature_history, marker='o', linestyle='-', color='#FF7043')
                    
                    # Añadir valor óptimo final
                    if ga.temperature_history:
                        plt.axhline(y=ga.temperature_history[-1], color='red', linestyle='--', 
                                label=f'Temperatura final: {ga.temperature_history[-1]:.2f} °C')
                
                # Añadir temperatura deseada como referencia
                plt.axhline(y=ga.input_data.temp_int, color='blue', linestyle=':', 
                        label=f'Temperatura deseada: {ga.input_data.temp_int:.1f} °C')
                
                # Añadir zona de confort térmico (±2°C de la temperatura deseada)
                plt.axhspan(
                    ga.input_data.temp_int - 2, 
                    ga.input_data.temp_int + 2, 
                    alpha=0.2, color='green', 
                    label='Zona de confort (±2°C)'
                )
                
                plt.title("Evolución de la Temperatura Promedio del Aula")
                plt.xlabel("Generaciones")
                plt.ylabel("Temperatura (°C)")
                plt.legend()
                plt.grid(True)
                plt.close()  # No mostrar, solo guardar la figura
            except Exception as e:
                # En caso de error, crear una gráfica simple con mensaje de error
                self.temp_aula_fig = plt.figure(figsize=(8, 5))
                plt.text(0.5, 0.5, f"Error al generar gráfica: {str(e)}", 
                        ha='center', va='center', transform=plt.gca().transAxes)
                plt.close()
        
        # Asignar las nuevas funciones
        ga.plot_fitness = captured_plot_fitness
        ga.plot_comparison = captured_plot_comparison
        ga.plot_luminosidad = captured_plot_luminosidad
        ga.plot_temperatura = captured_plot_temperatura
        ga.plot_espacio_persona = captured_plot_espacio_persona
        ga.plot_avg_temperature = captured_plot_avg_temperature
        
        # Ejecutar el algoritmo genético
        ga.run_evolution(generations=generations, mutation_rate=mutation_rate)
        
        # Restaurar las funciones originales
        ga.plot_fitness = original_plot_fitness
        ga.plot_comparison = original_plot_comparison
        ga.plot_luminosidad = original_plot_luminosidad
        ga.plot_temperatura = original_plot_temperatura
        ga.plot_espacio_persona = original_plot_espacio_persona
        ga.plot_avg_temperature = original_plot_avg_temperature
        
        # Mostrar los resultados en el área de texto
        self.display_text_results(ga)
        
        # Mostrar las gráficas capturadas en las pestañas correspondientes
        self.display_captured_plots()

    def display_text_results(self, ga):
        """Muestra los resultados de texto en el área de resultados"""
        self.results_text.config(state=tk.NORMAL)
        self.results_text.delete(1.0, tk.END)
        
        try:
            # Calcular resultados
            consumo_antes = ga.input_data.carga + ga.input_data.lamparas * ga.input_data.potencia_lampara
            consumo_despues = (ga.best_solution['BTU'] / 1000) + ga.best_solution['P_luz'] / 10
            
            if ga.input_data.superficie != 0:
                personas_por_m2 = ga.best_solution['N_personas'] / ga.input_data.superficie
            else:
                personas_por_m2 = 0
                
            # Calcular la temperatura promedio del aula con manejo de errores
            try:
                if 'temp_promedio' in ga.best_solution:
                    temp_promedio = ga.best_solution['temp_promedio']
                else:
                    temp_promedio = ga.calculate_avg_temperature(ga.best_solution)
            except Exception as e:
                temp_promedio = 0.0
                print(f"Error al calcular temperatura: {e}")
            
            # Formatear resultados
            results_text = f"""📊 RESULTADOS OPTIMIZADOS:

    Capacidad Óptima del Aire Acondicionado: {ga.best_solution['BTU']:.2f} BTU
    Tipo de Aire Acondicionado Recomendado: {ga.get_AC_type(ga.best_solution['BTU'])}
    Potencia de Iluminación Recomendada: {ga.best_solution['P_luz']:.2f} W
    Nivel Óptimo de Aislamiento Térmico (U): {ga.best_solution['U']:.2f}
    Cantidad Recomendada de Personas por Aula: {ga.best_solution['N_personas']}
    Cantidad de personas por m²: {personas_por_m2:.2f}

    Consumo Base: {consumo_antes:.2f} kWh
    Consumo Óptimo: {consumo_despues:.2f} kWh
    Ahorro Energético: {consumo_antes - consumo_despues:.2f} kWh ({(1 - consumo_despues/consumo_antes) * 100:.1f}%)
    """

            # Agregar información de temperatura solo si está disponible
            if temp_promedio > 0:
                results_text += f"""
    Temperatura Promedio del Aula: {temp_promedio:.1f} °C
    (Temperatura deseada: {ga.input_data.temp_int:.1f} °C)
    """
            
            results_text += f"""
    Mejor Fitness alcanzado: {ga.best_fitness:.2f}
    """
            
            self.results_text.insert(tk.END, results_text)
        except Exception as e:
            error_msg = f"Error al mostrar resultados: {str(e)}"
            self.results_text.insert(tk.END, error_msg)
            print(error_msg)
        
        self.results_text.config(state=tk.DISABLED)
    def display_captured_plots(self):
        """Muestra las gráficas capturadas en sus respectivas pestañas"""
        # Limpiar contenido anterior
        for tab in [self.fitness_tab, self.comparison_tab, self.luminosidad_tab, 
                   self.temperatura_tab, self.espacio_tab, self.temp_aula_tab]:
            for widget in tab.winfo_children():
                widget.destroy()
        
        # Mostrar gráfica de fitness
        if self.fitness_fig:
            canvas = FigureCanvasTkAgg(self.fitness_fig, self.fitness_tab)
            canvas.draw()
            canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        # Mostrar gráfica de comparación
        if self.comparison_fig:
            canvas = FigureCanvasTkAgg(self.comparison_fig, self.comparison_tab)
            canvas.draw()
            canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        # Mostrar gráfica de luminosidad
        if self.luminosidad_fig:
            canvas = FigureCanvasTkAgg(self.luminosidad_fig, self.luminosidad_tab)
            canvas.draw()
            canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        # Mostrar gráfica de temperatura
        if self.temperatura_fig:
            canvas = FigureCanvasTkAgg(self.temperatura_fig, self.temperatura_tab)
            canvas.draw()
            canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        # Mostrar gráfica de espacio por persona
        if self.espacio_fig:
            canvas = FigureCanvasTkAgg(self.espacio_fig, self.espacio_tab)
            canvas.draw()
            canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
            
        if self.temp_aula_fig:
            canvas = FigureCanvasTkAgg(self.temp_aula_fig, self.temp_aula_tab)
            canvas.draw()
            canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

    def save_results(self):
        """Guarda los resultados en un archivo de texto"""
        try:
            from tkinter import filedialog
            import datetime
            
            # Obtener fecha y hora actual para el nombre del archivo
            now = datetime.datetime.now()
            default_filename = f"optiluz_resultados_{now.strftime('%Y%m%d_%H%M%S')}.txt"
            
            # Abrir diálogo para guardar archivo
            filename = filedialog.asksaveasfilename(
                defaultextension=".txt",
                filetypes=[("Archivos de texto", "*.txt"), ("Todos los archivos", "*.*")],
                initialfile=default_filename
            )
            
            if not filename:  # Si el usuario cancela
                return
                
            # Guardar el contenido del área de resultados
            with open(filename, 'w', encoding='utf-8') as f:
                f.write("OPTILUZ - RESULTADOS DE OPTIMIZACIÓN\n")
                f.write(f"Fecha: {now.strftime('%d-%m-%Y %H:%M:%S')}\n\n")
                f.write(self.results_text.get(1.0, tk.END))
                
                # Agregar información sobre los parámetros utilizados
                f.write("\n\nPARÁMETROS UTILIZADOS:\n")
                for key, entry in self.entries.items():
                    f.write(f"{key}: {entry.get()}\n")
                    
            messagebox.showinfo("Guardado Exitoso", 
                               f"Los resultados han sido guardados en:\n{filename}")
            
        except Exception as e:
            messagebox.showerror("Error al Guardar", f"No se pudo guardar el archivo: {e}")