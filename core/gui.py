# gui.py
# Graphical user interface for Syna using CustomTkinter.

import customtkinter as ctk
import threading
import time
import os
import queue
from datetime import datetime
from PIL import Image, ImageDraw
from core.constants import MEMORY_MODEL
from core.config import MEMORY_FILE, PERSONALITY_FILE, MODEL, PROJECT_ROOT
from core.utils import log_error, load_file, save_memory
from core.llm import ask_syna, kobold_client, conversation_history, _get_memory_engine
from tools.tools import send_desktop_notification


class SynaApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Syna")
        self.geometry("720x620")
        self.resizable(True, True)
        ctk.set_appearance_mode("dark")

        self.purple = "#A855F7"
        self.purple_light = "#C084FC"
        self.dark_bg = "#0B0B12"
        self.darker = "#14141E"
        self.bubble_user = "#A855F7"
        self.bubble_syna = "#1E1E2E"
        self.cyan = "#06B6D4"
        self.pink = "#EC4899"
        self.text_primary = "#E2E8F0"
        self.text_secondary = "#94A3B8"
        self.border_color = "#2D2D44"

        self.configure(fg_color=self.dark_bg)
        self.pending_responses = []

        # ---- FONTS ----
        self.font_title = ctk.CTkFont(family="Orbitron", size=15, weight="bold")
        self.font_btn = ctk.CTkFont(family="Orbitron", size=11)
        self.font_chat = ctk.CTkFont(family="JetBrains Mono", size=13)
        self.font_mono = ctk.CTkFont(family="JetBrains Mono", size=10)

        # ---- Load avatar (from project assets) ----
        self.avatar_image = None
        avatar_path = os.path.join(PROJECT_ROOT, "assets", "icon.png")
        if os.path.exists(avatar_path):
            img = Image.open(avatar_path).resize((28, 28))
            # Cria máscara circular
            mask = Image.new("L", (28, 28), 0)
            draw = ImageDraw.Draw(mask)
            draw.ellipse((0, 0, 28, 28), fill=255)
            img.putalpha(mask)
            self.avatar_image = ctk.CTkImage(img, size=(28, 28))

        # ---- Header ----
        self.header = ctk.CTkFrame(self, fg_color=self.darker, height=56, corner_radius=0)
        self.header.pack(fill="x")
        self.header.pack_propagate(False)

        header_left = ctk.CTkFrame(self.header, fg_color="transparent")
        header_left.pack(side="left", padx=12, pady=8)

        if self.avatar_image:
            avatar_label = ctk.CTkLabel(header_left, image=self.avatar_image, text="")
            avatar_label.pack(side="left", padx=(0, 8))

        name_frame = ctk.CTkFrame(header_left, fg_color="transparent")
        name_frame.pack(side="left")

        ctk.CTkLabel(
            name_frame,
            text="SYNA",
            font=self.font_title,
            text_color=self.purple_light
        ).pack(anchor="w")

        self.status_label = ctk.CTkLabel(
            name_frame,
            text="● ONLINE",
            font=self.font_btn,
            text_color=self.cyan
        )
        self.status_label.pack(anchor="w")

        # ---- CYBER BUTTONS ----

        self.clear_btn = ctk.CTkButton(
            self.header,
            text="[LIMPAR]",
            width=70,
            height=28,
            font=self.font_btn,
            fg_color="transparent",
            border_color=self.purple,
            border_width=1,
            hover_color="#2D2D44",
            corner_radius=4,
            command=self.clear_chat
        )
        self.clear_btn.pack(side="right", padx=6)

        self.voice_btn = ctk.CTkButton(
            self.header,
            text="[VOZ]",
            width=50,
            height=28,
            font=self.font_btn,
            fg_color="transparent",
            border_color=self.purple,
            border_width=1,
            hover_color="#2D2D44",
            corner_radius=4,
            command=self.start_voice_mode
        )
        self.voice_btn.pack(side="right", padx=6)

        self.reload_btn = ctk.CTkButton(
            self.header,
            text="[REBOOT]",
            width=70,
            height=28,
            font=self.font_btn,
            fg_color="transparent",
            border_color=self.purple,
            border_width=1,
            hover_color="#2D2D44",
            corner_radius=4,
            command=self.reload_syna
        )
        self.reload_btn.pack(side="right", padx=6)

        self.think_btn = ctk.CTkButton(
            self.header,
            text="[PENSAR]",
            width=70,
            height=28,
            font=self.font_btn,
            fg_color="transparent",
            border_color=self.purple,
            border_width=1,
            hover_color="#2D2D44",
            corner_radius=4,
            command=self.toggle_think_mode
        )
        self.think_btn.pack(side="right", padx=6)

        self.speak_all_btn = ctk.CTkButton(
            self.header,
            text="[FALAR]",
            width=70,
            height=28,
            font=self.font_btn,
            fg_color="transparent",
            border_color=self.purple,
            border_width=1,
            hover_color="#2D2D44",
            corner_radius=4,
            command=self.toggle_speak_all
        )
        self.speak_all_btn.pack(side="right", padx=6)

                # ---- CHAT FRAME ----
        self.chat_frame = ctk.CTkScrollableFrame(
            self,
            fg_color=self.dark_bg,
            corner_radius=0
        )
        self.chat_frame.pack(fill="both", expand=True, padx=0, pady=0)
        self.after(100, self.bind_scroll)

        # ---- INPUT AREA ----
        self.input_frame = ctk.CTkFrame(self, fg_color=self.darker, corner_radius=4)
        self.input_frame.pack(fill="x", padx=16, pady=(8, 4))

        self.input_field = ctk.CTkTextbox(
            self.input_frame,
            font=self.font_chat,
            fg_color="#0A0A12",
            text_color=self.text_primary,
            border_color=self.purple,
            border_width=1,
            height=72,
            corner_radius=4,
            wrap="word"
        )
        self.input_field.pack(side="left", fill="x", expand=True, padx=(12, 8), pady=10)
        self.input_field.bind("<Return>", self.on_enter)
        self.input_field.bind("<Shift-Return>", self.on_shift_enter)

        self.send_btn = ctk.CTkButton(
            self.input_frame,
            text="→",
            width=48,
            height=72,
            font=ctk.CTkFont(size=18, weight="bold"),
            fg_color=self.purple,
            hover_color=self.purple_light,
            corner_radius=4,
            command=self.send_message
        )
        self.send_btn.pack(side="right", padx=(0, 12), pady=10)

        # ---- HINT ----
        self.hint_label = ctk.CTkLabel(
            self,
            text="ENTER para enviar  •  SHIFT+ENTER nova linha",
            font=ctk.CTkFont(size=10, family="JetBrains Mono"),
            text_color=self.text_secondary
        )
        self.hint_label.pack(pady=(0, 8))

        # ---- OUTPUT PANEL (debug) ----
        self.output_visible = False
        self.output_header = ctk.CTkButton(
            self,
            text="▼ OUTPUT",
            width=80,
            height=20,
            font=self.font_btn,
            fg_color="transparent",
            border_color=self.purple,
            border_width=1,
            hover_color="#2D2D44",
            corner_radius=4,
            command=self.toggle_output
        )
        self.output_header.pack(pady=(4, 0))

        self.output_frame = ctk.CTkFrame(self, fg_color="#0A0A12", corner_radius=4, height=120)
        # Starts hidden

        self.output_text = ctk.CTkTextbox(
            self.output_frame,
            font=self.font_mono,
            fg_color="#0A0A12",
            text_color="#88DD88",
            border_color=self.border_color,
            border_width=1,
            wrap="word",
            activate_scrollbars=True,
            height=120,
            corner_radius=4
        )
        self.output_text.pack(fill="both", expand=True, padx=4, pady=4)
        self.output_text.configure(state="disabled")

        # ---- GREETING ----
        hour = datetime.now().hour
        if hour < 12:
            greeting = "Bom dia, Matheus. Sistemas online."
        elif hour < 18:
            greeting = "Boa tarde, Matheus. Estou pronta para continuar."
        else:
            greeting = "Boa noite, Matheus. De volta ao trabalho?"
        self.append_date_separator()
        self.append_message("Syna", greeting)
        self.protocol("WM_DELETE_WINDOW", self.on_close)

        self.message_queue = queue.Queue()

        self.think_mode_enabled = False
        self.speak_all_enabled = False

        self.after(100, self.process_queue)

    # ------------------------------------------------------------------
    # Queue processing (thread-safe GUI updates)
    # ------------------------------------------------------------------
    def process_queue(self):
        """Process messages from the queue (sent from other threads)."""
        try:
            while True:
                task = self.message_queue.get_nowait()
                if task['type'] == 'append_message':
                    self.append_message(task['sender'], task['message'])
                elif task['type'] == 'log_status':
                    self.log_status(task['message'])
                elif task['type'] == 'update_status':
                    self.status_label.configure(text=task['text'], text_color=task['color'])
                elif task['type'] == 'send_btn_state':
                    self.send_btn.configure(state=task['state'])
                elif task['type'] == 'hide_typing':
                    self.hide_typing()
        except queue.Empty:
            pass
        finally:
            self.after(100, self.process_queue)

    def enqueue(self, task):
        """Thread-safe method to add a task to the queue."""
        self.message_queue.put(task)

    # ------------------------------------------------------------------
    # UI toggles
    # ------------------------------------------------------------------
    def toggle_output(self):
        if self.output_visible:
            self.output_frame.pack_forget()
            self.output_header.configure(text="▼ Output")
            self.output_visible = False
        else:
            self.output_frame.pack(fill="x", padx=16, pady=(0, 4), before=self.hint_label)
            self.output_header.configure(text="▲ Output")
            self.output_visible = True
            self.output_text.see("end")

    def toggle_think_mode(self):
        self.think_mode_enabled = not self.think_mode_enabled
        if self.think_mode_enabled:
            self.think_btn.configure(fg_color=self.purple, text_color="white")
            self.log_status("🧠 Think mode ENABLED.")
        else:
            self.think_btn.configure(fg_color="transparent", text_color=self.purple_light)
            self.log_status("🧠 Think mode DISABLED.")

    def toggle_speak_all(self):
        self.speak_all_enabled = not self.speak_all_enabled
        if self.speak_all_enabled:
            self.speak_all_btn.configure(fg_color=self.purple, text_color="white")
            self.log_status("🔊 'Speak All' mode ENABLED.")
        else:
            self.speak_all_btn.configure(fg_color="transparent", text_color=self.purple_light)
            self.log_status("🔊 'Speak All' mode DISABLED.")

    # ------------------------------------------------------------------
    # Logging
    # ------------------------------------------------------------------
    def log_status(self, message):
        """Add a log line to the output panel."""
        timestamp = datetime.now().strftime("%H:%M:%S")
        line = f"[{timestamp}] {message}\n"
        self.output_text.configure(state="normal")
        self.output_text.insert("end", line)
        self.output_text.see("end")
        self.output_text.configure(state="disabled")

    # ------------------------------------------------------------------
    # Reload / restart
    # ------------------------------------------------------------------
    def reload_syna(self):
        """Restart the Syna application (requires start_all.sh)."""
        import subprocess
        self.on_close()
        # start_all.sh is not included in the public repo – it's a local convenience script
        start_script = os.path.join(PROJECT_ROOT, "start_all.sh")
        subprocess.Popen(["python3", start_script])

    # ------------------------------------------------------------------
    # Core input processing
    # ------------------------------------------------------------------
    def process_user_input(self, user_input):
        from context_tracker import mark_syna_interaction
        mark_syna_interaction()

        think_mode = self.think_mode_enabled
        if user_input.startswith("/think "):
            user_input = user_input[7:].strip()
        if think_mode:
            self.log_status("🧠 Processing with think mode...")

        self.log_status(f"Processing: '{user_input[:50]}{'...' if len(user_input) > 50 else ''}'")

        # Layer architecture
        from core.router import classify_intent
        try:
            from layers.system_layer import SystemLayer
            from layers.web_layer import WebLayer
            from layers.automation_layer import AutomationLayer
            print("DEBUG: All layers imported successfully.")
        except Exception as import_err:
            print(f"DEBUG: ERROR importing layers: {import_err}")
            import traceback
            traceback.print_exc()
            SystemLayer = WebLayer = AutomationLayer = None

        candidates = classify_intent(user_input)
        self.log_status(f"🎯 Candidate layers: {candidates}")
        print(f"DEBUG: candidates = {candidates}")

        if SystemLayer is not None:
            layers_map = {
                "system": SystemLayer(),
                "web": WebLayer(),
                "automation": AutomationLayer(),
            }
            for layer_name, score in candidates:
                if layer_name in layers_map:
                    layer = layers_map[layer_name]
                    print(f"DEBUG: Calling layer.handle for {layer_name} with input '{user_input}'")
                    try:
                        reply = layer.handle(user_input)
                        print(f"DEBUG: handle returned: {repr(reply)}")
                    except Exception as e:
                        print(f"DEBUG: Exception in layer.handle: {e}")
                        import traceback
                        traceback.print_exc()
                        reply = None

                    if reply is not None:
                        self.log_status(f"✅ Layer '{layer_name}' handled the input.")
                        if self.speak_all_enabled:
                            from core.voice import speak
                            threading.Thread(target=speak, args=(reply,), daemon=True).start()
                        conversation_history.append({"role": "user", "content": user_input, "type": "command"})
                        conversation_history.append({"role": "assistant", "content": reply, "type": "command"})
                        return reply
                    else:
                        self.log_status(f"   Layer '{layer_name}' could not handle, trying next...")
        else:
            print("DEBUG: SystemLayer not imported, skipping layers.")

        # Fallback to conversation
        self.log_status("→ No specialized layer handled, using fallback (Conversation)...")
        reply = ask_syna(user_input)
        if self.speak_all_enabled:
            from core.voice import speak
            threading.Thread(target=speak, args=(reply,), daemon=True).start()
        return reply

    # ------------------------------------------------------------------
    # Chat display helpers
    # ------------------------------------------------------------------
    def process_queue(self):
        try:
            while True:
                task = self.message_queue.get_nowait()
                if task['type'] == 'append_message':
                    self.append_message(task['sender'], task['message'])
                elif task['type'] == 'log_status':
                    self.log_status(task['message'])
                elif task['type'] == 'update_status':
                    self.status_label.configure(text=task['text'], text_color=task['color'])
                elif task['type'] == 'send_btn_state':
                    self.send_btn.configure(state=task['state'])
                elif task['type'] == 'hide_typing':
                    self.hide_typing()
        except queue.Empty:
            pass
        finally:
            self.after(100, self.process_queue)

    def enqueue(self, task):
        self.message_queue.put(task)

    def toggle_output(self):
        if self.output_visible:
            self.output_frame.pack_forget()
            self.output_header.configure(text="▼ OUTPUT")
            self.output_visible = False
        else:
            self.output_frame.pack(fill="x", padx=16, pady=(0, 4), before=self.hint_label)
            self.output_header.configure(text="▲ OUTPUT")
            self.output_visible = True
            self.output_text.see("end")

    def toggle_think_mode(self):
        self.think_mode_enabled = not self.think_mode_enabled
        if self.think_mode_enabled:
            self.think_btn.configure(fg_color=self.purple, text_color="white")
            self.log_status("🧠 Think mode ENABLED.")
        else:
            self.think_btn.configure(fg_color="transparent", text_color=self.purple_light)
            self.log_status("🧠 Think mode DISABLED.")

    def toggle_speak_all(self):
        self.speak_all_enabled = not self.speak_all_enabled
        if self.speak_all_enabled:
            self.speak_all_btn.configure(fg_color=self.purple, text_color="white")
            self.log_status("🔊 'Speak All' mode ENABLED.")
        else:
            self.speak_all_btn.configure(fg_color="transparent", text_color=self.purple_light)
            self.log_status("🔊 'Speak All' mode DISABLED.")

    def log_status(self, message):
        timestamp = datetime.now().strftime("%H:%M:%S")
        line = f"[{timestamp}] {message}\n"
        self.output_text.configure(state="normal")
        self.output_text.insert("end", line)
        self.output_text.see("end")
        self.output_text.configure(state="disabled")

    def reload_syna(self):
        import subprocess
        self.on_close()
        start_script = os.path.join(PROJECT_ROOT, "start_all.sh")
        subprocess.Popen(["python3", start_script])

    def process_user_input(self, user_input):
        from context_tracker import mark_syna_interaction
        mark_syna_interaction()

        think_mode = self.think_mode_enabled
        if user_input.startswith("/think "):
            user_input = user_input[7:].strip()
        if think_mode:
            self.log_status("🧠 Processing with think mode...")

        self.log_status(f"Processing: '{user_input[:50]}{'...' if len(user_input) > 50 else ''}'")

        from core.router import classify_intent
        try:
            from layers.system_layer import SystemLayer
            from layers.web_layer import WebLayer
            from layers.automation_layer import AutomationLayer
            print("DEBUG: All layers imported successfully.")
        except Exception as import_err:
            print(f"DEBUG: ERROR importing layers: {import_err}")
            import traceback
            traceback.print_exc()
            SystemLayer = WebLayer = AutomationLayer = None

        candidates = classify_intent(user_input)
        self.log_status(f"🎯 Candidate layers: {candidates}")
        print(f"DEBUG: candidates = {candidates}")

        if SystemLayer is not None:
            layers_map = {
                "system": SystemLayer(),
                "web": WebLayer(),
                "automation": AutomationLayer(),
            }
            for layer_name, score in candidates:
                if layer_name in layers_map:
                    layer = layers_map[layer_name]
                    print(f"DEBUG: Calling layer.handle for {layer_name} with input '{user_input}'")
                    try:
                        reply = layer.handle(user_input)
                        print(f"DEBUG: handle returned: {repr(reply)}")
                    except Exception as e:
                        print(f"DEBUG: Exception in layer.handle: {e}")
                        import traceback
                        traceback.print_exc()
                        reply = None

                    if reply is not None:
                        self.log_status(f"✅ Layer '{layer_name}' handled the input.")
                        if self.speak_all_enabled:
                            from core.voice import speak
                            threading.Thread(target=speak, args=(reply,), daemon=True).start()
                        conversation_history.append({"role": "user", "content": user_input, "type": "command"})
                        conversation_history.append({"role": "assistant", "content": reply, "type": "command"})
                        return reply
                    else:
                        self.log_status(f"   Layer '{layer_name}' could not handle, trying next...")
        else:
            print("DEBUG: SystemLayer not imported, skipping layers.")

        self.log_status("→ No specialized layer handled, using fallback (Conversation)...")
        reply = ask_syna(user_input)
        if self.speak_all_enabled:
            from core.voice import speak
            threading.Thread(target=speak, args=(reply,), daemon=True).start()
        return reply

    def append_date_separator(self):
        today = datetime.now().strftime("%d de %B de %Y")
        row = ctk.CTkFrame(self.chat_frame, fg_color="transparent")
        row.pack(fill="x", padx=24, pady=8)

        ctk.CTkFrame(row, fg_color="#333355", height=1).pack(
            side="left", fill="x", expand=True, pady=6
        )
        ctk.CTkLabel(
            row,
            text=f"  {today}  ",
            font=ctk.CTkFont(size=11, family="JetBrains Mono"),
            text_color=self.text_secondary
        ).pack(side="left")
        ctk.CTkFrame(row, fg_color="#333355", height=1).pack(
            side="left", fill="x", expand=True, pady=6
        )

    def append_message(self, sender, message):
        import re
        timestamp = datetime.now().strftime("%H:%M")
        is_user = sender == "Você"

        message = re.sub(r'\*\*(.*?)\*\*', r'[\1]', message)
        message = re.sub(r'\*(.*?)\*', r'\1', message)
        message = re.sub(r'^#{1,3}\s+(.+)$', r'▸ \1', message, flags=re.MULTILINE)
        message = re.sub(r'^\s*[-*]\s+', '  • ', message, flags=re.MULTILINE)
        message = re.sub(r'```[\w]*\n?(.*?)```', r'\1', message, flags=re.DOTALL)
        message = re.sub(r'`(.*?)`', r'[\1]', message)

        row = ctk.CTkFrame(self.chat_frame, fg_color="transparent")
        row.pack(fill="x", padx=12, pady=(4, 0))

        outer = ctk.CTkFrame(row, fg_color="transparent")
        outer.pack(anchor="e" if is_user else "w")

        meta = ctk.CTkFrame(outer, fg_color="transparent")
        meta.pack(fill="x", pady=(0, 2))

        if not is_user and self.avatar_image:
            ctk.CTkLabel(
                meta,
                image=self.avatar_image,
                text=""
            ).pack(side="left", padx=(0, 6))

        ctk.CTkLabel(
            meta,
            text=f"{'Você' if is_user else 'Syna'}  {timestamp}",
            font=ctk.CTkFont(size=11, family="JetBrains Mono"),
            text_color=self.text_secondary
        ).pack(side="left" if not is_user else "right")

        bubble_color = self.bubble_user if is_user else self.bubble_syna
        text_color = self.text_primary

        bubble = ctk.CTkFrame(outer, fg_color=bubble_color, corner_radius=8)
        bubble.pack(anchor="e" if is_user else "w")

        msg_text = ctk.CTkTextbox(
            bubble,
            font=self.font_chat,
            text_color=text_color,
            fg_color=bubble_color,
            border_width=0,
            wrap="word",
            activate_scrollbars=False,
            cursor="arrow",
            height=1,
            width=480,
        )
        msg_text.insert("1.0", message)
        msg_text.configure(state="disabled")
        msg_text.pack(padx=14, pady=8)

        def fix_height(widget=msg_text):
            widget.update_idletasks()
            try:
                widget.configure(state="normal")
                num_lines = int(widget.index("end-1c").split(".")[0])
                widget.configure(state="disabled")
                widget.configure(height=num_lines * 21 + 4)
            except:
                pass

        msg_text.after(10, fix_height)
        msg_text.after(100, fix_height)
        msg_text.after(300, fix_height)

        self.chat_frame.after(350, lambda: self.chat_frame._parent_canvas.yview_moveto(1.0))

    def bind_scroll(self):
        canvas = self.chat_frame._parent_canvas

        def scroll_up(e):
            if str(e.widget) == str(canvas) or str(e.widget).startswith(str(self.chat_frame)):
                canvas.yview_scroll(-1, "units")

        def scroll_down(e):
            if str(e.widget) == str(canvas) or str(e.widget).startswith(str(self.chat_frame)):
                canvas.yview_scroll(1, "units")

        self.bind_all("<Button-4>", scroll_up)
        self.bind_all("<Button-5>", scroll_down)

    def show_typing(self):
        self.typing_row = ctk.CTkFrame(self.chat_frame, fg_color="transparent")
        self.typing_row.pack(fill="x", padx=12, pady=(4, 0), anchor="w")

        bubble = ctk.CTkFrame(
            self.typing_row,
            fg_color=self.bubble_syna,
            corner_radius=8
        )
        bubble.pack(anchor="w")

        self.typing_label = ctk.CTkLabel(
            bubble,
            text="  ···  ",
            font=ctk.CTkFont(family="JetBrains Mono", size=16),
            text_color=self.purple_light
        )
        self.typing_label.pack(padx=14, pady=8)
        self._animate_typing(0)

    def _animate_typing(self, step):
        if not hasattr(self, 'typing_label') or not self.typing_label.winfo_exists():
            return
        dots = ["  ·      ", "  · ·    ", "  · · ·  "]
        self.typing_label.configure(text=dots[step % 3])
        self._typing_job = self.after(400, lambda: self._animate_typing(step + 1))

    def hide_typing(self):
        if hasattr(self, '_typing_job'):
            self.after_cancel(self._typing_job)
        if hasattr(self, 'typing_row') and self.typing_row.winfo_exists():
            self.typing_row.destroy()

    def clear_chat(self):
        for widget in self.chat_frame.winfo_children():
            widget.destroy()
        conversation_history.clear()
        self.append_message("Syna", "Conversa limpa. Como posso ajudar?")

    def on_enter(self, event):
        self.send_message()
        return "break"

    def on_shift_enter(self, event):
        return None

    def get_input_text(self):
        return self.input_field.get("1.0", "end").strip()

    def clear_input(self):
        self.input_field.delete("1.0", "end")

    def send_message(self, event=None):
        user_input = self.get_input_text()
        if not user_input:
            return
        self.clear_input()
        self.append_message("Você", user_input)
        self.status_label.configure(text="● PENSANDO...", text_color="#f39c12")
        self.send_btn.configure(state="disabled")
        self.show_typing()

        def process():
            reply = self.process_user_input(user_input)
            self.after(0, self.hide_typing)
            self.after(0, lambda: self.append_message("Syna", reply))
            self.after(0, lambda: self.status_label.configure(text="● ONLINE", text_color=self.cyan))
            self.after(0, lambda: self.send_btn.configure(state="normal"))

        threading.Thread(target=process, daemon=True).start()

    def start_voice_mode(self):
        self.log_status("🎤 Voice mode activated. Waiting for your speech...")
        threading.Thread(target=self.voice_loop, daemon=True).start()

    def voice_loop(self):
        try:
            from core.voice import listen, speak
            self.enqueue({'type': 'log_status', 'message': "🎤 Listening (5s)..."})
            user_input = listen(duration=5)
            self.enqueue({'type': 'log_status', 'message': f"📝 Transcription: '{user_input}'"})
            if not user_input:
                self.enqueue({'type': 'log_status', 'message': "❌ No audio captured."})
                return

            reply = self.process_user_input(user_input)
            self.enqueue({'type': 'append_message', 'sender': 'Syna', 'message': reply})
            speak(reply)

        except Exception as e:
            import traceback
            traceback.print_exc()
            self.enqueue({'type': 'log_status', 'message': f"❌ Voice error: {e}"})

    def on_close(self):
        if conversation_history:
            self.status_label.configure(text="● SALVANDO...", text_color="#f39c12")
            try:
                filtered_history = [msg for msg in conversation_history if msg.get("type") != "command"]

                diary_file = os.path.join(PROJECT_ROOT, "memory", "session_log.md")
                diary_prompt = (
                    "Você é um diarista. Resuma a conversa desta sessão em um parágrafo conciso, "
                    "destacando os tópicos principais, decisões tomadas e o tom geral da interação. "
                    "Escreva em português, sem títulos, apenas o texto."
                )
                try:
                    diary_response = kobold_client.chat.completions.create(
                        model=MEMORY_MODEL,
                        messages=[
                            {"role": "system", "content": diary_prompt},
                            {"role": "user", "content": str(filtered_history)}
                        ],
                        max_tokens=2048,
                    )
                    diary_text = diary_response.choices[0].message.content
                    with open(diary_file, "a", encoding="utf-8") as f:
                        f.write(f"\n---\n**Sessão {datetime.now().strftime('%d/%m/%Y %H:%M')}**\n{diary_text}\n")
                except Exception as e:
                    log_error(f"Failed to generate session diary: {e}")

                try:
                    extraction_prompt = (
                        "Você é um extrator de fatos. Dada a conversa abaixo, extraia frases curtas e objetivas "
                        "que representem informações factuais importantes, decisões ou detalhes de projetos mencionados. "
                        "Retorne cada frase em uma linha separada, sem numeração, sem marcadores, sem texto adicional. "
                        "Exemplo:\n"
                        "O protagonista do TRPG se chama Kael.\n"
                        "O sistema de magia usa runas antigas."
                    )
                    extraction_response = kobold_client.chat.completions.create(
                        model=MODEL,
                        messages=[
                            {"role": "system", "content": extraction_prompt},
                            {"role": "user", "content": str(filtered_history)}
                        ],
                        max_tokens=1024,
                        temperature=0.3,
                    )
                    facts_text = extraction_response.choices[0].message.content

                    engine = _get_memory_engine()
                    for line in facts_text.splitlines():
                        fact = line.strip()
                        if fact and not fact.startswith("Exemplo") and len(fact) > 5:
                            engine.remember(fact, {"tipo": "extraido", "sessao": datetime.now().isoformat()})
                except Exception as e:
                    log_error(f"Failed to index implicit memories: {e}")

            except Exception as e:
                log_error(e)
        self.destroy()