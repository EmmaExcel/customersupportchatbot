import os
from pathlib import Path

from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parent.parent
ENV_FILE = PROJECT_ROOT / ".env"


def load_environment():
    if ENV_FILE.exists():
        load_dotenv(ENV_FILE)


load_environment()


def get(name, default=None):
    return os.getenv(name, default)
