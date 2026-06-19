# SynaAI – Local AI Agent with Vector Memory

**Syna** is a modular, personality‑driven AI assistant designed to run entirely on your local machine. It combines a conversational LLM (via KoboldCPP or Groq) with a **persistent vector memory** (ChromaDB + sentence‑transformers) to provide context‑aware, long‑term interactions. Originally built as a development partner, Syna can search the web, read links, manage files, execute system commands, and even see your screen – all while maintaining a unique, sarcastic persona.

## Key Features

- **Vector Memory (RAG)** – Uses `all-MiniLM-L6-v2` embeddings and ChromaDB to store and retrieve relevant facts from past conversations. Injected automatically into the system prompt.
- **Local & API Hybrid** – Works with local GGUF models (KoboldCPP) and falls back to Groq/OpenRouter APIs when needed.
- **Personality Engine** – Dynamic system prompts with multiple modes (Partner, Mentor, Tool, Engineer). No generic "AI assistant" tone – Syna is sarcastic, direct, and uses nicknames.
- **Web Search & Link Reading** – Searches via DuckDuckGo, extracts text from URLs (BeautifulSoup), and summarizes content with full personality.
- **System Automation** – Open apps/folders, create/edit files, take screenshots, analyze images, send desktop notifications.
- **Voice Interface** – Speech‑to‑text (Whisper) and text‑to‑speech (Kokoro) built into the GUI.
- **Clean Architecture** – Layered design (`SystemLayer`, `WebLayer`, `AutomationLayer`) with intent routing and fallback.

## Architecture Overview

```text
User Input → GUI → Router → Layer (system/web/automation) → Tools → LLM → Response
                                 ↑
                           Vector Memory
                           (ChromaDB)

- **Memory Engine (`core/memory_engine.py`)** – Singleton that loads a SentenceTransformer model, creates embeddings, and queries ChromaDB for top‑k relevant documents. Retrieved memories are appended to the system prompt before LLM inference.
- **Context Injection** – At every user message, `ask_syna()` calls `engine.remember_context(query)` and merges results into the prompt. On shutdown, the conversation is automatically scanned for factual statements and indexed back into the vector store.
- **Layers** – Each layer implements `can_handle()` (local keyword/pattern detection) and `handle()` (executes tool). Priority is determined by confidence scores from `router.classify_intent()`.

## Requirements

- Python 3.10+
- KoboldCPP (for local models) or a Groq API key
- System dependencies: `espeak`, `ffmpeg` (for voice), `xprop` (for window context on Linux)

## Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/Syna.git
   cd Syna

2. Create a virtual environment
    python -m venv .venv
    source .venv/bin/activate   # Linux/Mac

3. Install dependencies
    pip install -r requirements.txt

4. Set up environment variables
Copy .env.example to .env and fill in your API keys (Groq, OpenRouter – optional).
    cp .env.example .env

5. Configure system paths
Copy core/constants_example.py to core/constants.py and adjust the paths to match your system (apps, folders). This file is required for the system automation features to work.

6. Run KoboldCPP (optional – for local models)
Download a GGUF model and start the server:
    ./koboldcpp --model model.Q4_K_M.gguf --port 5001

7. Launch Syna
    python core/syna.py

Project Status

This is the core public release – a stripped‑down, sanitized version of a larger personal project. The vector memory system is fully functional, and the architecture is ready to be extended for custom agents (e.g., game design copilot, research assistant, coding mentor).
License

MIT – free to use, modify, and distribute. See LICENSE file.

Built with 💜 by MatheusGG – an independent developer from Spain
