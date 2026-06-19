# utils.py
# Funções utilitárias gerais: logging, manipulação de arquivos, texto.

import os
import traceback
from datetime import datetime

# ----- Sistema de Log e Output -----
_syna_app_instance = None

def set_syna_app_instance(app):
    """Define a instância da interface para permitir logs no Output."""
    global _syna_app_instance
    _syna_app_instance = app

def log_error(message):
    """Grava erro no arquivo de log com timestamp, sem incomodar o usuário."""
    log_path = os.path.expanduser("~/syna/error.log")
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    try:
        with open(log_path, "a", encoding="utf-8") as f:
            f.write(f"[{timestamp}] {message}\n")
            if isinstance(message, Exception):
                traceback.print_exc(file=f)
            f.write("\n")
    except Exception:
        pass  # Se não conseguir logar, paciência.

def log_token_usage(prompt_tokens, completion_tokens, total_tokens):
    global _syna_app_instance
    if _syna_app_instance:
        _syna_app_instance.log_status(f"📊 Tokens: prompt={prompt_tokens} | resposta={completion_tokens} | total={total_tokens}")
    else:
        # Fallback: escreve no error.log para depuração
        log_error(f"📊 Tokens (sem GUI): prompt={prompt_tokens} | resposta={completion_tokens} | total={total_tokens}")

# ----- Manipulação de Arquivos -----
def load_file(path):
    """Lê o conteúdo de um arquivo de texto e retorna como string."""
    try:
        with open(path, "r", encoding="utf-8") as f:
            return f.read()
    except Exception:
        return ""

def save_memory(content, memory_file):
    """Anexa conteúdo ao arquivo de memória (usado em fallbacks)."""
    try:
        with open(memory_file, "a", encoding="utf-8") as f:
            f.write(content)
    except Exception:
        pass

# ----- Processamento de Texto -----
def truncate_text(text, max_chars=1500):
    """Limita o texto a max_chars caracteres, quebrando em palavra."""
    if len(text) <= max_chars:
        return text
    return text[:max_chars].rsplit(' ', 1)[0] + "...\n[memória truncada]"

# ----- Contexto da Janela Ativa (compartilhado) -----
_last_external_context = {"title": "Desktop", "app": "System"}

def get_last_external_context():
    """Retorna o contexto da última janela externa conhecida."""
    return _last_external_context.copy()

def set_last_external_context(title, app):
    """Atualiza o contexto da janela externa."""
    global _last_external_context
    _last_external_context = {"title": title, "app": app}
