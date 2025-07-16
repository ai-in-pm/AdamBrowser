"""
Adam Browser AI Agent Module

This module contains the core AI agent logic for processing natural language
commands and coordinating browser automation tasks.

Components:
- AdamAgent: Main agent class
- IntentClassifier: NLP-based intent recognition
- CommandProcessor: Command parsing and execution
- ContextManager: Session and context tracking
"""

from .agent import AdamAgent
from .intent_classifier import IntentClassifier
from .command_processor import CommandProcessor
from .context_manager import ContextManager

__all__ = [
    "AdamAgent",
    "IntentClassifier", 
    "CommandProcessor",
    "ContextManager",
]
