import os
import threading
from django.apps import AppConfig
from .main import start_bot

class BotConfig(AppConfig):
    name = 'bot'

    def ready(self):
        # Start the bot in a separate thread when the app is ready
        if os.environ.get('RUN_MAIN') != 'true':
            return
        
        thread = threading.Thread(target=start_bot)
        thread.daemon = True
        thread.start()