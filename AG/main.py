"""
OptiLuz: Sistema de Optimización Energética para Instituciones Educativas
---------------------------------------------------------------------------
Este programa utiliza algoritmos genéticos para optimizar el consumo energético
en aulas educativas, considerando el aire acondicionado, iluminación, aislamiento
térmico y cantidad de personas recomendada.

Desarrollado como parte del proyecto OptiLuz.
"""

import os
import sys
import traceback
import logging
from datetime import datetime
from OptiluzGUI import OptiluzGUI

# Configurar logging
def setup_logging():
    """Configura el sistema de logging para la aplicación."""
    log_dir = "logs"
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
        
    log_file = os.path.join(log_dir, f"optiluz_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log")
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler(sys.stdout)
        ]
    )
    
    return logging.getLogger("OptiLuz")

def show_splash_screen():
    """Muestra información básica sobre la aplicación en la consola."""
    print("""
    ╔═══════════════════════════════════════════════════╗
    ║                     OptiLuz                        ║
    ║  Sistema de Optimización Energética para Aulas     ║
    ╚═══════════════════════════════════════════════════╝
    
    Iniciando aplicación...
    """)

def main():
    """Función principal que inicia la aplicación."""
    show_splash_screen()
    logger = setup_logging()
    
    try:
        logger.info("Iniciando OptiLuz")
        app = OptiluzGUI()
        logger.info("Interfaz gráfica iniciada")
        app.mainloop()
        logger.info("Aplicación cerrada correctamente")
    
    except Exception as e:
        logger.error(f"Error no manejado: {e}")
        logger.error(traceback.format_exc())
        
        # Intentar mostrar un mensaje de error
        try:
            import tkinter as tk
            from tkinter import messagebox
            
            root = tk.Tk()
            root.withdraw()
            messagebox.showerror(
                "Error Fatal", 
                f"Ha ocurrido un error inesperado:\n\n{str(e)}\n\nConsulte el archivo de log para más detalles."
            )
            root.destroy()
        except:
            print(f"ERROR FATAL: {e}")
            print("Consulte los logs para más detalles.")
        
        sys.exit(1)

if __name__ == "__main__":
    main()