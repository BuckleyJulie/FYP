# chatbot/__init__.py

from .gpt import get_script_response
from .scripts import get_script

__all__ = ["get_script_response", "get_script"]
