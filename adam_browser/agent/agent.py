"""
Main Adam Browser AI Agent

The core agent that processes natural language commands and coordinates
all browser automation activities. Uses BERT for intent classification
and maintains session context for complex multi-step operations.
"""

import asyncio
import time
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass
from enum import Enum
from loguru import logger

from ..config import config
from ..browser import BrowserManager
from ..database import DatabaseManager
from ..security import SecurityVault
from .intent_classifier import IntentClassifier
from .command_processor import CommandProcessor
from .context_manager import ContextManager


class AgentState(Enum):
    """Agent operational states."""
    IDLE = "idle"
    PROCESSING = "processing"
    EXECUTING = "executing"
    WAITING = "waiting"
    ERROR = "error"
    STOPPED = "stopped"


@dataclass
class AgentMetrics:
    """Agent performance metrics."""
    commands_processed: int = 0
    successful_commands: int = 0
    failed_commands: int = 0
    total_execution_time: float = 0.0
    average_response_time: float = 0.0
    uptime: float = 0.0
    last_activity: Optional[float] = None


class AdamAgent:
    """
    Main AI Agent for Adam Browser.
    
    Processes natural language commands and coordinates browser automation
    through specialized modules for different websites and tasks.
    """
    
    def __init__(self):
        """Initialize the Adam Agent."""
        self.state = AgentState.IDLE
        self.metrics = AgentMetrics()
        self.start_time = time.time()
        
        # Core components
        self.browser_manager: Optional[BrowserManager] = None
        self.database_manager: Optional[DatabaseManager] = None
        self.security_vault: Optional[SecurityVault] = None
        self.intent_classifier: Optional[IntentClassifier] = None
        self.command_processor: Optional[CommandProcessor] = None
        self.context_manager: Optional[ContextManager] = None
        
        # Event callbacks
        self.on_state_change: Optional[Callable[[AgentState], None]] = None
        self.on_command_complete: Optional[Callable[[Dict[str, Any]], None]] = None
        self.on_error: Optional[Callable[[Exception], None]] = None
        
        # Command queue for batch processing
        self.command_queue: List[Dict[str, Any]] = []
        self.is_running = False
        
        logger.info("Adam Agent initialized")
    
    async def initialize(self) -> bool:
        """
        Initialize all agent components.
        
        Returns:
            bool: True if initialization successful, False otherwise
        """
        try:
            logger.info("Initializing Adam Agent components...")
            
            # Initialize database first
            self.database_manager = DatabaseManager()
            await self.database_manager.initialize()
            
            # Initialize security vault
            self.security_vault = SecurityVault()
            await self.security_vault.initialize()
            
            # Initialize browser manager
            self.browser_manager = BrowserManager()
            await self.browser_manager.initialize()
            
            # Initialize AI components
            self.intent_classifier = IntentClassifier()
            await self.intent_classifier.initialize()
            
            self.command_processor = CommandProcessor(
                browser_manager=self.browser_manager,
                database_manager=self.database_manager,
                security_vault=self.security_vault
            )
            
            self.context_manager = ContextManager()
            
            logger.info("Adam Agent initialization complete")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize Adam Agent: {e}")
            self.state = AgentState.ERROR
            if self.on_error:
                self.on_error(e)
            return False
    
    async def start(self) -> None:
        """Start the agent and begin processing commands."""
        if not await self.initialize():
            raise RuntimeError("Failed to initialize agent")
        
        self.is_running = True
        self.state = AgentState.IDLE
        self._update_state(AgentState.IDLE)
        
        logger.info("Adam Agent started and ready for commands")
        
        # Start background tasks
        asyncio.create_task(self._process_command_queue())
        asyncio.create_task(self._update_metrics())
    
    async def stop(self) -> None:
        """Stop the agent and cleanup resources."""
        logger.info("Stopping Adam Agent...")
        
        self.is_running = False
        self.state = AgentState.STOPPED
        self._update_state(AgentState.STOPPED)
        
        # Cleanup components
        if self.browser_manager:
            await self.browser_manager.cleanup()
        
        if self.database_manager:
            await self.database_manager.close()
        
        logger.info("Adam Agent stopped")
    
    async def process_command(self, command: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Process a natural language command.
        
        Args:
            command: Natural language command string
            context: Optional context information
            
        Returns:
            Dict containing execution results and metadata
        """
        start_time = time.time()
        command_id = f"cmd_{int(start_time * 1000)}"
        
        try:
            self._update_state(AgentState.PROCESSING)
            
            logger.info(f"Processing command [{command_id}]: {command}")
            
            # Update context
            if context:
                self.context_manager.update_context(context)
            
            # Classify intent
            intent_result = await self.intent_classifier.classify(command)
            logger.debug(f"Intent classification: {intent_result}")
            
            # Add to context
            self.context_manager.add_command(command, intent_result)
            
            # Process command
            self._update_state(AgentState.EXECUTING)
            execution_result = await self.command_processor.execute(
                command=command,
                intent=intent_result,
                context=self.context_manager.get_current_context()
            )
            
            # Calculate metrics
            execution_time = time.time() - start_time
            self.metrics.commands_processed += 1
            self.metrics.total_execution_time += execution_time
            self.metrics.last_activity = time.time()
            
            if execution_result.get('success', False):
                self.metrics.successful_commands += 1
            else:
                self.metrics.failed_commands += 1
            
            # Update average response time
            self.metrics.average_response_time = (
                self.metrics.total_execution_time / self.metrics.commands_processed
            )
            
            # Log to database
            await self.database_manager.log_command(
                command_id=command_id,
                command=command,
                intent=intent_result,
                result=execution_result,
                execution_time=execution_time
            )
            
            result = {
                'command_id': command_id,
                'command': command,
                'intent': intent_result,
                'execution_result': execution_result,
                'execution_time': execution_time,
                'success': execution_result.get('success', False)
            }
            
            # Notify completion
            if self.on_command_complete:
                self.on_command_complete(result)
            
            self._update_state(AgentState.IDLE)
            logger.info(f"Command [{command_id}] completed in {execution_time:.2f}s")
            
            return result
            
        except Exception as e:
            execution_time = time.time() - start_time
            self.metrics.commands_processed += 1
            self.metrics.failed_commands += 1
            self.metrics.total_execution_time += execution_time
            
            error_result = {
                'command_id': command_id,
                'command': command,
                'error': str(e),
                'execution_time': execution_time,
                'success': False
            }
            
            logger.error(f"Command [{command_id}] failed: {e}")
            
            # Log error to database
            await self.database_manager.log_error(
                command_id=command_id,
                command=command,
                error=str(e),
                execution_time=execution_time
            )
            
            self._update_state(AgentState.ERROR)
            if self.on_error:
                self.on_error(e)
            
            return error_result
    
    def queue_command(self, command: str, context: Optional[Dict[str, Any]] = None) -> str:
        """
        Add a command to the processing queue.
        
        Args:
            command: Natural language command
            context: Optional context
            
        Returns:
            str: Command ID for tracking
        """
        command_id = f"queued_{int(time.time() * 1000)}"
        
        self.command_queue.append({
            'id': command_id,
            'command': command,
            'context': context,
            'queued_at': time.time()
        })
        
        logger.debug(f"Command queued [{command_id}]: {command}")
        return command_id
    
    async def _process_command_queue(self) -> None:
        """Background task to process queued commands."""
        while self.is_running:
            if self.command_queue and self.state == AgentState.IDLE:
                queued_command = self.command_queue.pop(0)
                
                try:
                    await self.process_command(
                        command=queued_command['command'],
                        context=queued_command['context']
                    )
                except Exception as e:
                    logger.error(f"Failed to process queued command: {e}")
            
            await asyncio.sleep(0.1)  # Small delay to prevent busy waiting
    
    async def _update_metrics(self) -> None:
        """Background task to update agent metrics."""
        while self.is_running:
            self.metrics.uptime = time.time() - self.start_time
            await asyncio.sleep(1)  # Update every second
    
    def _update_state(self, new_state: AgentState) -> None:
        """Update agent state and notify callbacks."""
        if self.state != new_state:
            old_state = self.state
            self.state = new_state
            
            logger.debug(f"Agent state changed: {old_state.value} -> {new_state.value}")
            
            if self.on_state_change:
                self.on_state_change(new_state)
    
    def get_status(self) -> Dict[str, Any]:
        """Get current agent status and metrics."""
        return {
            'state': self.state.value,
            'metrics': {
                'commands_processed': self.metrics.commands_processed,
                'successful_commands': self.metrics.successful_commands,
                'failed_commands': self.metrics.failed_commands,
                'success_rate': (
                    self.metrics.successful_commands / max(self.metrics.commands_processed, 1) * 100
                ),
                'average_response_time': self.metrics.average_response_time,
                'uptime': self.metrics.uptime,
                'last_activity': self.metrics.last_activity,
            },
            'queue_size': len(self.command_queue),
            'is_running': self.is_running,
            'components': {
                'browser_manager': self.browser_manager is not None,
                'database_manager': self.database_manager is not None,
                'security_vault': self.security_vault is not None,
                'intent_classifier': self.intent_classifier is not None,
                'command_processor': self.command_processor is not None,
                'context_manager': self.context_manager is not None,
            }
        }
    
    def set_callbacks(self, 
                     on_state_change: Optional[Callable[[AgentState], None]] = None,
                     on_command_complete: Optional[Callable[[Dict[str, Any]], None]] = None,
                     on_error: Optional[Callable[[Exception], None]] = None) -> None:
        """Set event callbacks for GUI integration."""
        self.on_state_change = on_state_change
        self.on_command_complete = on_command_complete
        self.on_error = on_error
