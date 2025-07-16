"""
Database Manager for Adam Browser

Manages SQLite databases for logging, metrics, and user data with
automatic schema creation and migration support.
"""

import sqlite3
import asyncio
import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from pathlib import Path
from contextlib import asynccontextmanager
import aiosqlite
from loguru import logger

from ..config import config


class DatabaseManager:
    """
    Manages SQLite databases for Adam Browser.
    
    Handles command logging, metrics collection, user preferences,
    and session data with automatic schema management.
    """
    
    def __init__(self):
        """Initialize the database manager."""
        self.main_db_path = config.database.db_path
        self.log_db_path = config.database.log_db_path
        
        # Ensure database directories exist
        os.makedirs(os.path.dirname(self.main_db_path), exist_ok=True)
        os.makedirs(os.path.dirname(self.log_db_path), exist_ok=True)
        
        self.is_initialized = False
        
        # Database schemas
        self.main_schema = {
            'user_preferences': '''
                CREATE TABLE IF NOT EXISTS user_preferences (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    key TEXT UNIQUE NOT NULL,
                    value TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''',
            'sessions': '''
                CREATE TABLE IF NOT EXISTS sessions (
                    id TEXT PRIMARY KEY,
                    start_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    end_time TIMESTAMP,
                    commands_count INTEGER DEFAULT 0,
                    success_count INTEGER DEFAULT 0,
                    error_count INTEGER DEFAULT 0,
                    total_execution_time REAL DEFAULT 0.0,
                    metadata TEXT
                )
            ''',
            'bookmarks': '''
                CREATE TABLE IF NOT EXISTS bookmarks (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    url TEXT NOT NULL,
                    title TEXT,
                    description TEXT,
                    tags TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_visited TIMESTAMP
                )
            ''',
            'credentials': '''
                CREATE TABLE IF NOT EXISTS credentials (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    site_url TEXT NOT NULL,
                    username TEXT,
                    encrypted_data TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_used TIMESTAMP
                )
            '''
        }
        
        self.log_schema = {
            'command_logs': '''
                CREATE TABLE IF NOT EXISTS command_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    command_id TEXT UNIQUE NOT NULL,
                    session_id TEXT,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    command TEXT NOT NULL,
                    intent TEXT,
                    parameters TEXT,
                    execution_time REAL,
                    success BOOLEAN,
                    error_message TEXT,
                    url TEXT,
                    page_title TEXT,
                    screenshot_path TEXT
                )
            ''',
            'action_logs': '''
                CREATE TABLE IF NOT EXISTS action_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    command_id TEXT,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    action_type TEXT NOT NULL,
                    target_element TEXT,
                    action_data TEXT,
                    success BOOLEAN,
                    execution_time REAL,
                    error_message TEXT
                )
            ''',
            'performance_metrics': '''
                CREATE TABLE IF NOT EXISTS performance_metrics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    metric_type TEXT NOT NULL,
                    metric_name TEXT NOT NULL,
                    metric_value REAL NOT NULL,
                    metadata TEXT
                )
            ''',
            'error_logs': '''
                CREATE TABLE IF NOT EXISTS error_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    error_type TEXT NOT NULL,
                    error_message TEXT NOT NULL,
                    stack_trace TEXT,
                    context TEXT,
                    command_id TEXT
                )
            '''
        }
        
        logger.info("Database manager initialized")
    
    async def initialize(self) -> bool:
        """
        Initialize databases and create schemas.
        
        Returns:
            bool: True if initialization successful
        """
        try:
            logger.info("Initializing databases...")
            
            # Initialize main database
            await self._initialize_database(self.main_db_path, self.main_schema)
            
            # Initialize log database
            await self._initialize_database(self.log_db_path, self.log_schema)
            
            # Create indexes for performance
            await self._create_indexes()
            
            # Clean up old logs if configured
            if config.database.max_log_entries > 0:
                await self._cleanup_old_logs()
            
            self.is_initialized = True
            logger.info("Database initialization complete")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize databases: {e}")
            return False
    
    async def _initialize_database(self, db_path: str, schema: Dict[str, str]) -> None:
        """Initialize a database with schema."""
        async with aiosqlite.connect(db_path) as db:
            # Enable foreign keys
            await db.execute("PRAGMA foreign_keys = ON")
            
            # Create tables
            for table_name, create_sql in schema.items():
                await db.execute(create_sql)
                logger.debug(f"Created table: {table_name}")
            
            await db.commit()
    
    async def _create_indexes(self) -> None:
        """Create database indexes for performance."""
        indexes = [
            # Log database indexes
            ("idx_command_logs_timestamp", "command_logs", "timestamp"),
            ("idx_command_logs_session", "command_logs", "session_id"),
            ("idx_command_logs_command_id", "command_logs", "command_id"),
            ("idx_action_logs_timestamp", "action_logs", "timestamp"),
            ("idx_action_logs_command", "action_logs", "command_id"),
            ("idx_performance_timestamp", "performance_metrics", "timestamp"),
            ("idx_error_logs_timestamp", "error_logs", "timestamp"),
        ]
        
        async with aiosqlite.connect(self.log_db_path) as db:
            for index_name, table_name, column_name in indexes:
                try:
                    await db.execute(f"CREATE INDEX IF NOT EXISTS {index_name} ON {table_name}({column_name})")
                except Exception as e:
                    logger.warning(f"Failed to create index {index_name}: {e}")
            
            await db.commit()
    
    async def log_command(self, command_id: str, command: str, intent: Dict[str, Any], 
                         result: Dict[str, Any], execution_time: float, 
                         session_id: Optional[str] = None) -> bool:
        """
        Log a command execution.
        
        Args:
            command_id: Unique command identifier
            command: Original command text
            intent: Intent classification result
            result: Execution result
            execution_time: Time taken to execute
            session_id: Optional session identifier
            
        Returns:
            bool: True if logging successful
        """
        try:
            async with aiosqlite.connect(self.log_db_path) as db:
                await db.execute('''
                    INSERT INTO command_logs (
                        command_id, session_id, command, intent, parameters,
                        execution_time, success, error_message, url, page_title
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    command_id,
                    session_id,
                    command,
                    intent.get('intent', ''),
                    json.dumps(intent.get('parameters', {})),
                    execution_time,
                    result.get('success', False),
                    result.get('error', ''),
                    result.get('url', ''),
                    result.get('page_title', '')
                ))
                
                await db.commit()
                return True
                
        except Exception as e:
            logger.error(f"Failed to log command: {e}")
            return False
    
    async def log_action(self, command_id: str, action_type: str, target_element: str,
                        action_data: Dict[str, Any], success: bool, 
                        execution_time: float, error_message: str = "") -> bool:
        """
        Log an individual action within a command.
        
        Args:
            command_id: Associated command ID
            action_type: Type of action (click, type, scroll, etc.)
            target_element: Target element selector or description
            action_data: Additional action data
            success: Whether action succeeded
            execution_time: Time taken for action
            error_message: Error message if failed
            
        Returns:
            bool: True if logging successful
        """
        try:
            async with aiosqlite.connect(self.log_db_path) as db:
                await db.execute('''
                    INSERT INTO action_logs (
                        command_id, action_type, target_element, action_data,
                        success, execution_time, error_message
                    ) VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (
                    command_id,
                    action_type,
                    target_element,
                    json.dumps(action_data),
                    success,
                    execution_time,
                    error_message
                ))
                
                await db.commit()
                return True
                
        except Exception as e:
            logger.error(f"Failed to log action: {e}")
            return False
    
    async def log_error(self, command_id: str, command: str, error: str, 
                       execution_time: float) -> bool:
        """
        Log a command error.
        
        Args:
            command_id: Command identifier
            command: Original command
            error: Error message
            execution_time: Time before error occurred
            
        Returns:
            bool: True if logging successful
        """
        try:
            async with aiosqlite.connect(self.log_db_path) as db:
                await db.execute('''
                    INSERT INTO error_logs (
                        command_id, error_type, error_message, context
                    ) VALUES (?, ?, ?, ?)
                ''', (
                    command_id,
                    "command_execution",
                    error,
                    json.dumps({'command': command, 'execution_time': execution_time})
                ))
                
                await db.commit()
                return True
                
        except Exception as e:
            logger.error(f"Failed to log error: {e}")
            return False
    
    async def log_metric(self, metric_type: str, metric_name: str, 
                        metric_value: float, metadata: Optional[Dict[str, Any]] = None) -> bool:
        """
        Log a performance metric.
        
        Args:
            metric_type: Type of metric (performance, usage, etc.)
            metric_name: Name of the metric
            metric_value: Numeric value
            metadata: Optional additional data
            
        Returns:
            bool: True if logging successful
        """
        try:
            async with aiosqlite.connect(self.log_db_path) as db:
                await db.execute('''
                    INSERT INTO performance_metrics (
                        metric_type, metric_name, metric_value, metadata
                    ) VALUES (?, ?, ?, ?)
                ''', (
                    metric_type,
                    metric_name,
                    metric_value,
                    json.dumps(metadata) if metadata else None
                ))
                
                await db.commit()
                return True
                
        except Exception as e:
            logger.error(f"Failed to log metric: {e}")
            return False
    
    async def get_command_history(self, limit: int = 100, 
                                 session_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Get command history.
        
        Args:
            limit: Maximum number of commands to return
            session_id: Optional session filter
            
        Returns:
            List of command records
        """
        try:
            async with aiosqlite.connect(self.log_db_path) as db:
                db.row_factory = aiosqlite.Row
                
                if session_id:
                    cursor = await db.execute('''
                        SELECT * FROM command_logs 
                        WHERE session_id = ?
                        ORDER BY timestamp DESC 
                        LIMIT ?
                    ''', (session_id, limit))
                else:
                    cursor = await db.execute('''
                        SELECT * FROM command_logs 
                        ORDER BY timestamp DESC 
                        LIMIT ?
                    ''', (limit,))
                
                rows = await cursor.fetchall()
                return [dict(row) for row in rows]
                
        except Exception as e:
            logger.error(f"Failed to get command history: {e}")
            return []
    
    async def get_metrics_summary(self, hours: int = 24) -> Dict[str, Any]:
        """
        Get metrics summary for the specified time period.
        
        Args:
            hours: Number of hours to look back
            
        Returns:
            Dict containing metrics summary
        """
        try:
            since = datetime.now() - timedelta(hours=hours)
            
            async with aiosqlite.connect(self.log_db_path) as db:
                # Command statistics
                cursor = await db.execute('''
                    SELECT 
                        COUNT(*) as total_commands,
                        SUM(CASE WHEN success = 1 THEN 1 ELSE 0 END) as successful_commands,
                        AVG(execution_time) as avg_execution_time,
                        MAX(execution_time) as max_execution_time
                    FROM command_logs 
                    WHERE timestamp > ?
                ''', (since,))
                
                command_stats = await cursor.fetchone()
                
                # Error statistics
                cursor = await db.execute('''
                    SELECT COUNT(*) as error_count
                    FROM error_logs 
                    WHERE timestamp > ?
                ''', (since,))
                
                error_stats = await cursor.fetchone()
                
                return {
                    'period_hours': hours,
                    'total_commands': command_stats[0] if command_stats[0] else 0,
                    'successful_commands': command_stats[1] if command_stats[1] else 0,
                    'failed_commands': (command_stats[0] - command_stats[1]) if command_stats[0] and command_stats[1] else 0,
                    'success_rate': (command_stats[1] / command_stats[0] * 100) if command_stats[0] else 0,
                    'avg_execution_time': command_stats[2] if command_stats[2] else 0,
                    'max_execution_time': command_stats[3] if command_stats[3] else 0,
                    'error_count': error_stats[0] if error_stats[0] else 0,
                }
                
        except Exception as e:
            logger.error(f"Failed to get metrics summary: {e}")
            return {}
    
    async def _cleanup_old_logs(self) -> None:
        """Clean up old log entries based on configuration."""
        try:
            max_entries = config.database.max_log_entries
            
            async with aiosqlite.connect(self.log_db_path) as db:
                # Clean up command logs
                await db.execute('''
                    DELETE FROM command_logs 
                    WHERE id NOT IN (
                        SELECT id FROM command_logs 
                        ORDER BY timestamp DESC 
                        LIMIT ?
                    )
                ''', (max_entries,))
                
                # Clean up action logs (keep only those with valid command_ids)
                await db.execute('''
                    DELETE FROM action_logs 
                    WHERE command_id NOT IN (
                        SELECT command_id FROM command_logs
                    )
                ''')
                
                await db.commit()
                logger.info(f"Cleaned up old log entries (kept {max_entries} commands)")
                
        except Exception as e:
            logger.error(f"Failed to cleanup old logs: {e}")
    
    async def close(self) -> None:
        """Close database connections and cleanup."""
        logger.info("Closing database connections...")
        # SQLite connections are automatically closed when context managers exit
        self.is_initialized = False
