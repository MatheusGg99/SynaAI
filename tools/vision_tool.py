# tools/vision_tool.py
from tools.tool_base import BaseTool
from tools.tools import take_screenshot, try_read_image

class ScreenshotTool(BaseTool):
    def can_handle(self, user_input: str) -> bool:
        keywords = ["screenshot", "print da tela", "olha minha tela", "veja minha tela", "o que está na tela"]
        return any(k in user_input.lower() for k in keywords)
    
    def execute(self, user_input: str) -> str:
        return take_screenshot(user_input)

class ImageReadTool(BaseTool):
    def can_handle(self, user_input: str) -> bool:
        import re
        patterns = [
            r'(?:analise|descreva|veja|olhe|leia)\s+(?:a\s+)?(?:imagem|foto|figura)\s+(?:do\s+)?(?:arquivo\s+)?[\'"]?([^\'"]+\.(?:png|jpg|jpeg|gif|bmp|webp))',
            r'(?:imagem|foto|figura)\s+[\'"]?([^\'"]+\.(?:png|jpg|jpeg|gif|bmp|webp))',
        ]
        for pattern in patterns:
            if re.search(pattern, user_input, re.IGNORECASE):
                return True
        return False
    
    def execute(self, user_input: str) -> str:
        return try_read_image(user_input)