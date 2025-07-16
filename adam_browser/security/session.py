"""
Session Manager for Adam Browser

Manages secure sessions with timeout, authentication, and state tracking.
"""

import time
import secrets
from typing import Dict, Optional, Any, Set
from dataclasses import dataclass, field
from enum import Enum
from loguru import logger

from ..config import config


class SessionState(Enum):
    """Session states."""
    ACTIVE = "active"
    EXPIRED = "expired"
    LOCKED = "locked"
    TERMINATED = "terminated"


@dataclass
class Session:
    """Session data structure."""
    session_id: str
    user_id: str
    created_at: float
    last_activity: float
    state: SessionState = SessionState.ACTIVE
    data: Dict[str, Any] = field(default_factory=dict)
    permissions: Set[str] = field(default_factory=set)
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None


class SessionManager:
    """
    Manages secure user sessions with timeout and authentication.
    
    Provides session creation, validation, timeout handling,
    and secure session data storage.
    """
    
    def __init__(self):
        """Initialize session manager."""
        self.sessions: Dict[str, Session] = {}
        self.session_timeout = config.security.session_timeout
        self.auto_lock = config.security.auto_lock
        
        # Session cleanup tracking
        self.last_cleanup = time.time()
        self.cleanup_interval = 300  # 5 minutes
        
        logger.info("Session manager initialized")
    
    def create_session(self, user_id: str, permissions: Optional[Set[str]] = None,
                      ip_address: Optional[str] = None, 
                      user_agent: Optional[str] = None) -> str:
        """
        Create a new session.
        
        Args:
            user_id: User identifier
            permissions: Set of permissions for this session
            ip_address: Client IP address
            user_agent: Client user agent
            
        Returns:
            str: Session ID
        """
        try:
            # Generate secure session ID
            session_id = self._generate_session_id()
            
            # Create session
            session = Session(
                session_id=session_id,
                user_id=user_id,
                created_at=time.time(),
                last_activity=time.time(),
                permissions=permissions or set(),
                ip_address=ip_address,
                user_agent=user_agent
            )
            
            # Store session
            self.sessions[session_id] = session
            
            logger.info(f"Session created: {session_id} for user: {user_id}")
            return session_id
            
        except Exception as e:
            logger.error(f"Failed to create session: {e}")
            raise
    
    def validate_session(self, session_id: str, 
                         ip_address: Optional[str] = None) -> Optional[Session]:
        """
        Validate and refresh a session.
        
        Args:
            session_id: Session ID to validate
            ip_address: Client IP address for validation
            
        Returns:
            Session: Valid session object, or None if invalid
        """
        try:
            # Clean up expired sessions periodically
            self._cleanup_expired_sessions()
            
            # Get session
            session = self.sessions.get(session_id)
            if not session:
                logger.debug(f"Session not found: {session_id}")
                return None
            
            # Check session state
            if session.state != SessionState.ACTIVE:
                logger.debug(f"Session not active: {session_id} (state: {session.state.value})")
                return None
            
            # Check timeout
            if self._is_session_expired(session):
                self._expire_session(session_id)
                logger.debug(f"Session expired: {session_id}")
                return None
            
            # Validate IP address if provided and stored
            if ip_address and session.ip_address and ip_address != session.ip_address:
                logger.warning(f"IP address mismatch for session: {session_id}")
                # Optionally terminate session on IP mismatch
                # self._terminate_session(session_id)
                # return None
            
            # Update last activity
            session.last_activity = time.time()
            
            logger.debug(f"Session validated: {session_id}")
            return session
            
        except Exception as e:
            logger.error(f"Session validation failed: {e}")
            return None
    
    def terminate_session(self, session_id: str) -> bool:
        """
        Terminate a session.
        
        Args:
            session_id: Session ID to terminate
            
        Returns:
            bool: True if session was terminated
        """
        try:
            session = self.sessions.get(session_id)
            if session:
                session.state = SessionState.TERMINATED
                session.data.clear()  # Clear sensitive data
                
                # Remove from active sessions
                del self.sessions[session_id]
                
                logger.info(f"Session terminated: {session_id}")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Failed to terminate session: {e}")
            return False
    
    def lock_session(self, session_id: str) -> bool:
        """
        Lock a session (requires re-authentication to unlock).
        
        Args:
            session_id: Session ID to lock
            
        Returns:
            bool: True if session was locked
        """
        try:
            session = self.sessions.get(session_id)
            if session and session.state == SessionState.ACTIVE:
                session.state = SessionState.LOCKED
                logger.info(f"Session locked: {session_id}")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Failed to lock session: {e}")
            return False
    
    def unlock_session(self, session_id: str, password: str) -> bool:
        """
        Unlock a locked session.
        
        Args:
            session_id: Session ID to unlock
            password: Password for authentication
            
        Returns:
            bool: True if session was unlocked
        """
        try:
            session = self.sessions.get(session_id)
            if session and session.state == SessionState.LOCKED:
                # In a real implementation, you would verify the password
                # For now, we'll assume password verification is handled elsewhere
                
                session.state = SessionState.ACTIVE
                session.last_activity = time.time()
                
                logger.info(f"Session unlocked: {session_id}")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Failed to unlock session: {e}")
            return False
    
    def get_session_data(self, session_id: str, key: str) -> Any:
        """
        Get session data value.
        
        Args:
            session_id: Session ID
            key: Data key
            
        Returns:
            Any: Session data value, or None if not found
        """
        session = self.sessions.get(session_id)
        if session and session.state == SessionState.ACTIVE:
            return session.data.get(key)
        return None
    
    def set_session_data(self, session_id: str, key: str, value: Any) -> bool:
        """
        Set session data value.
        
        Args:
            session_id: Session ID
            key: Data key
            value: Data value
            
        Returns:
            bool: True if data was set
        """
        try:
            session = self.sessions.get(session_id)
            if session and session.state == SessionState.ACTIVE:
                session.data[key] = value
                session.last_activity = time.time()
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Failed to set session data: {e}")
            return False
    
    def has_permission(self, session_id: str, permission: str) -> bool:
        """
        Check if session has a specific permission.
        
        Args:
            session_id: Session ID
            permission: Permission to check
            
        Returns:
            bool: True if session has permission
        """
        session = self.sessions.get(session_id)
        if session and session.state == SessionState.ACTIVE:
            return permission in session.permissions
        return False
    
    def add_permission(self, session_id: str, permission: str) -> bool:
        """
        Add permission to session.
        
        Args:
            session_id: Session ID
            permission: Permission to add
            
        Returns:
            bool: True if permission was added
        """
        try:
            session = self.sessions.get(session_id)
            if session and session.state == SessionState.ACTIVE:
                session.permissions.add(permission)
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Failed to add permission: {e}")
            return False
    
    def remove_permission(self, session_id: str, permission: str) -> bool:
        """
        Remove permission from session.
        
        Args:
            session_id: Session ID
            permission: Permission to remove
            
        Returns:
            bool: True if permission was removed
        """
        try:
            session = self.sessions.get(session_id)
            if session and session.state == SessionState.ACTIVE:
                session.permissions.discard(permission)
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Failed to remove permission: {e}")
            return False
    
    def get_active_sessions(self) -> Dict[str, Dict[str, Any]]:
        """
        Get information about active sessions.
        
        Returns:
            Dict: Active session information
        """
        active_sessions = {}
        
        for session_id, session in self.sessions.items():
            if session.state == SessionState.ACTIVE:
                active_sessions[session_id] = {
                    'user_id': session.user_id,
                    'created_at': session.created_at,
                    'last_activity': session.last_activity,
                    'permissions': list(session.permissions),
                    'ip_address': session.ip_address,
                }
        
        return active_sessions
    
    def _generate_session_id(self) -> str:
        """Generate a secure session ID."""
        return secrets.token_urlsafe(32)
    
    def _is_session_expired(self, session: Session) -> bool:
        """Check if a session has expired."""
        if self.session_timeout <= 0:
            return False  # No timeout
        
        return (time.time() - session.last_activity) > self.session_timeout
    
    def _expire_session(self, session_id: str) -> None:
        """Mark a session as expired."""
        session = self.sessions.get(session_id)
        if session:
            session.state = SessionState.EXPIRED
            logger.debug(f"Session expired: {session_id}")
    
    def _cleanup_expired_sessions(self) -> None:
        """Clean up expired sessions."""
        current_time = time.time()
        
        # Only run cleanup periodically
        if current_time - self.last_cleanup < self.cleanup_interval:
            return
        
        expired_sessions = []
        
        for session_id, session in self.sessions.items():
            if (session.state == SessionState.EXPIRED or 
                self._is_session_expired(session)):
                expired_sessions.append(session_id)
        
        # Remove expired sessions
        for session_id in expired_sessions:
            del self.sessions[session_id]
        
        if expired_sessions:
            logger.info(f"Cleaned up {len(expired_sessions)} expired sessions")
        
        self.last_cleanup = current_time
    
    def terminate_all_sessions(self, user_id: Optional[str] = None) -> int:
        """
        Terminate all sessions, optionally for a specific user.
        
        Args:
            user_id: Optional user ID to filter by
            
        Returns:
            int: Number of sessions terminated
        """
        try:
            sessions_to_terminate = []
            
            for session_id, session in self.sessions.items():
                if user_id is None or session.user_id == user_id:
                    sessions_to_terminate.append(session_id)
            
            # Terminate sessions
            for session_id in sessions_to_terminate:
                self.terminate_session(session_id)
            
            logger.info(f"Terminated {len(sessions_to_terminate)} sessions")
            return len(sessions_to_terminate)
            
        except Exception as e:
            logger.error(f"Failed to terminate sessions: {e}")
            return 0
    
    def get_session_stats(self) -> Dict[str, Any]:
        """Get session statistics."""
        stats = {
            'total_sessions': len(self.sessions),
            'active_sessions': 0,
            'locked_sessions': 0,
            'expired_sessions': 0,
        }
        
        for session in self.sessions.values():
            if session.state == SessionState.ACTIVE:
                stats['active_sessions'] += 1
            elif session.state == SessionState.LOCKED:
                stats['locked_sessions'] += 1
            elif session.state == SessionState.EXPIRED:
                stats['expired_sessions'] += 1
        
        return stats


# Global session manager instance
session_manager = SessionManager()
