"""
Security Module for Adam Browser

Provides encryption, credential management, and security utilities
for protecting sensitive user data and browser automation credentials.

Components:
- SecurityVault: Encrypted credential storage
- EncryptionManager: AES encryption utilities
- SessionManager: Secure session handling
"""

from .vault import SecurityVault
from .encryption import EncryptionManager
from .session import SessionManager

__all__ = [
    "SecurityVault",
    "EncryptionManager",
    "SessionManager",
]
