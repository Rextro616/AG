from OptiluzInput import OptiluzInput
from OptiluzGA import OptiluzGA

datos = OptiluzInput(
    superficie=50,
    ventanas=4,
    coeficiente=1.2,
    temp_ext=30,
    temp_int=22,
    humedad=60,
    carga=5000,
    lux=300,
    tipo_iluminacion="LED",
    eficiencia=100,
    lamparas=10,
    potencia_lampara=20,
    alpha=0.8,
    beta=0.2
)

# Crear el algoritmo genético y ejecutarlo
ga = OptiluzGA(datos, pop_size=20)
ga.run_evolution(generations=50)
