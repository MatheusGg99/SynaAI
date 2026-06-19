# config.py
# Carrega configurações do ambiente, paths globais e modelos de IA.

import os
import sys
from dotenv import load_dotenv
from core.utils import log_error

def _get_project_root():
    """Returns the absolute path to the project root (where this file is located: core/config.py)"""
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

PROJECT_ROOT = _get_project_root()

# Carrega variáveis do .env
load_dotenv(os.path.join(PROJECT_ROOT, ".env"))

# Chaves de API
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

# ------------------------------------------------------------
# CONFIGURAÇÃO DE MODELOS
# ------------------------------------------------------------

# Modelo principal (local)
PRIMARY_MODEL = "aya-expanse-8b-Q4_K_M" 

# Modelo para ferramentas que exigem API (visão, comandos complexos, etc.)
TOOL_MODEL = "meta-llama/llama-4-scout-17b-16e-instruct"

# Modelos de fallback (APIs gratuitas)
FALLBACK_MODELS = [
    {
        "model": "aya-expanse-8b-Q4_K_M",       
        "provider": "kobold",              
    },
    {
        "model": "llama-3.1-8b-instant",
        "provider": "groq",
    },
]

if not GROQ_API_KEY:
    log_error("GROQ_API_KEY não definida no .env")

# Modelo legado (mantido para compatibilidade com código antigo)
MODEL = PRIMARY_MODEL

# ------------------------------------------------------------
# DIRETÓRIOS E ARQUIVOS
# ------------------------------------------------------------
SYSTEM_PROMPT_FILE = os.path.join(PROJECT_ROOT, "system_prompt.md")
MEMORY_FILE = os.path.join(PROJECT_ROOT, "memory", "memory.md")
PERSONALITY_FILE = os.path.join(PROJECT_ROOT, "memory", "personality.md")
SYSTEM_PROMPT_LITE_FILE = os.path.join(PROJECT_ROOT, "system_prompt_lite.md")

# Loga se algo crítico falhou
if not GROQ_API_KEY:
    log_error("GROQ_API_KEY não definida no .env")
if not OPENROUTER_API_KEY:
    log_error("OPENROUTER_API_KEY não definida no .env")
