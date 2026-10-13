
import os
from dotenv import load_dotenv
from openai import OpenAI

# Cargar las variables del archivo .env
load_dotenv()

# Obtener la API Key y el modelo
api_key = os.getenv("OPENAI_API_KEY")
modelo = os.getenv("OPENAI_MODEL")

# Verificar que las variables estén configuradas
if not api_key or api_key == "TU_API_KEY":
    raise ValueError("Configura tu OPENAI_API_KEY en el archivo .env")

if not modelo:
    raise ValueError("Configura OPENAI_MODEL en el archivo .env")

# Crear el cliente de OpenAI
client = OpenAI(api_key=api_key)

# Enviar una pregunta sin utilizar herramientas
respuesta = client.responses.create(
    model=modelo,
    input="¿Qué es un agente de inteligencia artificial? Explícalo brevemente."
)

# Mostrar la respuesta
print("Respuesta de OpenAI:")
print(respuesta.output_text)
