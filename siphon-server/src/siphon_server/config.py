import tomllib
import os
from pathlib import Path
from dataclasses import dataclass


@dataclass
class Settings:
    default_model: str
    log_level: int
    cache: bool


def load_settings() -> Settings:
    """Load settings with precedence: ENV VARS > config file > defaults"""

    # Defaults (lowest priority)
    config = {"default_model": "gpt-oss:latest", "log_level": 2, "cache": True}

    # Load from config file if it exists
    config_path = Path.home() / ".config" / "siphon" / "config.toml"
    if config_path.exists():
        with open(config_path, "rb") as f:
            file_config = tomllib.load(f)
            config.update(file_config)

    # Override with environment variables (highest priority)
    if "SIPHON_DEFAULT_MODEL" in os.environ:
        config["default_model"] = os.environ["DEFAULT_MODEL"]

    if "SIPHON_LOG_LEVEL" in os.environ:
        config["log_level"] = int(os.environ["LOG_LEVEL"])

    if "SIPHON_CACHE" in os.environ:
        config["cache"] = os.environ["CACHE"].lower() in ("true", "1", "yes")

    return Settings(**config)


# Singleton
settings = load_settings()
