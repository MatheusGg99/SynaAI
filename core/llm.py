# llm.py
# Communication with language models (Local, Groq, OpenRouter)

from core.clients import groq_client, kobold_client
from core.config import (
    PRIMARY_MODEL, FALLBACK_MODELS,
    SYSTEM_PROMPT_FILE, MEMORY_FILE, PERSONALITY_FILE, SYSTEM_PROMPT_LITE_FILE
)
from core.utils import log_error, log_token_usage, load_file, truncate_text, get_last_external_context, _syna_app_instance
from core.memory_engine import MemoryEngine
from datetime import datetime
import time
import re

# ------------------------------------------------------------
# PROVIDER → CLIENT MAPPING
# ------------------------------------------------------------

PROVIDER_TO_CLIENT = {
    "groq": groq_client,
    "kobold": kobold_client,
}

# Vector Memory Engine (loaded once)
_memory_engine = None

def _get_memory_engine():
    """Initializes the memory engine on demand (Singleton)."""
    global _memory_engine
    if _memory_engine is None:
        _memory_engine = MemoryEngine()
    return _memory_engine

# ------------------------------------------------------------
# HISTORY AND PROMPT
# ------------------------------------------------------------
conversation_history = []

# Context profiles based on model capabilities
CONTEXT_PROFILES = {
    # Local models: ultra-light
    "gemma-2-2b-it-Q4_K_M": "minimal",
    
    # APIs with limited TPM: balanced
    "moonshotai/kimi-k2-instruct-0905": "balanced",
    "qwen/qwen3-32b": "balanced",
    
    # Robust APIs: full
    "aya-expanse-8b-Q4_K_M": "full",
    "llama-3.3-70b-versatile": "full",
    "openai/gpt-oss-120b": "full",
}

def get_history_limit(model_name):
    """Returns the number of history messages based on the profile."""
    profile = CONTEXT_PROFILES.get(model_name, "balanced")
    limits = {"minimal": 4, "balanced": 8, "full": 30}
    return limits.get(profile, 5)

def get_max_tokens(model_name):
    """Returns max_tokens based on the profile."""
    profile = CONTEXT_PROFILES.get(model_name, "balanced")
    limits = {"minimal": 512, "balanced": 1000, "full": 4096}
    return limits.get(profile, 512)

def build_dynamic_prompt(model_name):
    """Builds the system prompt based on the model's profile."""
    profile = CONTEXT_PROFILES.get(model_name, "balanced")
    
    # Identity base (common to all)
    if profile == "minimal":
        base = load_file(SYSTEM_PROMPT_LITE_FILE)
        personality = truncate_text(load_file(PERSONALITY_FILE), 520)
    elif profile == "balanced":
        base = truncate_text(load_file(SYSTEM_PROMPT_FILE), 1000)
        personality = truncate_text(load_file(PERSONALITY_FILE), 1500)
    else:  # full
        base = load_file(SYSTEM_PROMPT_FILE)
        personality = load_file(PERSONALITY_FILE)
    
    ctx = get_last_external_context()
    live_context = f"Context: {ctx['app']} - {ctx['title']} ({datetime.now().strftime('%H:%M')})"
    
    parts = [base, live_context]
    if personality:
        parts.append(f"Personality: {personality}")
    
    return "\n\n".join(parts)

# ------------------------------------------------------------
# MAIN CONVERSATION FUNCTION
# ------------------------------------------------------------
def ask_syna(user_input, task_type="default", think_mode=False):
    """
    Sends the message to the appropriate model and returns the reply.
    task_type can be "default", "think", "code" (future expansion).
    """
    global conversation_history
    conversation_history.append({"role": "user", "content": user_input})

    # Build the list of models to try
    models_to_try = []

    # Primary model is always tried first
    models_to_try.append({
        "model": PRIMARY_MODEL,
        "client": kobold_client,
    })

    # Add fallbacks (converting provider → client)
    for fb in FALLBACK_MODELS:
        provider = fb.get("provider")
        if not provider:
            log_error(f"Fallback without provider defined: {fb}")
            continue
        client_to_use = PROVIDER_TO_CLIENT.get(provider)
        if client_to_use:
            models_to_try.append({
                "model": fb["model"],
                "client": client_to_use,
            })
        else:
            log_error(f"Unknown provider in fallbacks: {provider}")

    last_error = None
    for entry in models_to_try:
        model_name = entry["model"]
        client_to_use = entry["client"]
        
        # Apply limits based on model
        history_limit = get_history_limit(model_name)
        max_tok = get_max_tokens(model_name)
        history_to_send = conversation_history[-history_limit:]
        prompt = build_dynamic_prompt(model_name)
        
        try:
            print("DEBUG: Querying vector memory...")
            engine = _get_memory_engine()
            memory_context = engine.remember_context(user_input)
            print(f"DEBUG: Memory returned: {repr(memory_context)}")
            if memory_context:
                print("DEBUG: Injecting memory into prompt...")
                prompt += f"\n\n{memory_context}\n(Use this information if relevant to the user's question.)"
                print("DEBUG: Injection complete.")
        except Exception as e:
            print(f"DEBUG: ERROR in memory: {e}")
            log_error(f"Error querying vector memory: {e}")

        if think_mode:
            prompt += "\n\n## THINK MODE ENABLED\nBefore answering, think step by step about the user's question. Place your complete reasoning between <thinking> and </thinking> tags. Then provide your final answer normally."
        
        try:
            response = client_to_use.chat.completions.create(
                model=model_name,
                messages=[{"role": "system", "content": prompt}] + history_to_send,
                max_tokens=max_tok,
                temperature=0.8,
            )
            reply = response.choices[0].message.content

            if think_mode:
                thinking_match = re.search(r'<thinking>(.*?)</thinking>', reply, re.DOTALL)
                if thinking_match:
                    thinking_content = thinking_match.group(1).strip()
                    # Log the thinking in the output panel
                    if _syna_app_instance:
                        _syna_app_instance.log_status(f"🧠 Reasoning:\n{thinking_content}")
                    # Remove the thinking block from the final reply
                    reply = re.sub(r'<thinking>.*?</thinking>', '', reply, flags=re.DOTALL).strip()
            
            # Auto-truncate: keep only the last 40 messages (20 user+assistant pairs)
            if len(conversation_history) > 40:
                # Preserve the system message at index 0
                conversation_history = conversation_history[:1] + conversation_history[-39:]

            usage = response.usage
            if usage:
                log_token_usage(usage.prompt_tokens, usage.completion_tokens, usage.total_tokens)
            
            return reply
        except Exception as e:
            last_error = e
            log_error(f"Failed on model {model_name}: {e}. Trying next...")
            time.sleep(1)

    # All models failed
    log_error(f"All models failed. Last error: {last_error}")
    return f"[Critical error: Could not connect to any model. Last error: {last_error}]"