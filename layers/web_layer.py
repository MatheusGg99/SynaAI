"""
Web Layer - handles web search requests and URL reading using local detection.
"""

import re
from layers.base_layer import BaseLayer
from tools.tools import handle_web_search, handle_url

class WebLayer(BaseLayer):
    """
    Layer responsible for processing web search commands.
    Uses fast local detection to decide whether to handle the input,
    the calls the existing search pipeline.
    """

    def __init__(self):
        print("WebLayer: Initialized.")

    def can_handle(self, user_input: str) -> bool:
        """
        Quick local check to determine if the input is likely a web search or a URL.
        Returns True if any trigger word or a URL pattern is found.
        """
        lower = user_input.lower()
        triggers = [
            "pesquisar", "pesquise", "pesquisa", "procure", "buscar", "busque",
            "google", "internet", "o que é", "quem é", "defina", "significado de",
            "notícias sobre", "notícia de"
        ]
        url_pattern = re.compile(r'https?://\S+', re.IGNORECASE)
        is_url = bool(url_pattern.search(user_input))

        return is_url or any(trigger in lower for trigger in triggers)
    
    def handle(self, user_input: str):
        """
        Attempts to process the input as a web search or a URL.
        Returns the search result if successful, or None if it cannot handle.
        """
        print(f"WebLayer.handle: Received: '{user_input}'")

        if not self.can_handle(user_input):
            print("WebLayer: can_handle returned False, skipping.")
            return None
        
        url_pattern = re.compile(r'https?://\S+', re.IGNORECASE)
        url_match = url_pattern.search(user_input)

        if url_match:
            print("WebLayer: Detected URL, calling handle_url...")
            try:
                result = handle_url(user_input)
                if result:
                    print(f"WebLayer: URL processed, result length: {len(result)} chars,")
                else:
                    print("WebLayer: handle_url returned None.")
                return result
            except Exception as e:
                print(f"WebLayer: Error during handle_url: {e}")
                return f"Error in reading link: {e}"
        
        print("WebLayer: Calling handle_web_search...")
        try:
            result = handle_web_search(user_input)
            if result:
                print(f"WebLayer: Got result ({len(result)} chars).")
            else:
                print("WebLayer: handle_web_search returned None.")
            return result
        except Exception as e:
            print(f"WebLayer: Error during web search: {e}")
            return f"Error in to do web research: {e}"
        