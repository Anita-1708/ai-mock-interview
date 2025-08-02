import os

class AppConfig:
    def __init__(self):
        self.openai_api_key = os.getenv("OPENAI_API_KEY", "your-key-here")
