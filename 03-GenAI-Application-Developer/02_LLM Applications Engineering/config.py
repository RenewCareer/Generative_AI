import os

from dotenv import load_dotenv

# Load variables from .env file
load_dotenv()

def get_required_env(name: str) -> str:
    """Get a required environment variable, raise an error if not found."""
    value = os.getenv(name)

    if value is None:
        raise EnvironmentError(f"Required environment variable '{name}' not found.")
    return value


OPENAI_API_KEY = get_required_env("OPENAI_API_KEY")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4.1-mini")  # Default to gpt-4.1-mini if not set