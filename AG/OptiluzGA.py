# optiluz_ga.py

import random
import matplotlib.pyplot as plt

class OptiluzGA:
    """
    Clase que maneja el algoritmo genético para OptiLuz.
    Incluye métodos para inicializar la población, evaluar la función de fitness,
    ejecutar la evolución y generar visualizaciones de los resultados.
    """
    def __init__(self, input_data, pop_size=10):
        self.input_data = input_data
        self.pop_size = pop_size
        self.population = []
        self.fitness_history = []
        self.best_solution = None
        self.best_fitness = float('inf')

        # Rango de valores para cada variable optimizable
        self.bounds = {
            'BTU': (10000, 50000),      # Capacidad del aire acondicionado en BTU
            'P_luz': (100, 2000),        # Potencia de iluminación en W
            'U': (0.2, 2.5),             # Coeficiente de transmisión térmica (aislamiento)
            'N_personas': (10, 50)       # Cantidad de personas recomendadas por aula
        }

        self.best_solution_history = []  # <-- NUEVO: Para guardar el mejor individuo en cada generación
    
    def initialize_population(self):
        """Inicializa la población de individuos con valores aleatorios dentro de los límites definidos."""
        self.population = [
            {
                'BTU': random.uniform(self.bounds['BTU'][0], self.bounds['BTU'][1]),
                'P_luz': random.uniform(self.bounds['P_luz'][0], self.bounds['P_luz'][1]),
                'U': random.uniform(self.bounds['U'][0], self.bounds['U'][1]),
                'N_personas': random.randint(self.bounds['N_personas'][0], self.bounds['N_personas'][1])
            } for _ in range(self.pop_size)
        ]
    
    def evaluate_individual(self, individual):
        """
        Evalúa un individuo utilizando la función de fitness definida para OptiLuz.
        Se emplean las fórmulas basadas en los datos de entrada y los genes del individuo.
        """
        # Extraer genes del individuo
        BTU_gene = individual['BTU']
        P_luz_gene = individual['P_luz']
        U_gene = individual['U']
        N_personas_gene = individual['N_personas']
        
        # Extraer parámetros de entrada
        A_aula = self.input_data.superficie
        ventanas = self.input_data.ventanas
        carga = self.input_data.carga
        lux = self.input_data.lux
        eficiencia = self.input_data.eficiencia
        temp_ext = self.input_data.temp_ext
        temp_int = self.input_data.temp_int
        
        # Constantes de las fórmulas
        AC_factor = 337       # Factor asociado a la superficie del aula para BTU
        PERSON_factor = 600   # Factor asociado a la cantidad de personas para BTU
        EQUIP_factor = 300    # Factor asociado a la carga térmica de equipos
        window_area = 1.5     # Área promedio de cada ventana (m²), valor asumido
        
        # Cálculo del BTU óptimo teórico basado en los datos
        BTU_optimal = (A_aula * AC_factor) + (N_personas_gene * PERSON_factor) + (carga * EQUIP_factor)
        error_AC = abs(BTU_gene - BTU_optimal)
        
        # Cálculo de la potencia de iluminación óptima
        P_luz_optimal = (lux * A_aula) / eficiencia
        error_luz = abs(P_luz_gene - P_luz_optimal)
        
        # Cálculo de la pérdida de calor (W) debido al aislamiento térmico
        A_ventanas = ventanas * window_area
        Q_perdida = U_gene * A_ventanas * abs(temp_ext - temp_int)
        error_loss = Q_perdida  # Se busca minimizar la pérdida de calor
        
        # Cálculo de la cantidad de personas óptima derivada del BTU
        N_personas_optimal = (BTU_gene - (A_aula * AC_factor) - (carga * EQUIP_factor)) / PERSON_factor
        error_personas = abs(N_personas_gene - N_personas_optimal)
        
        # Suma de errores (consumo energético total) y penalización por desviación en cantidad de personas
        E_total = error_AC + error_luz + error_loss
        C_penalizacion = error_personas
        
        # Factores de ponderación (ingresados en la interfaz)
        alpha = self.input_data.alpha
        beta = self.input_data.beta
        
        # Función de fitness: se busca minimizar tanto el consumo energético total como la penalización
        fitness = alpha * E_total + beta * C_penalizacion
        return fitness
    
    def evaluate_population(self):
        """Evalúa toda la población, actualizando el mejor individuo y almacenando la historia del fitness."""
        fitness_values = [self.evaluate_individual(ind) for ind in self.population]
        min_fitness = min(fitness_values)
        best_idx = fitness_values.index(min_fitness)
        self.best_solution = self.population[best_idx]
        self.best_fitness = min_fitness
        self.fitness_history.append(min_fitness)

        self.best_solution_history.append(self.best_solution.copy())  # <-- NUEVO: Guardamos el mejor de esta generación
        
        return fitness_values
    
    def selection(self, tournament_size=3):
        """
        Realiza la selección de individuos mediante el método de torneo.
        Se selecciona el individuo con menor fitness de un grupo aleatorio de tamaño tournament_size.
        """
        selected = []
        for _ in range(self.pop_size):
            tournament = random.sample(self.population, tournament_size)
            best = min(tournament, key=self.evaluate_individual)
            selected.append(best)
        return selected
    
    def crossover(self, parent1, parent2):
        """
        Realiza el cruce en un punto entre dos padres.
        Se intercambian los genes a partir de un punto de cruce aleatorio.
        """
        keys = ['BTU', 'P_luz', 'U', 'N_personas']
        crossover_point = random.randint(1, len(keys) - 1)
        child1, child2 = {}, {}
        for i, key in enumerate(keys):
            if i < crossover_point:
                child1[key] = parent1[key]
                child2[key] = parent2[key]
            else:
                child1[key] = parent2[key]
                child2[key] = parent1[key]
        return child1, child2
    
    def mutate(self, individual, mutation_rate=0.1):
        """
        Aplica mutación a un individuo.
        Cada gen tiene una probabilidad mutation_rate de ser modificado.
        Se usa random.uniform para variables continuas y random.randint para la variable entera.
        """
        keys = ['BTU', 'P_luz', 'U', 'N_personas']
        for key in keys:
            if random.random() < mutation_rate:
                if key == 'N_personas':
                    individual[key] = random.randint(self.bounds[key][0], self.bounds[key][1])
                else:
                    individual[key] = random.uniform(self.bounds[key][0], self.bounds[key][1])
        return individual
    
    def evolve_population(self, mutation_rate=0.1, tournament_size=3):
        """
        Ejecuta un ciclo de evolución: selección, cruce y mutación para generar una nueva población.
        """
        new_population = []
        selected = self.selection(tournament_size)
        random.shuffle(selected)
        
        # Cruzamos en pares
        for i in range(0, len(selected) - 1, 2):
            parent1 = selected[i]
            parent2 = selected[i + 1]
            child1, child2 = self.crossover(parent1, parent2)
            child1 = self.mutate(child1, mutation_rate)
            child2 = self.mutate(child2, mutation_rate)
            new_population.extend([child1, child2])
        
        # Si la población es impar, agregamos el último individuo sin modificar
        if len(selected) % 2 == 1:
            new_population.append(selected[-1])
        
        self.population = new_population
        return self.population
    
    def run_evolution(self, generations=50, mutation_rate=0.1, tournament_size=3):
        """
        Ejecuta el ciclo completo de evolución del algoritmo genético durante un número de generaciones.
        Imprime el mejor fitness de cada generación, y al finalizar muestra los resultados y las visualizaciones.
        """
        self.initialize_population()
        for gen in range(generations):
            self.evaluate_population()
            print(f"Generación {gen+1}: Mejor Fitness = {self.best_fitness:.2f}")
            self.evolve_population(mutation_rate, tournament_size)
        self.display_results()
    
    def display_results(self):
        """Muestra los resultados finales y genera las visualizaciones de la evolución del fitness y del consumo energético."""
        print("\n📊 RESULTADOS OPTIMIZADOS:")
        print(f"Capacidad Óptima del Aire Acondicionado: {self.best_solution['BTU']:.2f} BTU")
        print(f"Tipo de Aire Acondicionado Recomendado: {self.get_AC_type(self.best_solution['BTU'])}")
        print(f"Potencia de Iluminación Recomendada: {self.best_solution['P_luz']:.2f} W")
        print(f"Nivel Óptimo de Aislamiento Térmico (U): {self.best_solution['U']:.2f}")
        print(f"Cantidad Recomendada de Personas por Aula: {self.best_solution['N_personas']}\n")

        # Simulación de consumo energético antes y después de la optimización (valores estimados)
        consumo_antes = self.input_data.carga + self.input_data.lamparas * self.input_data.potencia_lampara
        consumo_despues = (self.best_solution['BTU'] / 1000) + self.best_solution['P_luz'] / 10

        # <-- NUEVO: Cantidad de personas por m²
        if self.input_data.superficie != 0:
            personas_por_m2 = self.best_solution['N_personas'] / self.input_data.superficie
        else:
            personas_por_m2 = 0
        print(f"Cantidad de personas por m²: {personas_por_m2:.2f}\n")  # <-- NUEVO

        # <-- NUEVO: Renombrar consumos a “Consumo Base” y “Consumo Óptimo”
        print(f"⚡ Consumo Base: {consumo_antes:.2f} kWh")
        print(f"⚡ Consumo Óptimo: {consumo_despues:.2f} kWh")

        # Generar gráficos
        self.plot_fitness()
        self.plot_comparison(consumo_antes, consumo_despues)

        # <-- NUEVO: Llamamos a las gráficas extra
        self.plot_luminosidad()
        self.plot_temperatura()
        self.plot_espacio_persona()

    def get_AC_type(self, BTU):
        """
        Determina el tipo de aire acondicionado recomendado en función del BTU optimizado.
        Se clasifican en tres rangos para este ejemplo.
        """
        if BTU < 12000:
            return "Unidad de Ventana (SEER 10-12)"
        elif BTU < 24000:
            return "Mini Split (SEER 15-20)"
        else:
            return "Sistema Centralizado (SEER 20+)"
    
    def plot_fitness(self):
        """Genera un gráfico que muestra la evolución de la función de fitness a lo largo de las generaciones."""
        plt.figure(figsize=(8, 5))
        plt.plot(self.fitness_history, marker='o', linestyle='-', color='b')
        plt.xlabel("Generaciones")
        plt.ylabel("Fitness (Menor es Mejor)")
        plt.title("Evolución de la Función de Fitness")
        plt.grid(True)
        plt.show()

    def plot_comparison(self, consumo_antes, consumo_despues):
        """Genera un gráfico de barras comparando el consumo energético base y óptimo."""
        labels = ["Consumo Base", "Consumo Óptimo"]  # <-- NUEVO: Renombramos aquí
        valores = [consumo_antes, consumo_despues]
        
        plt.figure(figsize=(6, 5))
        plt.bar(labels, valores, color=['red', 'green'])
        plt.xlabel("Estado")
        plt.ylabel("Consumo Energético (kWh)")
        plt.title("Comparación de Consumo Energético")
        plt.show()

    def print_population(self):
        """Imprime en consola la población actual y sus valores de fitness."""
        fitness_values = [self.evaluate_individual(ind) for ind in self.population]
        for idx, (ind, fit) in enumerate(zip(self.population, fitness_values), start=1):
            print(f"Individuo {idx}: {ind} | Fitness: {fit:.2f}")

    # =============================
    # ========== NUEVO ============
    # =============================

    def plot_luminosidad(self):
        """
        Gráfica de la luminosidad (P_luz) del mejor individuo en cada generación,
        para ver cómo evoluciona la potencia de iluminación recomendada.
        """
        p_luz_vals = [sol['P_luz'] for sol in self.best_solution_history]
        plt.figure()
        plt.plot(p_luz_vals, marker='o')
        plt.title("Evolución de la Luminosidad (Potencia de Iluminación)")
        plt.xlabel("Generaciones")
        plt.ylabel("P_luz (W)")
        plt.grid(True)
        plt.show()

    def plot_temperatura(self):
        """
        Gráfica del coeficiente U (aislamiento), usándolo como un proxy de la 'temperatura'.
        Mientras más bajo sea U, mejor aislamiento y menor pérdida de calor.
        """
        u_vals = [sol['U'] for sol in self.best_solution_history]
        plt.figure()
        plt.plot(u_vals, marker='o')
        plt.title("Evolución de la 'Temperatura' (Coef. U)")
        plt.xlabel("Generaciones")
        plt.ylabel("U (Coef. Transmisión Térmica)")
        plt.grid(True)
        plt.show()

    def plot_espacio_persona(self):
        """
        Gráfica de cuántos m² por persona hay en el mejor individuo de cada generación:
        A_aula / N_personas.
        """
        A = self.input_data.superficie
        espacios = []
        for sol in self.best_solution_history:
            n = sol['N_personas']
            if n != 0:
                espacios.append(A / n)
            else:
                espacios.append(A)  # Si n=0, evitamos división por cero
        plt.figure()
        plt.plot(espacios, marker='o')
        plt.title("Evolución del Espacio por Persona (m²/persona)")
        plt.xlabel("Generaciones")
        plt.ylabel("m²/persona")
        plt.grid(True)
        plt.show()
