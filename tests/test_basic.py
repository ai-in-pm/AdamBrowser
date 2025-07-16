"""
Basic tests for Adam Browser

Tests core functionality and module imports to ensure
the application is properly configured and functional.
"""

import sys
import os
import pytest
import asyncio
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


class TestImports:
    """Test that all modules can be imported correctly."""
    
    def test_import_main_module(self):
        """Test importing the main adam_browser module."""
        import adam_browser
        assert adam_browser.__version__ == "1.0.0"
    
    def test_import_config(self):
        """Test importing configuration module."""
        from adam_browser.config import config, Config
        assert config is not None
        assert isinstance(config, Config)
    
    def test_import_agent(self):
        """Test importing agent modules."""
        from adam_browser.agent import AdamAgent, IntentClassifier
        assert AdamAgent is not None
        assert IntentClassifier is not None
    
    def test_import_browser(self):
        """Test importing browser modules."""
        from adam_browser.browser import BrowserManager
        assert BrowserManager is not None
    
    def test_import_database(self):
        """Test importing database modules."""
        from adam_browser.database import DatabaseManager
        assert DatabaseManager is not None
    
    def test_import_security(self):
        """Test importing security modules."""
        from adam_browser.security import SecurityVault
        assert SecurityVault is not None
    
    def test_import_gui(self):
        """Test importing GUI modules."""
        try:
            from adam_browser.gui import AdamMainWindow
            assert AdamMainWindow is not None
        except ImportError as e:
            # wxPython might not be available in CI
            if "wx" in str(e):
                pytest.skip("wxPython not available")
            else:
                raise


class TestConfiguration:
    """Test configuration loading and validation."""
    
    def test_config_loading(self):
        """Test that configuration loads without errors."""
        from adam_browser.config import Config
        
        # Create a test config
        test_config = Config()
        assert test_config.app_name == "Adam Browser"
        assert test_config.version == "1.0.0"
    
    def test_config_sections(self):
        """Test that all config sections are present."""
        from adam_browser.config import config
        
        assert hasattr(config, 'browser')
        assert hasattr(config, 'ai')
        assert hasattr(config, 'database')
        assert hasattr(config, 'security')
        assert hasattr(config, 'gui')
        assert hasattr(config, 'automation')
    
    def test_browser_config(self):
        """Test browser configuration."""
        from adam_browser.config import config
        
        assert config.browser.default_browser in ['chromium', 'firefox', 'webkit']
        assert config.browser.timeout > 0
        assert config.browser.viewport_width > 0
        assert config.browser.viewport_height > 0


class TestDependencies:
    """Test that required dependencies are available."""
    
    def test_playwright_available(self):
        """Test that Playwright is available."""
        try:
            import playwright
            assert playwright is not None
        except ImportError:
            pytest.fail("Playwright is not installed")
    
    def test_torch_available(self):
        """Test that PyTorch is available."""
        try:
            import torch
            assert torch is not None
        except ImportError:
            pytest.skip("PyTorch not available - using fallback mode")
    
    def test_transformers_available(self):
        """Test that Transformers is available."""
        try:
            import transformers
            assert transformers is not None
        except ImportError:
            pytest.skip("Transformers not available - using fallback mode")
    
    def test_sqlite_available(self):
        """Test that SQLite is available."""
        import sqlite3
        assert sqlite3 is not None
    
    def test_cryptography_available(self):
        """Test that cryptography is available."""
        import cryptography
        assert cryptography is not None


class TestAsyncComponents:
    """Test async components and functionality."""
    
    @pytest.mark.asyncio
    async def test_database_manager_init(self):
        """Test database manager initialization."""
        from adam_browser.database import DatabaseManager
        
        db_manager = DatabaseManager()
        assert db_manager is not None
        
        # Test initialization (should not fail)
        try:
            success = await db_manager.initialize()
            assert isinstance(success, bool)
        except Exception as e:
            pytest.fail(f"Database manager initialization failed: {e}")
    
    @pytest.mark.asyncio
    async def test_security_vault_init(self):
        """Test security vault initialization."""
        from adam_browser.security import SecurityVault
        
        vault = SecurityVault()
        assert vault is not None
        
        # Test initialization
        try:
            success = await vault.initialize()
            assert isinstance(success, bool)
        except Exception as e:
            pytest.fail(f"Security vault initialization failed: {e}")
    
    @pytest.mark.asyncio
    async def test_intent_classifier_init(self):
        """Test intent classifier initialization."""
        from adam_browser.agent import IntentClassifier
        
        classifier = IntentClassifier()
        assert classifier is not None
        
        # Test initialization (may fail without model files)
        try:
            success = await classifier.initialize()
            assert isinstance(success, bool)
        except Exception:
            # Expected if BERT model files are not available
            pass


class TestFileStructure:
    """Test that required files and directories exist."""
    
    def test_config_file_exists(self):
        """Test that configuration file exists."""
        config_path = project_root / "adam.config.toml"
        assert config_path.exists(), "adam.config.toml not found"
    
    def test_icon_file_exists(self):
        """Test that icon file exists."""
        icon_path = project_root / "headico.png"
        assert icon_path.exists(), "headico.png not found"
    
    def test_database_directory_exists(self):
        """Test that database directory exists."""
        db_dir = project_root / "adam.browser.database"
        assert db_dir.exists(), "adam.browser.database directory not found"
    
    def test_bert_directory_exists(self):
        """Test that BERT model directory exists."""
        bert_dir = project_root / "bert-base-uncased-mrpc"
        assert bert_dir.exists(), "bert-base-uncased-mrpc directory not found"
    
    def test_requirements_file_exists(self):
        """Test that requirements file exists."""
        req_path = project_root / "requirements.txt"
        assert req_path.exists(), "requirements.txt not found"
    
    def test_readme_file_exists(self):
        """Test that README file exists."""
        readme_path = project_root / "README.md"
        assert readme_path.exists(), "README.md not found"


class TestBasicFunctionality:
    """Test basic functionality without full initialization."""
    
    def test_intent_classification_patterns(self):
        """Test intent classification patterns."""
        from adam_browser.agent.intent_classifier import IntentClassifier, IntentType
        
        classifier = IntentClassifier()
        
        # Test pattern matching (without BERT model)
        test_commands = [
            ("go to google.com", IntentType.NAVIGATE),
            ("search for python", IntentType.SEARCH),
            ("click the button", IntentType.CLICK),
            ("type hello world", IntentType.TYPE),
            ("scroll down", IntentType.SCROLL),
        ]
        
        for command, expected_intent in test_commands:
            intent, confidence = classifier._pattern_classify(command.lower())
            assert intent == expected_intent, f"Failed for command: {command}"
            assert confidence > 0, f"No confidence for command: {command}"
    
    def test_parameter_extraction(self):
        """Test parameter extraction from commands."""
        from adam_browser.agent.intent_classifier import IntentClassifier, IntentType
        
        classifier = IntentClassifier()
        
        # Test navigation parameter extraction
        params = classifier._extract_parameters("go to google.com", IntentType.NAVIGATE)
        assert 'target' in params
        assert 'google.com' in params['target']
        
        # Test search parameter extraction
        params = classifier._extract_parameters("search for python tutorials", IntentType.SEARCH)
        assert 'query' in params
        assert params['query'] == "python tutorials"
    
    def test_config_validation(self):
        """Test configuration validation."""
        from adam_browser.config import config
        
        # Test that config loads without errors
        assert config.app_name is not None
        assert config.version is not None
        assert config.browser is not None
        assert config.ai is not None


if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v"])
