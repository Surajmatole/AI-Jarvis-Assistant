import threading

from ui.ui import JarvisUI
from main import start_jarvis


if __name__ == "__main__":

    # Create UI
    app = JarvisUI()

    # Start Jarvis in Background
    threading.Thread(
        target=start_jarvis,
        args=(app,),
        daemon=True
    ).start()

    # Run UI (Main Thread)
    app.run()