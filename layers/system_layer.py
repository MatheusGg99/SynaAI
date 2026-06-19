from layers.base_layer import BaseLayer
from tools.system_tool import SystemCommandTool
from tools.file_tool import FileReadTool

# Outras ferramentas relevantes a sere importadas futuramente
# Exemplo: VisionTool, SreenshotTool, etc.

class SystemLayer(BaseLayer):
    def __init__(self):
        print("🔧 SystemLayer: Inicializando...")
        self.system_tool = SystemCommandTool()
        self.file_tool = FileReadTool()
        print("🔧 SystemLayer: Ferramentas carregadas.")

    def handle(self, user_input: str):
        print(f"🔧 SystemLayer.handle: Recebido: '{user_input}'")
        
        # Verifica se a ferramenta de sistema consegue lidar
        if self.system_tool.can_handle(user_input):
            print("🔧 SystemLayer: system_tool.can_handle retornou True")
            try:
                print("🔧 SystemLayer: Chamando system_tool.execute...")
                result = self.system_tool.execute(user_input)
                print(f"🔧 SystemLayer: execute retornou: {result[:100] if result else 'None'}")
                return result
            except Exception as e:
                print(f"❌ SystemLayer: Erro no system_tool: {e}")
                return f"Erro ao executar comando de sistema: {e}"
        else:
            print("🔧 SystemLayer: system_tool.can_handle retornou False")
        
        # Tenta ferramenta de arquivos
        if self.file_tool.can_handle(user_input):
            print("🔧 SystemLayer: file_tool.can_handle retornou True")
            try:
                result = self.file_tool.execute(user_input)
                print(f"🔧 SystemLayer: file_tool.execute retornou: {result[:100] if result else 'None'}")
                return result
            except Exception as e:
                print(f"❌ SystemLayer: Erro no file_tool: {e}")
                return f"Erro ao manipular arquivo: {e}"
        else:
            print("🔧 SystemLayer: file_tool.can_handle retornou False")
        
        print("🔧 SystemLayer: Nenhuma ferramenta aplicável, retornando None")
        return None