class OptiluzInput:
    """
    Clase mejorada para almacenar y validar los datos de entrada del sistema OptiLuz.
    Incluye métodos para verificar la coherencia de los datos y obtener sugerencias
    basadas en los estándares de confort y eficiencia energética.
    """
    def __init__(self, superficie, ventanas, coeficiente, temp_ext, temp_int, humedad,
                 carga, lux, tipo_iluminacion, eficiencia, lamparas, potencia_lampara,
                 alpha, beta):
        # Validar y almacenar los datos de entrada
        self.superficie = max(1.0, float(superficie))  # m²
        self.ventanas = max(0, int(ventanas))
        self.coeficiente = max(0.1, float(coeficiente))
        self.temp_ext = float(temp_ext)
        self.temp_int = float(temp_int)
        self.humedad = max(0, min(100, float(humedad)))  # %
        self.carga = max(0, float(carga))  # W
        self.lux = max(50, float(lux))  # lux
        
        # Validar tipo de iluminación
        tipos_validos = ["LED", "Fluorescente", "Incandescente"]
        if tipo_iluminacion in tipos_validos:
            self.tipo_iluminacion = tipo_iluminacion
        else:
            self.tipo_iluminacion = "LED"  # Valor por defecto
        
        # Asignar eficiencia según el tipo si no se proporciona
        if eficiencia <= 0:
            self.eficiencia = self._eficiencia_por_tipo(self.tipo_iluminacion)
        else:
            self.eficiencia = float(eficiencia)  # lm/W
        
        self.lamparas = max(1, int(lamparas))
        self.potencia_lampara = max(1, float(potencia_lampara))  # W
        
        # Factores de ponderación (deben sumar aproximadamente 1)
        alpha = float(alpha)
        beta = float(beta)
        sum_factors = alpha + beta
        
        if sum_factors > 0:
            # Normalizar para que sumen 1
            self.alpha = alpha / sum_factors
            self.beta = beta / sum_factors
        else:
            # Valores por defecto si los proporcionados no son válidos
            self.alpha = 0.7
            self.beta = 0.3
        
        # Calcular y almacenar valores derivados útiles
        self._calculate_derived_values()
    
    def _eficiencia_por_tipo(self, tipo):
        """Devuelve la eficiencia lumínica típica según el tipo de iluminación."""
        eficiencia_tipica = {
            "LED": 100,  # lm/W
            "Fluorescente": 60,  # lm/W
            "Incandescente": 15  # lm/W
        }
        return eficiencia_tipica.get(tipo, 80)
    
    def _calculate_derived_values(self):
        """Calcula valores derivados útiles para análisis y recomendaciones."""
        # Relación de aspecto de las ventanas con la superficie
        self.relacion_ventanas = (self.ventanas * 1.5) / self.superficie if self.superficie > 0 else 0
        
        # Diferencia de temperatura
        self.delta_temp = abs(self.temp_ext - self.temp_int)
        
        # Potencia instalada por m²
        self.potencia_instalada_m2 = (self.lamparas * self.potencia_lampara) / self.superficie if self.superficie > 0 else 0
        
        # Potencia teórica para la iluminación requerida
        self.potencia_teorica = (self.lux * self.superficie) / self.eficiencia if self.eficiencia > 0 else 0
        
        # Eficiencia de la instalación actual
        self.eficiencia_instalacion = self.potencia_teorica / (self.lamparas * self.potencia_lampara) if (self.lamparas * self.potencia_lampara) > 0 else 0
    
    def get_recommendations(self):
        """Genera recomendaciones básicas basadas en los datos de entrada."""
        recommendations = []
        
        # Recomendaciones de iluminación
        if self.eficiencia_instalacion < 0.7:
            recommendations.append("La iluminación actual es ineficiente. Considere actualizar a tecnología LED.")
        
        if self.tipo_iluminacion == "Incandescente":
            recommendations.append("Las lámparas incandescentes son muy ineficientes. Se recomienda cambiar a LED.")
        
        # Recomendaciones de ventanas y aislamiento
        if self.relacion_ventanas > 0.4:
            recommendations.append("La proporción de ventanas es alta. Considere mejorar el aislamiento térmico.")
        
        if self.delta_temp > 10 and self.coeficiente > 1.5:
            recommendations.append("La diferencia de temperatura es alta y el aislamiento es deficiente. Se recomienda mejorar el aislamiento.")
        
        # Recomendaciones de carga térmica
        carga_por_m2 = self.carga / self.superficie if self.superficie > 0 else 0
        if carga_por_m2 > 100:
            recommendations.append("La carga térmica por equipos es alta. Considere usar equipos más eficientes.")
        
        return recommendations
    
    def __str__(self):
        """Devuelve una representación en texto de los datos de entrada."""
        return (f"--- DATOS DE ENTRADA DEL SISTEMA ---\n"
                f"Características del Aula:\n"
                f"  Superficie: {self.superficie:.2f} m²\n"
                f"  Ventanas: {self.ventanas}\n"
                f"  Coeficiente de Transmisión Térmica: {self.coeficiente:.2f}\n\n"
                
                f"Factores Térmicos:\n"
                f"  Temperatura Exterior: {self.temp_ext:.1f} °C\n"
                f"  Temperatura Interior Deseada: {self.temp_int:.1f} °C\n"
                f"  Diferencia de Temperatura: {self.delta_temp:.1f} °C\n"
                f"  Humedad Relativa: {self.humedad:.1f} %\n"
                f"  Carga Térmica (equipos): {self.carga:.2f} W\n\n"
                
                f"Factores de Iluminación:\n"
                f"  Nivel de Iluminación Requerido: {self.lux:.1f} lux\n"
                f"  Tipo de Iluminación: {self.tipo_iluminacion}\n"
                f"  Eficiencia Lumínica: {self.eficiencia:.1f} lm/W\n"
                f"  Lámparas Instaladas: {self.lamparas}\n"
                f"  Potencia de Cada Lámpara: {self.potencia_lampara:.1f} W\n"
                f"  Potencia Total Instalada: {self.lamparas * self.potencia_lampara:.1f} W\n"
                f"  Potencia Teórica Necesaria: {self.potencia_teorica:.1f} W\n\n"
                
                f"Factores de Ponderación:\n"
                f"  α (consumo energético): {self.alpha:.2f}\n"
                f"  β (confort): {self.beta:.2f}")
    
    def to_dict(self):
        """Devuelve un diccionario con todos los datos para guardar o exportar."""
        return {
            'superficie': self.superficie,
            'ventanas': self.ventanas,
            'coeficiente': self.coeficiente,
            'temp_ext': self.temp_ext,
            'temp_int': self.temp_int,
            'humedad': self.humedad,
            'carga': self.carga,
            'lux': self.lux,
            'tipo_iluminacion': self.tipo_iluminacion,
            'eficiencia': self.eficiencia,
            'lamparas': self.lamparas,
            'potencia_lampara': self.potencia_lampara,
            'alpha': self.alpha,
            'beta': self.beta
        }