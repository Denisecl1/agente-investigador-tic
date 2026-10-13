
import os
from dotenv import load_dotenv

# Cargar las variables del archivo .env
load_dotenv()

# Obtener la API Key de forma segura
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Obtener el modelo configurado
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-6-luna")

# Verificar que la API Key esté disponible
if not OPENAI_API_KEY:
    raise ValueError(
        "No se encontró OPENAI_API_KEY en el archivo .env"
    )
