# syna.py
# Main entry point for Syna – launches GUI, context trackers, and autonomous observer.

import sys
import os
import threading
import time
from core.gui import SynaApp
from core.utils import set_syna_app_instance, set_last_external_context, log_error
from core.config import PROJECT_ROOT
from tools.tools import send_desktop_notification
from observers.autonomous_observer import autonomous_monitor
from context_tracker import update_context


def get_version():
    """Reads the version number from VERSION file in project root."""
    try:
        version_path = os.path.join(PROJECT_ROOT, "VERSION")
        with open(version_path, "r") as f:
            return f.read().strip()
    except Exception:
        return "1.1.0"  # fallback


def update_window_context():
    """Background thread: tracks the active window and updates the external context."""
    import subprocess
    from core.utils import set_last_external_context, log_error

    while True:
        try:
            root_cmd = subprocess.Popen(
                ['xprop', '-root', '_NET_ACTIVE_WINDOW'],
                stdout=subprocess.PIPE,
                stderr=subprocess.DEVNULL
            )
            stdout, _ = root_cmd.communicate()

            if stdout and b"not found" not in stdout:
                window_id = stdout.split()[-1].decode()
                window_cmd = subprocess.Popen(
                    ['xprop', '-id', window_id, 'WM_NAME', 'WM_CLASS'],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.DEVNULL
                )
                stdout, _ = window_cmd.communicate()
                output = stdout.decode()

                title = "Unknown"
                app = "System"
                for line in output.splitlines():
                    if "WM_NAME" in line:
                        title = line.split('=', 1)[-1].strip().strip('"')
                    if "WM_CLASS" in line:
                        app = line.split(',')[-1].strip().strip('"')

                # Ignore Syna's own windows to avoid self-referential context
                if app.lower() not in ["tk", "syna", "python3"]:
                    set_last_external_context(title, app)
        except Exception as e:
            log_error(f"Error in update_window_context: {e}")

        time.sleep(1)


def context_updater():
    """Background thread: periodically updates the context tracker."""
    while True:
        update_context()
        time.sleep(5)


if __name__ == "__main__":
    # Ensure the project root is in sys.path (for direct execution)
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    if project_root not in sys.path:
        sys.path.insert(0, project_root)

    app = SynaApp()
    app.version = get_version()
    set_syna_app_instance(app)

    # Launch background threads
    context_thread = threading.Thread(target=update_window_context, daemon=True)
    context_thread.start()

    context_update_thread = threading.Thread(target=context_updater, daemon=True)
    context_update_thread.start()

    observer_thread = threading.Thread(
        target=autonomous_monitor,
        args=(7,),  # check every 7 minutes
        daemon=True
    )
    observer_thread.start()

    app.mainloop()