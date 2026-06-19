# ------------------- CHANGELOG -------------------

## v1.2.0 — Perception & Reading (2026-06-17)

### ✅ Local Vector Memory (RAG)
- **Embedding engine:** Integrated `all-MiniLM-L6-v2` via Sentence Transformers for local semantic vector generation.
- **Vector database:** Implemented ChromaDB as persistent storage for embeddings and metadata (`~/SynaAI/memory/chroma_db`).
- **Automatic injection:** On every user message, Syna silently queries the vector DB and adds relevant memories to the system prompt (`llm.py`).
- **Implicit learning:** On GUI close (`on_close`), the local model extracts factual sentences from the conversation and indexes them into vector memory.
- **Semantic retrieval:** Cosine similarity search with relevance filter (`max_distance`) to avoid context pollution.
- **Clean architecture:** Decoupled `core/memory_engine.py` module with Singleton pattern to avoid multiple embedding model loads.
- **Safe fallback:** ChromaDB failures are logged silently and do not interrupt the conversation.

### ✅ URL Reading (Links)
- **Native detection:** `WebLayer` now recognizes standalone URLs (no trigger words needed) using regex `https?://\S+`.
- **Integration with existing tool:** Calls `handle_url` in `tools.py`, which fetches page text with `requests` + `BeautifulSoup`, injects it into history, and generates a summary.
- **Personality applied to summary:** The summary is now generated using Syna's full system prompt (cached), ensuring sarcastic tone, nicknames ("Demandor", etc.), and prohibition of generic phrases like “Hello! I'm here to help...”.
- **Adjusted parameters:** Temperature increased to `0.7` (was `0.3`) and `max_tokens` to `500` (was `400`) for more creative, personality-aligned responses.
- **Fixed text removal:** `handle_url` no longer appends the footer “💬 What do you want to know about this?” – Syna decides how to end the response.
- **User‑friendly error handling:** On extraction failure, Syna replies with a message containing “Demandor” and guidance to check the link.

---

## v1.1.1 — Hotfix
- Implemented temporary session diary (`session_log.md`) to prevent memory corruption.
- Fixed Layers: `SystemLayer` hang, `AutomationLayer` regex and match.end, `WebLayer` ddgs.

### Architecture Cleanup
- Removed obsolete tools from fallback in `gui.py` (SystemCommandTool, WebSearchTool, ScreenshotTool, etc.).
- Simplified message flow: Router → Layers → Fallback (direct LLM conversation).
- Removed dead code in `llm.py`: `build_system_prompt()`, `ask_syna_stream()`, unused `client` variable.
- Removed OpenRouter dependency: client, imports, entries in `FALLBACK_MODELS` and `PROVIDER_TO_CLIENT`.
- Fixed import bug for `groq_client` in `tools.py` and `gui.py`.
- Added 5s timeout to Groq API call in `tools.py` (`detect_command`).
- Removed unnecessary injection of system health report into `conversation_history`.
- Fixed memory truncation in "balanced" profile of `build_dynamic_prompt`.
- Added automatic truncation of conversation history (max 40 messages).

- Improved Autonomous Observer: removed LLM dependency for notification decisions; implemented deterministic rules based on real context (active app, focus time, hour, no interaction). Added spam control and longer check interval (15 minutes). Notifications are now fast, relevant, and GPU‑free.
- Discarded reminder scheduler after usage evaluation: the system was never used or integrated into the main flow. Removed files (`core/scheduler.py`, `tools/reminder_tool.py`) and references in `core/syna.py` (import and thread). Functionality noted in backlog for future implementation as operational memory.

---

## v1.1.0 — Voice & Layered Architecture (2026-05-06)
### Layered Architecture
- Created central router (`core/router.py`) with regex‑based classification (System, Web, Automation, Conversation).
- Implemented **System Layer** (`layers/system_layer.py`): open apps, folders, run commands.
- Implemented **Web Layer** (`layers/web_layer.py`): search via DuckDuckGo with local fallback.
- Implemented **Automation Layer** (`layers/automation_layer.py`): automatic Python script creation and debugging.
- Created abstract base class (`layers/base_layer.py`) for layer standardization.
- Integrated layers into main GUI flow (`gui.py`), with fallback to Conversation (LLM).

### Speech‑to‑Text Implementation
- Created voice module (`listen` + `speak`).
- Added voice recording button to GUI.
- Added `start_voice_mode` and `voice_loop` methods.
- Installed dependencies in venv.
- Downloaded Piper voice.

