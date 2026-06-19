# tools/file_tool.py
from tools.tool_base import BaseTool
from tools.tools import try_read_file

class FileReadTool(BaseTool):
    def can_handle(self, user_input: str) -> bool:
        import re
        patterns = [
            r'l[eê]ia?\s+(?:o\s+)?arquivo\s+(\S+)',
            r'abra?\s+(?:o\s+)?arquivo\s+(\S+)',
            r'analise?\s+(?:o\s+)?arquivo\s+(\S+)',
            r'veja?\s+(?:o\s+)?arquivo\s+(\S+)',
            r'leia\s+(\S+\.(?:gd|py|txt|md|json|cfg|tscn|tres|import|docx|pdf|xlsx))',
        ]
        for pattern in patterns:
            if re.search(pattern, user_input, re.IGNORECASE):
                return True
        return False
    
    def execute(self, user_input: str) -> str:
        return try_read_file(user_input)