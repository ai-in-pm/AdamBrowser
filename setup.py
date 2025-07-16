"""
Setup script for Adam Browser

Provides installation and setup utilities for the Adam Browser
autonomous AI agent browser application.
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path
from typing import List, Optional
import argparse
from loguru import logger


class AdamBrowserSetup:
    """Setup utility for Adam Browser."""
    
    def __init__(self):
        """Initialize setup utility."""
        self.project_root = Path(__file__).parent
        self.python_exe = sys.executable
        
    def check_python_version(self) -> bool:
        """Check if Python version is compatible."""
        if sys.version_info < (3, 11):
            logger.error("Python 3.11 or higher is required")
            logger.info(f"Current version: {sys.version}")
            return False
        
        logger.info(f"Python version OK: {sys.version}")
        return True
    
    def install_dependencies(self, dev: bool = False) -> bool:
        """
        Install Python dependencies.
        
        Args:
            dev: Install development dependencies
            
        Returns:
            bool: True if installation successful
        """
        try:
            logger.info("Installing Python dependencies...")
            
            # Base requirements
            requirements_file = self.project_root / "requirements.txt"
            if not requirements_file.exists():
                logger.error("requirements.txt not found")
                return False
            
            cmd = [self.python_exe, "-m", "pip", "install", "-r", str(requirements_file)]
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode != 0:
                logger.error(f"Failed to install dependencies: {result.stderr}")
                return False
            
            # Development dependencies
            if dev:
                dev_deps = [
                    "pytest>=7.4.0",
                    "pytest-asyncio>=0.21.0", 
                    "black>=23.11.0",
                    "flake8>=6.1.0",
                    "mypy>=1.7.0",
                    "pre-commit>=3.0.0"
                ]
                
                cmd = [self.python_exe, "-m", "pip", "install"] + dev_deps
                result = subprocess.run(cmd, capture_output=True, text=True)
                
                if result.returncode != 0:
                    logger.warning(f"Some dev dependencies failed to install: {result.stderr}")
            
            logger.info("Dependencies installed successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to install dependencies: {e}")
            return False
    
    def install_playwright_browsers(self) -> bool:
        """Install Playwright browsers."""
        try:
            logger.info("Installing Playwright browsers...")
            
            # Install Playwright browsers
            cmd = [self.python_exe, "-m", "playwright", "install", "chromium"]
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode != 0:
                logger.error(f"Failed to install Playwright browsers: {result.stderr}")
                return False
            
            logger.info("Playwright browsers installed successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to install Playwright browsers: {e}")
            return False
    
    def setup_bert_model(self) -> bool:
        """Setup BERT model for local NLP processing."""
        try:
            bert_dir = self.project_root / "bert-base-uncased-mrpc"
            
            if bert_dir.exists():
                logger.info("BERT model directory already exists")
                return True
            
            logger.info("Setting up BERT model...")
            
            # Create BERT model directory structure
            bert_dir.mkdir(exist_ok=True)
            model_dir = bert_dir / "bert-base-uncased-mrpc"
            model_dir.mkdir(exist_ok=True)
            
            # Create a placeholder config (in production, you'd download the actual model)
            config_content = '''{{
  "architectures": ["BertForSequenceClassification"],
  "attention_probs_dropout_prob": 0.1,
  "hidden_act": "gelu",
  "hidden_dropout_prob": 0.1,
  "hidden_size": 768,
  "initializer_range": 0.02,
  "intermediate_size": 3072,
  "max_position_embeddings": 512,
  "model_type": "bert",
  "num_attention_heads": 12,
  "num_hidden_layers": 12,
  "pad_token_id": 0,
  "type_vocab_size": 2,
  "vocab_size": 30522
}}'''
            
            config_path = model_dir / "config.json"
            with open(config_path, 'w') as f:
                f.write(config_content)
            
            logger.info("BERT model setup complete (placeholder)")
            logger.warning("Note: This is a placeholder setup. For full functionality,")
            logger.warning("download the actual BERT model files to the bert-base-uncased-mrpc directory")
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to setup BERT model: {e}")
            return False
    
    def setup_database(self) -> bool:
        """Setup database directories and initial schema."""
        try:
            logger.info("Setting up database...")
            
            # Create database directories
            db_dir = self.project_root / "adam.browser.database"
            db_dir.mkdir(exist_ok=True)
            
            data_dir = db_dir / "data"
            data_dir.mkdir(exist_ok=True)
            
            schema_dir = db_dir / "schema"
            schema_dir.mkdir(exist_ok=True)
            
            layouts_dir = db_dir / "schema.layouts"
            layouts_dir.mkdir(exist_ok=True)
            
            # Create logs directory
            logs_dir = self.project_root / "logs"
            logs_dir.mkdir(exist_ok=True)
            
            # Create screenshots directory
            screenshots_dir = self.project_root / "screenshots"
            screenshots_dir.mkdir(exist_ok=True)
            
            logger.info("Database directories created")
            return True
            
        except Exception as e:
            logger.error(f"Failed to setup database: {e}")
            return False
    
    def run_tests(self) -> bool:
        """Run basic tests to verify installation."""
        try:
            logger.info("Running basic tests...")
            
            test_file = self.project_root / "tests" / "test_basic.py"
            if not test_file.exists():
                logger.warning("Test file not found, skipping tests")
                return True
            
            cmd = [self.python_exe, "-m", "pytest", str(test_file), "-v"]
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                logger.info("All tests passed")
                return True
            else:
                logger.warning("Some tests failed:")
                logger.warning(result.stdout)
                return False
                
        except Exception as e:
            logger.error(f"Failed to run tests: {e}")
            return False
    
    def create_desktop_shortcut(self) -> bool:
        """Create desktop shortcut (Windows only)."""
        try:
            if sys.platform != "win32":
                logger.info("Desktop shortcut creation only supported on Windows")
                return True
            
            logger.info("Creating desktop shortcut...")
            
            import winshell
            from win32com.client import Dispatch
            
            desktop = winshell.desktop()
            shortcut_path = os.path.join(desktop, "Adam Browser.lnk")
            
            shell = Dispatch('WScript.Shell')
            shortcut = shell.CreateShortCut(shortcut_path)
            shortcut.Targetpath = str(self.project_root / "main.py")
            shortcut.Arguments = ""
            shortcut.WorkingDirectory = str(self.project_root)
            shortcut.IconLocation = str(self.project_root / "headico.png")
            shortcut.save()
            
            logger.info(f"Desktop shortcut created: {shortcut_path}")
            return True
            
        except ImportError:
            logger.warning("winshell not available, skipping desktop shortcut")
            return True
        except Exception as e:
            logger.error(f"Failed to create desktop shortcut: {e}")
            return False
    
    def full_setup(self, dev: bool = False, skip_tests: bool = False) -> bool:
        """
        Run complete setup process.
        
        Args:
            dev: Install development dependencies
            skip_tests: Skip running tests
            
        Returns:
            bool: True if setup successful
        """
        logger.info("Starting Adam Browser setup...")
        
        steps = [
            ("Checking Python version", self.check_python_version),
            ("Installing dependencies", lambda: self.install_dependencies(dev)),
            ("Installing Playwright browsers", self.install_playwright_browsers),
            ("Setting up BERT model", self.setup_bert_model),
            ("Setting up database", self.setup_database),
        ]
        
        if not skip_tests:
            steps.append(("Running tests", self.run_tests))
        
        steps.append(("Creating desktop shortcut", self.create_desktop_shortcut))
        
        for step_name, step_func in steps:
            logger.info(f"Step: {step_name}")
            if not step_func():
                logger.error(f"Setup failed at step: {step_name}")
                return False
        
        logger.info("✅ Adam Browser setup completed successfully!")
        logger.info("You can now run the application with: python main.py")
        
        return True


def main():
    """Main entry point for setup script."""
    parser = argparse.ArgumentParser(description="Adam Browser Setup Utility")
    parser.add_argument("--dev", action="store_true", help="Install development dependencies")
    parser.add_argument("--skip-tests", action="store_true", help="Skip running tests")
    parser.add_argument("--deps-only", action="store_true", help="Install dependencies only")
    parser.add_argument("--browsers-only", action="store_true", help="Install Playwright browsers only")
    parser.add_argument("--test-only", action="store_true", help="Run tests only")
    
    args = parser.parse_args()
    
    # Configure logging
    logger.remove()
    logger.add(
        sys.stderr,
        format="<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | <level>{message}</level>",
        level="INFO"
    )
    
    setup = AdamBrowserSetup()
    
    try:
        if args.deps_only:
            success = setup.install_dependencies(args.dev)
        elif args.browsers_only:
            success = setup.install_playwright_browsers()
        elif args.test_only:
            success = setup.run_tests()
        else:
            success = setup.full_setup(args.dev, args.skip_tests)
        
        return 0 if success else 1
        
    except KeyboardInterrupt:
        logger.info("Setup interrupted by user")
        return 1
    except Exception as e:
        logger.error(f"Setup failed with error: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
