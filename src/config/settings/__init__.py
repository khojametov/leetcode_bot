import os
from importlib import import_module

from src.config.settings.base import Settings


def get_settings() -> Settings:
    settings_module = os.getenv("SETTINGS_MODULE", "src.config.settings.dev")
    return import_module(settings_module).Settings()


settings = get_settings()
