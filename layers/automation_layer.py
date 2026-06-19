# layers/automation_layer.py
import os
import re
from layers.base_layer import BaseLayer
from core.llm import ask_syna
from core.utils import load_file, log_error

class AutomationLayer(BaseLayer):
    """
    Layer 3 - Automation
    Handles multi-step tasks, script creation, and complex workflows.
    Currently a skeleton - returns None to allow fallback until full logic is implemented.
    """

    def __init__(self):
        self.output_dir = os.path.expanduser("~/SynaAI/SynaScripts")
        os.makedirs(self.output_dir, exist_ok=True)
        print("⚙️ AutomationLayer: Initialized.")

    def can_handle(self, user_input: str) -> bool:
        lower = user_input.lower()
        triggers = [
            "depois", "em seguida", "sequência", "roteiro",
            "automatizar", "script", "automação", "passo a passo",
            "primeiro", "segundo", "terceiro", "criar um fluxo",
            "corrigir", "corrija", "arrumar", "arrume", "erro",
            "listar scripts", "mostrar scripts", "meus scripts"
        ]
        if "traceback" in lower:
            return True
        return any(trigger in lower for trigger in triggers)
    
    def handle(self, user_input: str):
        print(f"⚙️ AutomationLayer.handle: Received: '{user_input}'")
        if not self.can_handle(user_input):
            return None
        
        if "traceback" in user_input.lower():
            return self._fix_script(user_input)

        lower = user_input.lower()

        if "script" in user_input.lower() and ("python" in user_input.lower() or ".py" in user_input.lower()) and "corrigir" not in user_input.lower() and "erro" not in user_input.lower():
            return self._create_script(user_input)
        # Placeholder: no real automation yet
        # Future_versions will parse and execute chains of commands.
    
        if any(word in user_input.lower() for word in ["corrigir", "corrija", "arrumar", "arrume", "erro"]):
            return self._fix_script(user_input)

        return None

    def _create_script(self, user_input):
        match = re.search(r'script\s+python\s+de\s+(?:uma?|do|da)\s+(.+)', user_input, re.IGNORECASE)
        if not match:
            return "Não entendi o que o script deve fazer. Pode dar mais detalhes?"
        
        description = match.group(1).strip()
        prompt_code = (
            f"Crie um script Python que funcione como: {description}.\n"
            "Retorne APENAS o código Python puro, sem explicações, sem markdown, sem ```.\n"
            "Inclua um comentário no início com a descrição fornecida."
        )

        code = ask_syna(prompt_code)
        if not code or code.startswith("[Erro"):
            return f"Não consegui gerar o script para '{description}'."
        
        clean_code = re.sub(r'```[Pp]ython|```|`', '', code).strip()
        filename = description.lower().replace(" ", "_") + ".py"
        filepath = os.path.join(self.output_dir, filename)

        try:
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(f"# {description}\n")
                f.write(clean_code)
            return f"Script criado com sucesso: '{filepath}'"
        except Exception as e:
            return f"Erro ao salvar o script: {e}"
        
    def _fix_script(self, user_input):
        match = re.search(r'(?:corrigir|corrija|arrumar|arrume\s+)?(?:o\s+)?(?:script|arquivo\s+)?([\w\-\/\.\sáéíóúâêîôûãõç]+\.py)', user_input, re.IGNORECASE)

        if not match:
            file_match = re.search(r'File\s+"([^"]+\.py)"', user_input)
            if file_match:
                filename = file_match.group(1)
            else:
                return "Não consegui identificar o script a corrigir. Você pode pedir 'listar scripts' para ver os disponíveis."
        else:
            filename = match.group(1).strip()

        if os.path.isabs(filename):
            filepath = filename
        else:
            filepath = os.path.join(self.output_dir, filename)

        if not os.path.exists(filepath):
            return f"O arquivo `{filename}` não foi encontrado em `~/SynaAI/SynaScripts/`."
        
        # Read the contents of the file
        current_code = load_file(filepath)
        if not current_code:
            return f"Não consegui ler o conteúdo do arquivo `{filepath}`."
        
        # Extract the error description
        if match:
            error_start = match.end()
        else:
            tb_match = re.search(r'Traceback', user_input, re.IGNORECASE)
            error_start = tb_match.start() if tb_match else 0

        error_description = user_input[error_start:].strip()
        if not error_description:
            return "Você precisa me dizer qual foi o erro, para eu poder corrigir."

        # Extract the prompt
        fix_prompt = (
            f"O seguinte código Python causou este erro:\n\n"
            f"```python\n{current_code}\n```\n\n"
            f"Erro:\n{error_description}\n\n"
            "Instrução: Corrija o código removendo qualquer uso de atributos ou classes que não existem no módulo customtkinter. "
            "Por exemplo, se o erro mencionar 'module customtkinter has no attribute Entry', troque 'Entry' por 'CTkEntry'. "
            "Retorne APENAS o código Python completo corrigido, sem blocos ```, sem explicações."
        )

        # Request the correction for the LLM
        corrected_code = ask_syna(fix_prompt)
        print("DEBUG _fix_script RAW LLM response:")
        print(repr(corrected_code))
        if not corrected_code or corrected_code.startswith("[Erro"):
            return f"Não consegui gerar a correção para '{filename}'."
        
        # Clean up any remaining traces of markdown
        clean_corrected_code = re.sub(r'```[Pp]ython|```|`', '', corrected_code).strip()

        # Save over the original file
        try:
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(clean_corrected_code)
            return f"Script `{filepath}` corrigido com sucesso! Dê uma olhada no código."
        except Exception as e:
            log_error(f"Erro ao salvar correção do script {filename}: {e}")
            return f"Ocorreu um erro ao salvar o script corrigido: {e}"