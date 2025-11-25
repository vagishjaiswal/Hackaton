import json
import os
from typing import Any, Dict
from dotenv import load_dotenv

class ConfigLoader:
    """
    Loads and validates JSON configuration files and environment variables.
    """
    @staticmethod
    def load_json_config(path: str) -> Dict[str, Any]:
        if not os.path.exists(path):
            raise FileNotFoundError(f"Config file not found: {path}")
        with open(path, 'r', encoding='utf-8') as f:
            try:
                return json.load(f)
            except json.JSONDecodeError as e:
                raise ValueError(f"Invalid JSON in config file {path}: {e}")

    @staticmethod
    def load_env(env_path: str = '.env') -> None:
        if not os.path.exists(env_path):
            raise FileNotFoundError(f".env file not found: {env_path}")
        load_dotenv(env_path)
        required_vars = ["OPENAI_API_KEY", "GOOGLE_API_KEY", "DEFAULT_LLM_PROVIDER", "LOG_LEVEL"]
        missing = [var for var in required_vars if os.getenv(var) is None]
        if missing:
            raise EnvironmentError(f"Missing required env variables: {', '.join(missing)}")
