# core/voice.py
import os
import time
import threading
import numpy as np
import soundfile as sf
import sounddevice as sd
import whisper

# ---- Confgis de Kokoro ----
# O modelo carrega apenas uma vez
_pipeline = None
_model_lock = threading.Lock()
VOICE_NAME = "pf_dora" #voz padrao
DEFAULT_SPEED = 1.3

# ---- Configs do Whisper (STT) ----
MODEL = whisper.load_model("base")

def _get_pipeline():
    """Gerencia o carregamendo do modelo Kokoro (Singelton)."""
    global _pipeline
    if _pipeline is None:
        with _model_lock:
            # Verifica novamenta para garantir que outra thread nao carregou o modelo enquanto espero
            if _pipeline is None:
                print("Syna esta carregando seu modelo de voz...")
                try:
                    from kokoro import KPipeline
                    _pipeline = KPipeline(lang_code="p")
                    print("Modelo de voz carregado com sucesso!")
                except ImportError:
                    print("Erro: Biblioteca 'kokoro' nao encontrada.")
                    raise
                except Exception as e:
                    print(f"Erro ao carregar modelo Kokoro: {e}")
                    raise
    return _pipeline

def _speak_kokoro(text, voice=VOICE_NAME, speed=1.0):
    """
    Função interna para sintetizar e reproduzir a fala com Kokoro.
    """
    if not text:
        return
        
    print(f"Syna esta falando: {text}")
    try:
        # 1. Obtem o pipeline
        pipeline = _get_pipeline()

        # 2. Sintetiza o audio em tempo real
        audio_chunks = []
        for _, _, chunk in pipeline(text, voice=voice, speed=speed):
            audio_chunks.append(chunk)

        if not audio_chunks:
            print("Nenhum audio foi gerado.")
            return
        
        audio_final = np.concatenate(audio_chunks)

        # 3. Salva em um arquivo temporario
        temp_file = "/tmp/syna_speech.wav"
        sf.write(temp_file, audio_final, 24000)

        # 4. Reproduz com aplay
        os.system(f"aplay {temp_file} > /dev/null 2>&1")

    except Exception as e:
        print(f"Erro na sintese de fala: {e}")

# ---- Função Pública (GUI chama) ----
def speak(text, voice=None, speed=None):
    """
    Função principal paras sintetizar fala.
    """
    # Usa a voz padrão se nenhuma for especificada
    selected_voice = voice if voice else VOICE_NAME
    selected_speed = speed if speed is not None else DEFAULT_SPEED
    _speak_kokoro(text, voice=selected_voice, speed=selected_speed)

# ---- Funções de STT ----
def listen(duration=5, sample_rate=16000):
    """
    Grava áudio do microfone por 'duration' segundos e retorna a transcrição.
    """
    print("Syna está ouvindo...")
    try:
        # Grava áudio
        audio = sd.rec(int(duration * sample_rate), samplerate=sample_rate, channels=1)
        sd.wait()  # Aguarda a gravação terminar

        # Converte para o formato esperado pelo Whisper (int16)
        audio = (audio * 32767).astype(np.int16)
        max_val = np.max(np.abs(audio))
        if max_val > 0:
            audio = (audio / max_val * 32767).astype(np.int16)
        # Salva em um arquivo temporário
        temp_file = "/tmp/syna_input.wav"
        import wave
        with wave.open(temp_file, 'wb') as wf:
            wf.setnchannels(1)
            wf.setsampwidth(2)
            wf.setframerate(sample_rate)
            wf.writeframes(audio.tobytes())

        # Transcreve com Whisper
        result = MODEL.transcribe(temp_file, language="pt", fp16=False)
        text = result["text"].strip()
        print(f"📝 Transcrição: {text}")
        return text

    except Exception as e:
        print(f"❌ Erro na gravação/transcrição: {e}")
        return ""
    