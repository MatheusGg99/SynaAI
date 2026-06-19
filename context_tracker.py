import time
import re
from datetime import datetime
from core.utils import get_last_external_context

# Estado interno
current_app = "System"
current_title = "Desktop"
focus_start_time = time.time()
last_syna_interaction = time.time()
current_project_file = None

def update_context():
    """Atualiza as métricas de contexto. Deve ser chamada periodicamente."""
    global current_app, current_title, focus_start_time, current_project_file
    
    ctx = get_last_external_context()
    app = ctx['app']
    title = ctx['title']

    # Se o app mudou, reseta o tempo de foco
    if app != current_app:
        current_app = app
        current_title = title
        focus_start_time = time.time()

    # Extrai informações específicas
    if 'godot' in app.lower():
        # Exemplo: "Godot Engine - MeuJogo - player.gd"
        match = re.search(r'Godot Engine - (.*?) - (.*)', title)
        if match:
            current_project_file = match.group(2)
    elif any(editor in app.lower() for editor in ['code', 'gedit', 'sublime', 'vim']):
        # Exemplo: "syna.py - Visual Studio Code"
        match = re.search(r'(.+\.(?:py|gd|txt|md|json)) -', title)
        if match:
            current_project_file = match.group(1)

def get_context_summary():
    """Retorna um resumo textual do contexto atual para a IA."""
    ctx = get_last_external_context()
    focus_minutes = int((time.time() - focus_start_time) / 60)
    syna_idle_minutes = int((time.time() - last_syna_interaction) / 60)
    
    summary = f"App: {ctx['app']} | Título: {ctx['title']} | Foco: {focus_minutes}min | Syna inativa: {syna_idle_minutes}min"
    if current_project_file:
        summary += f" | Arquivo: {current_project_file}"
    return summary

def mark_syna_interaction():
    """Chamado sempre que o usuário envia uma mensagem."""
    global last_syna_interaction
    last_syna_interaction = time.time()

def get_idle_time_minutes():
    """Minutos desde a última interação com a Syna."""
    return int((time.time() - last_syna_interaction) / 60)

def get_focus_time_minutes():
    """Minutos de foco contínuo no app atual."""
    return int((time.time() - focus_start_time) / 60)