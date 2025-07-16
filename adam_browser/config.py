"""
Configuration management for Adam Browser.

Handles loading and validation of configuration from adam.config.toml
with support for environment variable overrides and runtime updates.
"""

import os
import toml
from pathlib import Path
from typing import Dict, Any, Optional
from dataclasses import dataclass, field
from loguru import logger


@dataclass
class BrowserConfig:
    """Browser-specific configuration."""
    default_browser: str = "chromium"
    browser_path: str = "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe"
    headless: bool = False
    devtools: bool = False
    slow_mo: int = 0
    timeout: int = 30000
    viewport_width: int = 1920
    viewport_height: int = 1080
    user_agent: str = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"


@dataclass
class AIConfig:
    """AI/NLP configuration."""
    model_path: str = "./bert-base-uncased-mrpc/bert-base-uncased-mrpc"
    use_local_model: bool = True
    fallback_to_api: bool = False
    confidence_threshold: float = 0.7
    max_tokens: int = 512


@dataclass
class DatabaseConfig:
    """Database configuration."""
    db_path: str = "./adam.browser.database/adam.db"
    log_db_path: str = "./adam.browser.database/logs.db"
    backup_enabled: bool = True
    backup_interval: int = 3600
    max_log_entries: int = 100000


@dataclass
class SecurityConfig:
    """Security and encryption configuration."""
    encrypt_credentials: bool = True
    vault_path: str = "./adam.browser.database/vault.enc"
    session_timeout: int = 3600
    auto_lock: bool = True
    master_password_required: bool = True


@dataclass
class GUIConfig:
    """GUI configuration."""
    theme: str = "default"
    window_width: int = 1200
    window_height: int = 800
    minimize_to_tray: bool = True
    show_splash: bool = True
    auto_start: bool = False


@dataclass
class AutomationConfig:
    """Automation behavior configuration."""
    scroll_speed: int = 500
    click_delay: int = 100
    type_delay: int = 50
    screenshot_interval: int = 10
    screenshot_path: str = "./screenshots"


class Config:
    """
    Main configuration class for Adam Browser.
    
    Loads configuration from adam.config.toml and provides
    structured access to all settings with validation.
    """
    
    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize configuration.
        
        Args:
            config_path: Path to configuration file. Defaults to adam.config.toml
        """
        self.config_path = config_path or "adam.config.toml"
        self._config_data: Dict[str, Any] = {}
        
        # Configuration sections
        self.browser = BrowserConfig()
        self.ai = AIConfig()
        self.database = DatabaseConfig()
        self.security = SecurityConfig()
        self.gui = GUIConfig()
        self.automation = AutomationConfig()
        
        # General settings
        self.app_name = "Adam Browser"
        self.version = "1.0.0"
        self.debug_mode = False
        self.log_level = "INFO"
        self.offline_mode = False
        self.telemetry_enabled = False
        
        self.load_config()
    
    def load_config(self) -> None:
        """Load configuration from TOML file."""
        try:
            if os.path.exists(self.config_path):
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    self._config_data = toml.load(f)
                logger.info(f"Loaded configuration from {self.config_path}")
            else:
                logger.warning(f"Configuration file {self.config_path} not found, using defaults")
                self._create_default_config()
                return
            
            self._apply_config()
            self._apply_env_overrides()
            self._validate_config()
            
        except Exception as e:
            logger.error(f"Failed to load configuration: {e}")
            logger.info("Using default configuration")
    
    def _apply_config(self) -> None:
        """Apply loaded configuration to dataclass instances."""
        # General settings
        general = self._config_data.get('general', {})
        self.app_name = general.get('app_name', self.app_name)
        self.version = general.get('version', self.version)
        self.debug_mode = general.get('debug_mode', self.debug_mode)
        self.log_level = general.get('log_level', self.log_level)
        self.offline_mode = general.get('offline_mode', self.offline_mode)
        self.telemetry_enabled = general.get('telemetry_enabled', self.telemetry_enabled)
        
        # Browser configuration
        browser_config = self._config_data.get('browser', {})
        for key, value in browser_config.items():
            if hasattr(self.browser, key):
                setattr(self.browser, key, value)
        
        # AI configuration
        ai_config = self._config_data.get('ai', {})
        for key, value in ai_config.items():
            if hasattr(self.ai, key):
                setattr(self.ai, key, value)
        
        # Database configuration
        db_config = self._config_data.get('database', {})
        for key, value in db_config.items():
            if hasattr(self.database, key):
                setattr(self.database, key, value)
        
        # Security configuration
        security_config = self._config_data.get('security', {})
        for key, value in security_config.items():
            if hasattr(self.security, key):
                setattr(self.security, key, value)
        
        # GUI configuration
        gui_config = self._config_data.get('gui', {})
        for key, value in gui_config.items():
            if hasattr(self.gui, key):
                setattr(self.gui, key, value)
        
        # Automation configuration
        automation_config = self._config_data.get('automation', {})
        for key, value in automation_config.items():
            if hasattr(self.automation, key):
                setattr(self.automation, key, value)
    
    def _apply_env_overrides(self) -> None:
        """Apply environment variable overrides."""
        # Support for common environment variables
        env_mappings = {
            'ADAM_DEBUG': ('debug_mode', bool),
            'ADAM_LOG_LEVEL': ('log_level', str),
            'ADAM_OFFLINE': ('offline_mode', bool),
            'ADAM_BROWSER_PATH': ('browser.browser_path', str),
            'ADAM_HEADLESS': ('browser.headless', bool),
            'ADAM_MODEL_PATH': ('ai.model_path', str),
        }
        
        for env_var, (config_path, config_type) in env_mappings.items():
            env_value = os.getenv(env_var)
            if env_value is not None:
                try:
                    if config_type == bool:
                        value = env_value.lower() in ('true', '1', 'yes', 'on')
                    else:
                        value = config_type(env_value)
                    
                    # Set the value using dot notation
                    self._set_nested_value(config_path, value)
                    logger.debug(f"Applied environment override: {env_var}={value}")
                except ValueError as e:
                    logger.warning(f"Invalid environment variable {env_var}: {e}")
    
    def _set_nested_value(self, path: str, value: Any) -> None:
        """Set a nested configuration value using dot notation."""
        parts = path.split('.')
        obj = self
        
        for part in parts[:-1]:
            obj = getattr(obj, part)
        
        setattr(obj, parts[-1], value)
    
    def _validate_config(self) -> None:
        """Validate configuration values."""
        # Validate paths exist
        paths_to_check = [
            self.ai.model_path,
            os.path.dirname(self.database.db_path),
            os.path.dirname(self.automation.screenshot_path),
        ]
        
        for path in paths_to_check:
            if path and not os.path.exists(path):
                logger.warning(f"Path does not exist: {path}")
        
        # Validate browser path
        if self.browser.browser_path and not os.path.exists(self.browser.browser_path):
            logger.warning(f"Browser path does not exist: {self.browser.browser_path}")
        
        # Validate numeric ranges
        if not 0 <= self.ai.confidence_threshold <= 1:
            logger.warning("AI confidence threshold should be between 0 and 1")
        
        if self.browser.timeout < 1000:
            logger.warning("Browser timeout should be at least 1000ms")
    
    def _create_default_config(self) -> None:
        """Create default configuration file."""
        try:
            # Create default config content (this would be the full TOML content)
            default_config = """# Adam Browser Configuration File - Generated Defaults
