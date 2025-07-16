"""
Context Manager for Adam Browser

Manages session context, command history, and state tracking
for intelligent multi-step operations and context-aware responses.
"""

import time
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from collections import deque
from loguru import logger


@dataclass
class CommandContext:
    """Context information for a command."""
    command: str
    intent: Dict[str, Any]
    timestamp: float
    success: bool
    execution_time: float
    url: str = ""
    page_title: str = ""
    parameters: Dict[str, Any] = field(default_factory=dict)


@dataclass
class SessionContext:
    """Overall session context."""
    session_id: str
    start_time: float
    current_url: str = ""
    current_page_title: str = ""
    current_domain: str = ""
    user_preferences: Dict[str, Any] = field(default_factory=dict)
    form_data: Dict[str, Any] = field(default_factory=dict)
    navigation_history: List[str] = field(default_factory=list)
    search_history: List[str] = field(default_factory=list)


class ContextManager:
    """
    Manages execution context and session state for Adam Browser.
    
    Tracks command history, user preferences, form data, and navigation
    patterns to enable intelligent context-aware automation.
    """
    
    def __init__(self, max_history: int = 100):
        """
        Initialize the context manager.
        
        Args:
            max_history: Maximum number of commands to keep in history
        """
        self.max_history = max_history
        
        # Session context
        self.session = SessionContext(
            session_id=f"session_{int(time.time())}",
            start_time=time.time()
        )
        
        # Command history
        self.command_history: deque = deque(maxlen=max_history)
        
        # Context tracking
        self.current_context: Dict[str, Any] = {}
        self.form_context: Dict[str, Any] = {}
        self.navigation_context: Dict[str, Any] = {}
        
        # Pattern recognition
        self.common_patterns: Dict[str, int] = {}
        self.user_preferences: Dict[str, Any] = {}
        
        logger.info(f"Context manager initialized for session: {self.session.session_id}")
    
    def add_command(self, command: str, intent: Dict[str, Any], 
                   success: bool = True, execution_time: float = 0.0,
                   url: str = "", page_title: str = "") -> None:
        """
        Add a command to the context history.
        
        Args:
            command: Original command text
            intent: Intent classification result
            success: Whether command succeeded
            execution_time: Time taken to execute
            url: Current page URL
            page_title: Current page title
        """
        context = CommandContext(
            command=command,
            intent=intent,
            timestamp=time.time(),
            success=success,
            execution_time=execution_time,
            url=url,
            page_title=page_title,
            parameters=intent.get('parameters', {})
        )
        
        self.command_history.append(context)
        
        # Update session context
        self._update_session_context(context)
        
        # Learn from patterns
        self._learn_patterns(context)
        
        logger.debug(f"Added command to context: {command}")
    
    def _update_session_context(self, context: CommandContext) -> None:
        """Update session context based on command."""
        # Update current page info
        if context.url:
            self.session.current_url = context.url
            self.session.current_page_title = context.page_title
            
            # Extract domain
            try:
                from urllib.parse import urlparse
                parsed = urlparse(context.url)
                self.session.current_domain = parsed.netloc
            except Exception:
                pass
            
            # Add to navigation history
            if context.url not in self.session.navigation_history:
                self.session.navigation_history.append(context.url)
                
                # Keep only recent navigation
                if len(self.session.navigation_history) > 20:
                    self.session.navigation_history = self.session.navigation_history[-20:]
        
        # Track search queries
        if context.intent.get('intent') == 'search':
            query = context.parameters.get('query', '')
            if query and query not in self.session.search_history:
                self.session.search_history.append(query)
                
                # Keep only recent searches
                if len(self.session.search_history) > 10:
                    self.session.search_history = self.session.search_history[-10:]
    
    def _learn_patterns(self, context: CommandContext) -> None:
        """Learn from command patterns."""
        intent_type = context.intent.get('intent', '')
        
        # Track common intent patterns
        if intent_type:
            self.common_patterns[intent_type] = self.common_patterns.get(intent_type, 0) + 1
        
        # Learn domain-specific preferences
        if self.session.current_domain:
            domain_key = f"domain_{self.session.current_domain}"
            if domain_key not in self.user_preferences:
                self.user_preferences[domain_key] = {}
            
            # Track successful actions per domain
            if context.success:
                action_key = f"{intent_type}_success"
                self.user_preferences[domain_key][action_key] = (
                    self.user_preferences[domain_key].get(action_key, 0) + 1
                )
    
    def get_current_context(self) -> Dict[str, Any]:
        """
        Get current execution context.
        
        Returns:
            Dict containing current context information
        """
        recent_commands = list(self.command_history)[-5:]  # Last 5 commands
        
        return {
            'session': {
                'session_id': self.session.session_id,
                'start_time': self.session.start_time,
                'duration': time.time() - self.session.start_time,
                'current_url': self.session.current_url,
                'current_page_title': self.session.current_page_title,
                'current_domain': self.session.current_domain,
            },
            'recent_commands': [
                {
                    'command': cmd.command,
                    'intent': cmd.intent.get('intent', ''),
                    'success': cmd.success,
                    'timestamp': cmd.timestamp,
                }
                for cmd in recent_commands
            ],
            'navigation_history': self.session.navigation_history[-5:],
            'search_history': self.session.search_history[-3:],
            'common_patterns': dict(sorted(
                self.common_patterns.items(), 
                key=lambda x: x[1], 
                reverse=True
            )[:5]),
            'form_context': self.form_context,
            'user_preferences': self.user_preferences,
        }
    
    def update_context(self, context_data: Dict[str, Any]) -> None:
        """
        Update context with external data.
        
        Args:
            context_data: Context data to merge
        """
        if 'form_data' in context_data:
            self.form_context.update(context_data['form_data'])
        
        if 'preferences' in context_data:
            self.user_preferences.update(context_data['preferences'])
        
        if 'navigation' in context_data:
            self.navigation_context.update(context_data['navigation'])
        
        logger.debug("Context updated with external data")
    
    def get_suggestions(self, current_command: str = "") -> List[str]:
        """
        Get command suggestions based on context.
        
        Args:
            current_command: Partial command being typed
            
        Returns:
            List of suggested commands
        """
        suggestions = []
        
        # Suggest based on current domain
        if self.session.current_domain:
            domain_suggestions = self._get_domain_suggestions()
            suggestions.extend(domain_suggestions)
        
        # Suggest based on recent patterns
        pattern_suggestions = self._get_pattern_suggestions()
        suggestions.extend(pattern_suggestions)
        
        # Suggest based on partial command
        if current_command:
            partial_suggestions = self._get_partial_suggestions(current_command)
            suggestions.extend(partial_suggestions)
        
        # Remove duplicates and limit
        unique_suggestions = list(dict.fromkeys(suggestions))
        return unique_suggestions[:10]
    
    def _get_domain_suggestions(self) -> List[str]:
        """Get suggestions based on current domain."""
        domain = self.session.current_domain.lower()
        
        domain_suggestions = {
            'google.com': [
                'search for [topic]',
                'click the first result',
                'scroll down to see more results'
            ],
            'youtube.com': [
                'search for [video topic]',
                'click on the first video',
                'scroll down to see comments'
            ],
            'expedia.com': [
                'book a flight from [origin] to [destination]',
                'find hotels in [city]',
                'rent a car in [location]'
            ],
            'maps.google.com': [
                'get directions from [start] to [end]',
                'search for [place type] near me',
                'zoom in on the map'
            ]
        }
        
        return domain_suggestions.get(domain, [])
    
    def _get_pattern_suggestions(self) -> List[str]:
        """Get suggestions based on common patterns."""
        suggestions = []
        
        # Most common intents
        top_intents = sorted(
            self.common_patterns.items(), 
            key=lambda x: x[1], 
            reverse=True
        )[:3]
        
        intent_templates = {
            'navigate': ['go to [website]', 'open [site]'],
            'search': ['search for [query]', 'find [topic]'],
            'click': ['click [element]', 'press [button]'],
            'type': ['type [text]', 'enter [information]'],
            'scroll': ['scroll down', 'scroll up'],
        }
        
        for intent, _ in top_intents:
            if intent in intent_templates:
                suggestions.extend(intent_templates[intent])
        
        return suggestions
    
    def _get_partial_suggestions(self, partial: str) -> List[str]:
        """Get suggestions based on partial command."""
        partial_lower = partial.lower()
        
        # Common command completions
        completions = {
            'go': ['go to google.com', 'go to youtube.com'],
            'search': ['search for python tutorials', 'search for news'],
            'click': ['click the login button', 'click the first link'],
            'type': ['type hello world', 'type my email'],
            'scroll': ['scroll down', 'scroll up'],
            'book': ['book a flight', 'book a hotel'],
            'get': ['get directions to downtown', 'get directions home'],
            'take': ['take screenshot', 'take a photo'],
        }
        
        suggestions = []
        for prefix, commands in completions.items():
            if partial_lower.startswith(prefix):
                suggestions.extend(commands)
        
        return suggestions
    
    def get_form_context(self, url: str = "") -> Dict[str, Any]:
        """
        Get form context for the current or specified URL.
        
        Args:
            url: URL to get form context for (current if empty)
            
        Returns:
            Dict containing form context
        """
        target_url = url or self.session.current_url
        
        # Return stored form data for this domain
        if target_url:
            try:
                from urllib.parse import urlparse
                domain = urlparse(target_url).netloc
                return self.form_context.get(domain, {})
            except Exception:
                pass
        
        return {}
    
    def save_form_data(self, form_data: Dict[str, Any], url: str = "") -> None:
        """
        Save form data for future use.
        
        Args:
            form_data: Form field data to save
            url: URL to associate data with (current if empty)
        """
        target_url = url or self.session.current_url
        
        if target_url:
            try:
                from urllib.parse import urlparse
                domain = urlparse(target_url).netloc
                
                if domain not in self.form_context:
                    self.form_context[domain] = {}
                
                self.form_context[domain].update(form_data)
                logger.debug(f"Saved form data for domain: {domain}")
                
            except Exception as e:
                logger.warning(f"Failed to save form data: {e}")
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get context statistics."""
        total_commands = len(self.command_history)
        successful_commands = sum(1 for cmd in self.command_history if cmd.success)
        
        return {
            'session_duration': time.time() - self.session.start_time,
            'total_commands': total_commands,
            'successful_commands': successful_commands,
            'success_rate': (successful_commands / total_commands * 100) if total_commands > 0 else 0,
            'unique_domains': len(set(self.session.navigation_history)),
            'common_intents': dict(list(sorted(
                self.common_patterns.items(), 
                key=lambda x: x[1], 
                reverse=True
            ))[:5]),
            'avg_execution_time': (
                sum(cmd.execution_time for cmd in self.command_history) / total_commands
                if total_commands > 0 else 0
            ),
        }
    
    def reset_session(self) -> None:
        """Reset the current session context."""
        old_session_id = self.session.session_id
        
        self.session = SessionContext(
            session_id=f"session_{int(time.time())}",
            start_time=time.time()
        )
        
        self.command_history.clear()
        self.current_context.clear()
        
        logger.info(f"Session reset: {old_session_id} -> {self.session.session_id}")
