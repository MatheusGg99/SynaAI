# tools/web_tool.py
from tools.tool_base import BaseTool
from tools.tools import handle_web_search

class WebSearchTool(BaseTool):
    def can_handle(self, user_input: str) -> bool:
        triggers = ["pesquise", "pesquisa", "procure por", "busque por", "procura na internet",
                    "busca na web", "pesquisar", "buscar", "procure", "busque"]
        lower = user_input.lower()
        return any(trigger in lower for trigger in triggers)
    
    def execute(self, user_input: str) -> str:
        reply = handle_web_search(user_input)
        return reply if reply else "Não consegui realizar a pesquisa."