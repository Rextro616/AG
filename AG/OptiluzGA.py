import random
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator

class OptiluzGA:
    """
    Clase mejorada que maneja el algoritmo genético para OptiLuz.
    Incluye elitismo, mejores métodos de selección y visualizaciones mejoradas.
    """
    def __init__(self, input_data, pop_size=20):
        self.input_data = input_data
        self.pop_size = pop_size
        self.population = []
        self.fitness_history = []
        self.best_solution = None
        self.best_fitness = float('inf')
        self.best_solution_history = []  # Para guardar el mejor individuo de cada generación
        
        # Definir rangos para cada variable optimizable (con límites más precisos)
        self.bounds = {
            'BTU': (8000, 60000),       # Capacidad del aire acondicionado en BTU
            'P_luz': (50, 3000),         # Potencia de iluminación en W
            'U': (0.1, 3.0),             # Coeficiente de transmisión térmica (aislamiento)
            'N_personas': (5, 100)       # Cantidad de personas recomendadas por aula
        }
        
        # Ajustar límites basados en las entradas
        self._adjust_bounds()
        
        # Factores para la evaluación
        self.BTU_FACTOR = 337        # Factor asociado a la superficie del aula para BTU
        self.PERSON_FACTOR = 600     # Factor asociado a la cantidad de personas para BTU
        self.EQUIP_FACTOR = 300      # Factor asociado a la carga térmica de equipos
        self.WINDOW_AREA = 1.5       # Área promedio de cada ventana (m²)
    
    def _adjust_bounds(self):
        """Ajusta los límites de las variables según las entradas"""
        # Ajustar BTU basado en la superficie y carga
        min_btu = (self.input_data.superficie * 250) + (self.input_data.carga / 2)
        max_btu = (self.input_data.superficie * 450) + (self.input_data.carga * 1.5)
        self.bounds['BTU'] = (max(8000, min_btu), max(60000, max_btu))
        
        # Ajustar P_luz basado en la iluminación requerida
        min_luz = (self.input_data.lux * self.input_data.superficie) / (self.input_data.eficiencia * 1.5)
        max_luz = (self.input_data.lux * self.input_data.superficie) / (self.input_data.eficiencia * 0.7)
        self.bounds['P_luz'] = (max(50, min_luz), max(3000, max_luz))
        
        # Ajustar N_personas basado en la superficie (aproximadamente 1.5-4 m² por persona)
        min_personas = max(5, self.input_data.superficie / 4)
        max_personas = min(100, self.input_data.superficie / 1.5)
        self.bounds['N_personas'] = (int(min_personas), int(max_personas))
    
    def initialize_population(self):
        """Inicializa la población con valores aleatorios dentro de los límites definidos."""
        self.population = []
        for _ in range(self.pop_size):
            individual = {
                'BTU': random.uniform(self.bounds['BTU'][0], self.bounds['BTU'][1]),
                'P_luz': random.uniform(self.bounds['P_luz'][0], self.bounds['P_luz'][1]),
                'U': random.uniform(self.bounds['U'][0], self.bounds['U'][1]),
                'N_personas': random.randint(self.bounds['N_personas'][0], self.bounds['N_personas'][1])
            }
            self.population.append(individual)
    
    def evaluate_individual(self, individual):
        """
        Evalúa un individuo utilizando la función de fitness definida para OptiLuz.
        Retorna el valor de fitness (menor es mejor).
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
        
        # Cálculo del BTU óptimo teórico basado en los datos
        BTU_optimal = (A_aula * self.BTU_FACTOR) + (N_personas_gene * self.PERSON_FACTOR) + (carga * self.EQUIP_FACTOR)
        # Penalización si el BTU es insuficiente (mayor penalización) o excesivo
        if BTU_gene < BTU_optimal:
            error_AC = 1.5 * abs(BTU_gene - BTU_optimal) / BTU_optimal  # Mayor penalización si es insuficiente
        else:
            error_AC = abs(BTU_gene - BTU_optimal) / BTU_optimal
        
        # Cálculo de la potencia de iluminación óptima
        P_luz_optimal = (lux * A_aula) / eficiencia
        # Penalización si la iluminación es insuficiente o excesiva
        if P_luz_gene < P_luz_optimal:
            error_luz = 1.2 * abs(P_luz_gene - P_luz_optimal) / P_luz_optimal  # Mayor si es insuficiente
        else:
            error_luz = abs(P_luz_gene - P_luz_optimal) / P_luz_optimal
        
        # Cálculo de la pérdida de calor (W) debido al aislamiento térmico
        A_ventanas = ventanas * self.WINDOW_AREA
        Q_perdida = U_gene * A_ventanas * abs(temp_ext - temp_int)
        error_loss = Q_perdida / 1000  # Normalizado
        
        # Cálculo de cantidad de personas óptima derivada del BTU
        if self.PERSON_FACTOR > 0:
            N_personas_optimal = max(5, (BTU_gene - (A_aula * self.BTU_FACTOR) - (carga * self.EQUIP_FACTOR)) / self.PERSON_FACTOR)
            error_personas = abs(N_personas_gene - N_personas_optimal) / max(N_personas_optimal, 1)
        else:
            error_personas = 0
        
        # Densidad de ocupación (m² por persona)
        densidad = A_aula / N_personas_gene if N_personas_gene > 0 else float('inf')
        
        # Penalización por densidad de ocupación inadecuada
        if densidad < 1.0:  # Muy poco espacio por persona
            error_densidad = 2.0  # Alta penalización
        elif densidad < 1.5:  # Espacio ajustado
            error_densidad = 1.0
        elif densidad > 5.0:  # Desperdicio de espacio
            error_densidad = (densidad - 5.0) / 5.0
        else:
            error_densidad = 0.0  # Densidad óptima
        
        # Consumo energético total normalizado
        E_total = 0.4 * error_AC + 0.3 * error_luz + 0.3 * error_loss
        
        # Confort/penalización
        C_penalizacion = 0.7 * error_personas + 0.3 * error_densidad
        
        # Factores de ponderación (ingresados en la interfaz)
        alpha = self.input_data.alpha
        beta = self.input_data.beta
        
        # Función de fitness
        fitness = alpha * E_total + beta * C_penalizacion
        return fitness
    
    def evaluate_population(self):
        """Evalúa toda la población y actualiza el mejor individuo encontrado."""
        fitness_values = []
        for ind in self.population:
            fitness = self.evaluate_individual(ind)
            fitness_values.append(fitness)
        
        # Encontrar el mejor individuo de esta generación
        min_fitness = min(fitness_values)
        best_idx = fitness_values.index(min_fitness)
        
        # Actualizar el mejor global si es mejor que el anterior
        if min_fitness < self.best_fitness:
            self.best_solution = self.population[best_idx].copy()
            self.best_fitness = min_fitness
        
        # Guardar el mejor de esta generación para el historial
        self.best_solution_history.append(self.population[best_idx].copy())
        self.fitness_history.append(min_fitness)
        
        return fitness_values
    
    def selection(self, fitness_values, tournament_size=3, elitism=2):
        """
        Realiza la selección mediante el método de torneo, con opción de elitismo.
        El parámetro elitism indica cuántos de los mejores individuos pasarán directamente.
        """
        selected = []
        
        # Ordenar la población por fitness (menor es mejor)
        sorted_indices = sorted(range(len(fitness_values)), key=lambda i: fitness_values[i])
        
        # Elitismo: los mejores individuos pasan directamente
        for i in range(min(elitism, self.pop_size)):
            selected.append(self.population[sorted_indices[i]].copy())
        
        # Selección por torneo para el resto
        while len(selected) < self.pop_size:
            # Seleccionar aleatoriamente individuos para el torneo
            tournament_indices = random.sample(range(len(self.population)), tournament_size)
            # Encontrar el mejor del torneo
            best_in_tournament = min(tournament_indices, key=lambda i: fitness_values[i])
            selected.append(self.population[best_in_tournament].copy())
        
        return selected
    
    def crossover(self, parent1, parent2, crossover_rate=0.9):
        """
        Realiza el cruce entre dos padres con una probabilidad dada.
        Si no hay cruce, retorna copias de los padres.
        """
        if random.random() > crossover_rate:
            return parent1.copy(), parent2.copy()
            
        # Lista de genes a cruzar
        keys = list(parent1.keys())
        
        # Cruce aritmético para variables continuas, un punto para discretas
        child1, child2 = {}, {}
        
        # Determinar el punto de cruce para variables discretas
        crossover_point = random.randint(1, len(keys) - 1)
        
        for i, key in enumerate(keys):
            if key == 'N_personas':  # Variable discreta
                if i < crossover_point:
                    child1[key] = parent1[key]
                    child2[key] = parent2[key]
                else:
                    child1[key] = parent2[key]
                    child2[key] = parent1[key]
            else:  # Variables continuas: cruce aritmético
                # Generar un factor de mezcla aleatorio
                alpha = random.random()
                child1[key] = alpha * parent1[key] + (1 - alpha) * parent2[key]
                child2[key] = (1 - alpha) * parent1[key] + alpha * parent2[key]
                
                # Asegurar que están dentro de los límites
                child1[key] = max(self.bounds[key][0], min(self.bounds[key][1], child1[key]))
                child2[key] = max(self.bounds[key][0], min(self.bounds[key][1], child2[key]))
        
        return child1, child2
    
    def mutate(self, individual, mutation_rate=0.1):
        """
        Aplica mutación a un individuo.
        La intensidad de la mutación se reduce con el tiempo para afinar la búsqueda.
        """
        mutated = individual.copy()
        
        for key in mutated:
            # Aplicar mutación con probabilidad mutation_rate
            if random.random() < mutation_rate:
                if key == 'N_personas':  # Variable discreta
                    # Mutación aditiva: sumar o restar un pequeño valor aleatorio
                    delta = random.randint(-5, 5)
                    mutated[key] += delta
                    # Asegurar que está dentro de los límites
                    mutated[key] = max(self.bounds[key][0], min(self.bounds[key][1], mutated[key]))
                else:  # Variables continuas
                    # Mutación basada en distribución normal
                    # La varianza se reduce para una búsqueda más fina
                    lower, upper = self.bounds[key]
                    range_size = upper - lower
                    
                    # Calcular sigma como un porcentaje del rango
                    sigma = range_size * 0.1
                    
                    # Generar un valor aleatorio según distribución normal
                    delta = random.gauss(0, sigma)
                    mutated[key] += delta
                    
                    # Asegurar que está dentro de los límites
                    mutated[key] = max(lower, min(upper, mutated[key]))
        
        return mutated
    
    def evolve_population(self, fitness_values, mutation_rate=0.1, crossover_rate=0.9, 
                         tournament_size=3, elitism=2):
        """
        Ejecuta un ciclo de evolución completo: selección, cruce y mutación.
        """
        # Selección
        selected = self.selection(fitness_values, tournament_size, elitism)
        
        # Crear nueva población
        new_population = []
        
        # Elitismo: los mejores pasan directamente
        for i in range(elitism):
            if i < len(selected):
                new_population.append(selected[i])
        
        # Cruce y mutación para el resto
        # Barajar la lista para no emparejar siempre los mismos
        remaining = selected[elitism:]
        random.shuffle(remaining)
        
        for i in range(0, len(remaining) - 1, 2):
            parent1 = remaining[i]
            parent2 = remaining[i + 1]
            
            # Cruce
            child1, child2 = self.crossover(parent1, parent2, crossover_rate)
            
            # Mutación
            child1 = self.mutate(child1, mutation_rate)
            child2 = self.mutate(child2, mutation_rate)
            
            # Añadir a la nueva población
            new_population.extend([child1, child2])
        
        # Si falta un individuo (población impar)
        if len(new_population) < self.pop_size and remaining:
            last_parent = remaining[-1]
            last_child = self.mutate(last_parent, mutation_rate)
            new_population.append(last_child)
        
        # Asegurar que la población tiene el tamaño correcto
        while len(new_population) > self.pop_size:
            new_population.pop()
            
        self.population = new_population
        return new_population
    
    def run_evolution(self, generations=50, mutation_rate=0.1, crossover_rate=0.9, 
                    tournament_size=3, elitism=2):
        """
        Ejecuta el ciclo completo de evolución del algoritmo genético.
        Muestra el progreso y aplica una reducción gradual de la tasa de mutación.
        """
        # Inicializar población y variables
        self.initialize_population()
        self.fitness_history = []
        self.best_solution_history = []
        self.best_fitness = float('inf')
        
        print("Iniciando optimización...")
        
        # Evolución a lo largo de las generaciones
        for gen in range(generations):
            # Reducir gradualmente la tasa de mutación
            current_mutation_rate = mutation_rate * (1 - gen / generations * 0.7)
            
            # Evaluar población actual
            fitness_values = self.evaluate_population()
            
            # Imprimir progreso
            if (gen + 1) % max(1, generations // 10) == 0 or gen == 0:
                min_fit = min(fitness_values)
                avg_fit = sum(fitness_values) / len(fitness_values)
                print(f"Generación {gen+1}/{generations}: Mejor Fitness = {min_fit:.4f}, "
                     f"Fitness Promedio = {avg_fit:.4f}")
            
            # Evolucionar a la siguiente generación (excepto en la última)
            if gen < generations - 1:
                self.evolve_population(
                    fitness_values, 
                    mutation_rate=current_mutation_rate,
                    crossover_rate=crossover_rate,
                    tournament_size=tournament_size,
                    elitism=elitism
                )
        
        # Evaluar una última vez para asegurar que tenemos el mejor individuo
        self.evaluate_population()
        
        print("\nOptimización finalizada.")
        print(f"Mejor Fitness encontrado: {self.best_fitness:.4f}")
        
        # Mostrar resultados
        self.display_results()
    
    def display_results(self):
        """Muestra los resultados finales y genera visualizaciones."""
        print("\n📊 RESULTADOS OPTIMIZADOS:")
        print(f"Capacidad Óptima del Aire Acondicionado: {self.best_solution['BTU']:.2f} BTU")
        print(f"Tipo de Aire Acondicionado Recomendado: {self.get_AC_type(self.best_solution['BTU'])}")
        print(f"Potencia de Iluminación Recomendada: {self.best_solution['P_luz']:.2f} W")
        print(f"Nivel Óptimo de Aislamiento Térmico (U): {self.best_solution['U']:.2f}")
        print(f"Cantidad Recomendada de Personas por Aula: {self.best_solution['N_personas']}\n")

        # Simulación de consumo energético antes y después de la optimización
        consumo_antes = self.input_data.carga + self.input_data.lamparas * self.input_data.potencia_lampara
        consumo_despues = (self.best_solution['BTU'] / 1000) + self.best_solution['P_luz'] / 10

        # Cantidad de personas por m²
        if self.input_data.superficie != 0:
            personas_por_m2 = self.best_solution['N_personas'] / self.input_data.superficie
            m2_por_persona = self.input_data.superficie / self.best_solution['N_personas']
        else:
            personas_por_m2 = 0
            m2_por_persona = 0
            
        print(f"Cantidad de personas por m²: {personas_por_m2:.2f}")
        print(f"Espacio por persona: {m2_por_persona:.2f} m²\n")

        print(f"⚡ Consumo Base: {consumo_antes:.2f} kWh")
        print(f"⚡ Consumo Óptimo: {consumo_despues:.2f} kWh")
        print(f"📉 Ahorro Energético: {consumo_antes - consumo_despues:.2f} kWh ({(1 - consumo_despues/consumo_antes) * 100:.1f}%)\n")

        # Generar gráficos
        self.plot_fitness()
        self.plot_comparison(consumo_antes, consumo_despues)
        self.plot_luminosidad()
        self.plot_temperatura()
        self.plot_espacio_persona()

    def get_AC_type(self, BTU):
        """Determina el tipo de aire acondicionado recomendado según el BTU."""
        if BTU < 12000:
            return "Unidad de Ventana (SEER 10-12)"
        elif BTU < 18000:
            return "Mini Split (SEER 14-16)"
        elif BTU < 24000:
            return "Mini Split (SEER 17-20)"
        elif BTU < 36000:
            return "Mini Split Multizona o Sistema Central (SEER 16-18)"
        else:
            return "Sistema Centralizado (SEER 20+)"
    
    def plot_fitness(self):
        """Genera un gráfico mejorado de la evolución del fitness."""
        plt.figure(figsize=(10, 6))
        plt.plot(self.fitness_history, marker='o', linestyle='-', color='b')
        plt.xlabel("Generaciones")
        plt.ylabel("Fitness (Menor es Mejor)")
        plt.title("Evolución de la Función de Fitness")
        plt.grid(True)
        
        # Añadir anotación del mejor valor
        min_fitness = min(self.fitness_history)
        min_gen = self.fitness_history.index(min_fitness)
        plt.annotate(f'Mejor: {min_fitness:.4f}', 
                    xy=(min_gen, min_fitness),
                    xytext=(min_gen + 2, min_fitness * 1.1),
                    arrowprops=dict(facecolor='black', arrowstyle='->'),
                    fontsize=10)
        
        # Mejorar la apariencia del gráfico
        plt.gca().xaxis.set_major_locator(MaxNLocator(integer=True))
        plt.tight_layout()
        plt.show()

    def plot_comparison(self, consumo_antes, consumo_despues):
        """Genera un gráfico de barras comparando el consumo energético."""
        labels = ["Consumo Base", "Consumo Óptimo"]
        valores = [consumo_antes, consumo_despues]
        
        # Calcular ahorro
        ahorro = consumo_antes - consumo_despues
        porcentaje = (ahorro / consumo_antes) * 100 if consumo_antes > 0 else 0
        
        plt.figure(figsize=(8, 6))
        bars = plt.bar(labels, valores, color=['#FF6B6B', '#4ECDC4'])
        
        # Añadir etiquetas con valores
        for bar in bars:
            height = bar.get_height()
            plt.text(bar.get_x() + bar.get_width()/2., height + 0.1,
                    f'{height:.1f} kWh', ha='center', va='bottom')
        
        # Añadir una línea para mostrar el ahorro
        plt.axhline(y=consumo_despues, color='gray', linestyle='--', alpha=0.7)
        
        # Añadir anotación de ahorro
        plt.annotate(f'Ahorro: {ahorro:.1f} kWh ({porcentaje:.1f}%)', 
                    xy=(0, consumo_despues + (ahorro/2)),
                    xytext=(0.5, consumo_despues + (ahorro/2) + 0.5),
                    arrowprops=dict(facecolor='black', arrowstyle='->'),
                    fontsize=10, ha='center')
        
        plt.xlabel("Estado")
        plt.ylabel("Consumo Energético (kWh)")
        plt.title("Comparación de Consumo Energético")
        plt.ylim(0, max(valores) * 1.2)  # Ajustar el límite Y
        plt.tight_layout()
        plt.show()

    def plot_luminosidad(self):
        """Muestra la evolución de la potencia de iluminación recomendada."""
        if not self.best_solution_history:
            return
            
        p_luz_vals = [sol['P_luz'] for sol in self.best_solution_history]
        generaciones = range(len(p_luz_vals))
        
        plt.figure(figsize=(10, 6))
        plt.plot(generaciones, p_luz_vals, marker='o', linestyle='-', color='orange')
        plt.axhline(y=self.best_solution['P_luz'], color='red', linestyle='--', 
                   label=f'Valor óptimo final: {self.best_solution["P_luz"]:.2f} W')
        
        # Iluminación óptima teórica
        P_luz_optimal = (self.input_data.lux * self.input_data.superficie) / self.input_data.eficiencia
        plt.axhline(y=P_luz_optimal, color='green', linestyle=':', 
                   label=f'Valor teórico óptimo: {P_luz_optimal:.2f} W')
        
        plt.title("Evolución de la Potencia de Iluminación")
        plt.xlabel("Generaciones")
        plt.ylabel("Potencia de Iluminación (W)")
        plt.legend()
        plt.grid(True)
        plt.tight_layout()
        plt.show()

    def plot_temperatura(self):
        """Muestra la evolución del coeficiente U (aislamiento térmico)."""
        if not self.best_solution_history:
            return
            
        u_vals = [sol['U'] for sol in self.best_solution_history]
        generaciones = range(len(u_vals))
        
        plt.figure(figsize=(10, 6))
        plt.plot(generaciones, u_vals, marker='o', linestyle='-', color='#5D5DFF')
        plt.axhline(y=self.best_solution['U'], color='red', linestyle='--', 
                   label=f'Valor óptimo final: {self.best_solution["U"]:.2f}')
        
        plt.title("Evolución del Coeficiente de Transmisión Térmica (U)")
        plt.xlabel("Generaciones")
        plt.ylabel("Coeficiente U (menor es mejor)")
        plt.legend()
        plt.grid(True)
        plt.tight_layout()
        plt.show()

    def plot_espacio_persona(self):
        """Muestra la evolución del espacio por persona (m²/persona)."""
        if not self.best_solution_history:
            return
            
        A = self.input_data.superficie
        espacios = []
        generaciones = []
        
        for i, sol in enumerate(self.best_solution_history):
            n = sol['N_personas']
            if n > 0:  # Evitar división por cero
                espacios.append(A / n)
                generaciones.append(i)
        
        plt.figure(figsize=(10, 6))
        plt.plot(generaciones, espacios, marker='o', linestyle='-', color='#66BB6A')
        
        # Añadir valor óptimo final
        final_espacio = A / self.best_solution['N_personas'] if self.best_solution['N_personas'] > 0 else 0
        plt.axhline(y=final_espacio, color='red', linestyle='--', 
                   label=f'Valor óptimo final: {final_espacio:.2f} m²/persona')
        
        # Añadir zonas de confort
        plt.axhspan(1.5, 3.5, alpha=0.2, color='green', label='Zona óptima (1.5-3.5 m²/persona)')
        
        plt.title("Evolución del Espacio por Persona")
        plt.xlabel("Generaciones")
        plt.ylabel("Espacio por Persona (m²/persona)")
        plt.legend()
        plt.grid(True)
        plt.tight_layout()
        plt.show()
        
    def print_population(self):
        """Imprime la población actual y sus valores de fitness."""
        fitness_values = [self.evaluate_individual(ind) for ind in self.population]
        sorted_indices = sorted(range(len(fitness_values)), key=lambda i: fitness_values[i])
        
        print("\n--- POBLACIÓN ACTUAL ---")
        for idx in sorted_indices:
            ind = self.population[idx]
            fit = fitness_values[idx]
            print(f"Individuo {idx+1}: BTU={ind['BTU']:.1f}, P_luz={ind['P_luz']:.1f}, "
                 f"U={ind['U']:.2f}, N_personas={ind['N_personas']} | Fitness: {fit:.4f}")