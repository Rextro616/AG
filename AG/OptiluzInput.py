class OptiluzInput:
    """
    Clase para almacenar los datos de entrada del sistema.
    """
    def __init__(self, superficie, ventanas, coeficiente, temp_ext, temp_int, humedad,
                 carga, lux, tipo_iluminacion, eficiencia, lamparas, potencia_lampara,
                 alpha, beta):
        self.superficie = superficie
        self.ventanas = ventanas
        self.coeficiente = coeficiente
        self.temp_ext = temp_ext
        self.temp_int = temp_int
        self.humedad = humedad
        self.carga = carga
        self.lux = lux
        self.tipo_iluminacion = tipo_iluminacion
        self.eficiencia = eficiencia
        self.lamparas = lamparas
        self.potencia_lampara = potencia_lampara
        self.alpha = alpha
        self.beta = beta

    def __str__(self):
        return (f"Superficie: {self.superficie} m²\n"
                f"Ventanas: {self.ventanas}\n"
                f"Coeficiente de Transmisión Térmica: {self.coeficiente}\n"
                f"Temperatura Exterior: {self.temp_ext} °C\n"
                f"Temperatura Interior Deseada: {self.temp_int} °C\n"
                f"Humedad Relativa: {self.humedad} %\n"
                f"Carga Térmica (equipos): {self.carga} W\n"
                f"Nivel de Iluminación (lux): {self.lux}\n"
                f"Tipo de Iluminación: {self.tipo_iluminacion}\n"
                f"Eficiencia Lumínica: {self.eficiencia} lm/W\n"
                f"Lámparas Instaladas: {self.lamparas}\n"
                f"Potencia de Cada Lámpara: {self.potencia_lampara} W\n"
                f"Factor de Ponderación α: {self.alpha}\n"
                f"Factor de Ponderación β: {self.beta}")
