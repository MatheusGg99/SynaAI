from groq import Groq
from openai import OpenAI
from core.config import GROQ_API_KEY, OPENROUTER_API_KEY

groq_client = Groq(api_key=GROQ_API_KEY)

openrouter_client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=OPENROUTER_API_KEY,
    default_headers={"HTTP-Referer": "http://localhost", "X-Title": "Syna"}
)

ollama_client = OpenAI(
    base_url='http://localhost:11434/v1',
    api_key='ollama'
)

kobold_client = OpenAI(
    base_url='http://localhost:5001/v1',
    api_key='dummy'
)