### System Improvements
- Migrated to **Aya Expanse 8B** (Q4_K_M) with CUDA acceleration.
- Startup script (`start_all.sh`) with optimized parameters for NVIDIA RTX 3050.
- Created session diary (`memory/session_log.md`) to replace automatic memory updates.
- Added `listar scripts` command in Automation Layer.
- Updated filename extraction regex to accept accents and absolute paths.

### Fixes
- Fixed router bug preventing classification of search commands.
- Fixed broken regex in `_fix_script` (AutomationLayer).
- Fixed LLM response validation that blocked scripts containing the word "Error".
- Fixed `error.log` path (pointed to `~/syna/` instead of `~/SynaAI/`).

### Technical Dependencies
- **Main model:** `aya-expanse-8b-Q4_K_M.gguf` (KoboldCPP, localhost:5001, CUDA).
- **Voice:** Kokoro TTS + Whisper `base`.
- **GUI:** CustomTkinter (dark theme, purple #534AB7).
- **Environment:** Python 3.12, Linux Mint 22.3 Cinnamon.

---

## v1.0.1 — Stability Hotfix (2026-04-17)
### Fixed
- `autonomous_observer` error (`cannot access local variable 'message'`) fixed with safe initialization and debug logs.
- System commands executed twice (BUG-004) – removed duplicate code in `send_message`.
- Updated fallback model list to use only functional APIs.

### Changed
- **Default local engine switched from Ollama to KoboldCPP** (faster generation).
- Integrated `kobold_client` into `llm.py` and `autonomous_observer.py`.

### Added
- Support for sampler parameters in KoboldCPP to prevent token loops.

---

## v1.0.0 — Initial Release
### Architecture
- Full modular structure (`core/`, `tools/`, `observers/`, `memory/`).
- Unified clients (`clients.py`) for Groq, OpenRouter, and Ollama.
- Strategy pattern for tools (partial – SystemCommandTool, ScreenshotTool, ImageReadTool, FileReadTool, WebSearchTool, ReminderTool).
- Automatic fallback between local models and APIs.
- Dynamic context profiles (minimal, balanced, full) based on the model used.
- Message queue (`queue.Queue`) for thread‑safe GUI updates (initial implementation).

### GUI
- Main window with dark purple theme, circular avatar, online status.
- Chat with bubbles (user on the right, Syna on the left).
- Multiline input with Shift+Enter and Enter to send.
- Expandable Output panel for real‑time debugging.
- Buttons: "limpar" (clear history) and "reload" (restart Syna).
- Toggle button 🧠 for Think Mode.
- Removed Overlay mode (unstable on Linux).

### Intelligence & Conversation
- Primary local model via Ollama (qwen2.5:3b) with light prompt for speed.
- Automatic fallback to APIs: moonshotai/kimi-k2-instruct-0905 (Groq), google/gemini-2.0-flash-exp:free, qwen/qwen3.6-plus-preview:free (OpenRouter).
- Persistent memory (`memory.md` and `personality.md`) updated on close.
- Context awareness: active window and title captured via `xprop`, injected into prompt.
- Think Mode (`/think` or button): displays internal reasoning between `<thinking>` tags in Output.

### System Tools
- Open apps (terminal, godot, firefox, spotify, tlauncher).
- Open folders (documentos, downloads, desktop, imagens, músicas, vídeos).
- Search files (`find ~ -name`).
- Create, edit, move, delete files (with creative content generation via LLM).
- System health check (uptime, RAM, disk, load average, top processes).

### Computer Vision
- Screenshot on demand (`olha minha tela`), analyzed with Scout model (Groq).
- Local image reading (`analisa a imagem ~/caminho`), using the same Scout model.

### File Reading
- Supported formats: .txt, .md, .py, .gd, .json, .cfg, .docx (includes tables), .pdf, .xlsx.
- Automatic truncation for files > 8000 characters.

### Web Search
- DuckDuckGo search (`pesquise`, `procure por`).
- Clean text extraction and summarization with a lightweight model.

### Reminders
- Scheduling by relative time (`daqui 10 minutos`) and absolute (`às 17:30`).
- Native notifications (`notify-send`) with Syna icon and dynamic duration.
- Notification logs in conversation history.

### Autonomy
- Autonomous observer thread that monitors context (app, focus time, inactivity) and sends proactive notifications using the local model (qwen2.5:1.5b).