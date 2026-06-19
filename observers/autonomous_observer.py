# observers/autonomous_observer.py
import time
import threading
from datetime import datetime
from tools.tools import send_desktop_notification
from core.utils import log_error, get_last_external_context
from context_tracker import get_idle_time_minutes, get_focus_time_minutes

# Estado para evitar notificações repetitivas
_last_focus_notification_time = 0
_last_absence_notification_time = 0

def should_speak():
    """
    Avalia regras determinísticas para decidir se deve enviar uma notificação proativa.
    Retorna uma mensagem no estilo da Syna ou None.
    """
    try:
        ctx = get_last_external_context()
        app = ctx.get('app', 'Sistema')
        focus_min = get_focus_time_minutes()
        idle_min = get_idle_time_minutes()
        current_hour = datetime.now().hour
        now = time.time()

        # Regra 1: Madrugada (00h - 05h) com foco prolongado
        if 0 <= current_hour < 5 and focus_min > 60:
            if now - _last_focus_notification_time < 14400:  # No máximo a cada 4 horas
                return None
            _last_focus_notification_time = now
            return f"Já é tarde e você está focado no {app} há {focus_min} minutos. A insônia é romântica, mas a produtividade de amanhã também importa. 😴"

        # Regra 2: Foco intenso (>90 min) em aplicativos produtivos
        productive_apps = ['godot', 'code', 'terminal', 'gedit', 'sublime', 'vim', 'studio']
        if any(p in app.lower() for p in productive_apps) and focus_min > 90:
            if now - _last_focus_notification_time < 7200:  # No máximo a cada 2 horas
                return None
            _last_focus_notification_time = now
            return f"Duas horas no {app}, hein? Salva o progresso e estica as pernas, Demandor. 💜"

        # Regra 3: Longa ausência (>60 min sem interação com a Syna)
        if idle_min > 60:
            if now - _last_absence_notification_time < 7200:
                return None
            _last_absence_notification_time = now
            return f"Faz mais de uma hora que não nos falamos. Está tudo bem? Aparece, saudades. 💬"

    except Exception as e:
        log_error(f"Erro ao avaliar regras do observador: {e}")
    return None

def autonomous_monitor(interval_minutes=15):
    """Thread que verifica periodicamente se deve falar."""
    while True:
        time.sleep(interval_minutes * 60)
        try:
            message = should_speak()
            if message:
                base_time = 3000
                char_time = min(len(message) * 50, 12000)
                duration = base_time + char_time
                send_desktop_notification("Syna", message, duration_ms=duration)

                from core.llm import conversation_history
                conversation_history.append({"role": "assistant", "content": f"[Notificação proativa] {message}"})
        except Exception as e:
            log_error(f"Erro no loop do observador: {e}")