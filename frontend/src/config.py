import os
from typing import Optional

from constants import ENV_FILE_PATH
from dotenv import load_dotenv


load_dotenv(dotenv_path=ENV_FILE_PATH)


class Settings:
    def __init__(self):
        self.ENV = os.getenv("ENV", "local")
        self.is_local = self.ENV == "local"
        self.API_BASE_URL = "http://localhost/api"


_settings_instance: Optional[Settings] = None


def get_settings() -> Settings:
    global _settings_instance
    if _settings_instance is None:
        _settings_instance = Settings()
    return _settings_instance