[general]
app_name = "Adam Browser"
version = "1.0.0"
debug_mode = false
log_level = "INFO"
offline_mode = false
telemetry_enabled = false

[browser]
default_browser = "chromium"
browser_path = "C:\\\\Program Files\\\\Google\\\\Chrome\\\\Application\\\\chrome.exe"
headless = false
devtools = false
timeout = 30000

[ai]
model_path = "./bert-base-uncased-mrpc/bert-base-uncased-mrpc"
use_local_model = true
confidence_threshold = 0.7
"""
            
            with open(self.config_path, 'w', encoding='utf-8') as f:
                f.write(default_config)
            logger.info(f"Created default configuration file: {self.config_path}")
            
        except Exception as e:
            logger.error(f"Failed to create default configuration: {e}")
    
    def save_config(self) -> None:
        """Save current configuration to file."""
        try:
            # Convert dataclasses back to dict format
            config_dict = {
                'general': {
                    'app_name': self.app_name,
                    'version': self.version,
                    'debug_mode': self.debug_mode,
                    'log_level': self.log_level,
                    'offline_mode': self.offline_mode,
                    'telemetry_enabled': self.telemetry_enabled,
                },
                'browser': self.browser.__dict__,
                'ai': self.ai.__dict__,
                'database': self.database.__dict__,
                'security': self.security.__dict__,
                'gui': self.gui.__dict__,
                'automation': self.automation.__dict__,
            }
            
            with open(self.config_path, 'w', encoding='utf-8') as f:
                toml.dump(config_dict, f)
            logger.info(f"Saved configuration to {self.config_path}")
            
        except Exception as e:
            logger.error(f"Failed to save configuration: {e}")
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get a configuration value using dot notation."""
        try:
            parts = key.split('.')
            value = self._config_data
            
            for part in parts:
                value = value[part]
            
            return value
        except (KeyError, TypeError):
            return default
    
    def reload(self) -> None:
        """Reload configuration from file."""
        logger.info("Reloading configuration...")
        self.load_config()


# Global configuration instance
config = Config()
