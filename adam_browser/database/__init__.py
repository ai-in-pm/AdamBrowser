"""
Database Module for Adam Browser

Provides SQLite-based data persistence for session logs, command history,
user preferences, and performance metrics.

Components:
- DatabaseManager: Main database interface
- SessionLogger: Command and action logging
- MetricsCollector: Performance metrics storage
- UserPreferences: User settings persistence
"""

from .database_manager import DatabaseManager
from .session_logger import SessionLogger
from .metrics_collector import MetricsCollector
from .user_preferences import UserPreferences

__all__ = [
    "DatabaseManager",
    "SessionLogger",
    "MetricsCollector",
    "UserPreferences",
]
