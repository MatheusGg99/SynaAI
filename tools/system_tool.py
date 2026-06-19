from tools.tool_base import BaseTool
from tools.tools import handle_system_command

class SystemCommandTool(BaseTool):
    def can_handle(self, user_input: str) -> bool:
        lower = user_input.lower().strip()

        # 1. Se for uma pergunta explícita, NÃO é comando
        if lower.endswith('?') or lower.startswith(('quem', 'qual', 'quando', 'onde', 'como', 'por que', 'será', 'você')):
            return False
        
        # Gatilhos explícitos para comandos sem verbo
        explicit_triggers = [
            "status do sistema", "saúde do sistema", "diagnóstico do sistema",
            "status", "saúde", "diagnóstico"
        ]
        for trigger in explicit_triggers:
            if trigger in lower:
                return True
        
        # 2. Lista de verbos de comando (imperativo ou ação direta)
        command_verbs = [
            "abre", "abra", "abrir",
            "executa", "execute", "executar",
            "roda", "rode", "rodar",
            "inicia", "inicie", "iniciar",
            "lança", "lance", "lançar",
            "mostra", "mostre", "mostrar",
            "abre o", "abra o", "abrir o"
        ]
        
        # 3. Se contiver um verbo de comando, É comando
        if any(verb in lower for verb in command_verbs):
            return True
        
        # 4. Lista de apps/pastas que podem ser alvo de comandos
        system_targets = [
            "terminal", "godot", "firefox", "spotify", "tlauncher",
            "documentos", "downloads", "desktop", "área de trabalho",
            "imagens", "músicas", "vídeos", "pasta", "arquivo"
        ]
        
        # 5. Se menciona um alvo mas NÃO tem verbo de comando, NÃO é comando
        # (ex: "você abriu o firefox?" já foi filtrado pelo '?', mas este é um fallback)
        if any(target in lower for target in system_targets):
            # Só considera comando se tiver palavra de ação
            action_words = ["abrir", "executar", "rodar", "iniciar", "lançar", "mostrar", "criar", "deletar", "mover"]
            return any(action in lower for action in action_words)
        
        return False
    
    def execute(self, user_input: str) -> str:
        reply = handle_system_command(user_input)
        if reply is None:
            return "Não entendi o comando de sistema."
        return reply