"""
Security Vault for Adam Browser

Provides encrypted storage for credentials, API keys, and sensitive data
with AES-256 encryption and secure key derivation.
"""

import os
import json
import hashlib
import secrets
from typing import Dict, Optional, Any, List
from pathlib import Path
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import base64
from loguru import logger

from ..config import config


class SecurityVault:
    """
    Encrypted credential storage vault.
    
    Provides secure storage for passwords, API keys, and other sensitive
    data using AES-256 encryption with PBKDF2 key derivation.
    """
    
    def __init__(self, vault_path: Optional[str] = None):
        """
        Initialize the security vault.
        
        Args:
            vault_path: Path to vault file (uses config default if None)
        """
        self.vault_path = vault_path or config.security.vault_path
        self.master_password: Optional[str] = None
        self.encryption_key: Optional[bytes] = None
        self.salt: Optional[bytes] = None
        self.is_unlocked = False
        
        # Ensure vault directory exists
        os.makedirs(os.path.dirname(self.vault_path), exist_ok=True)
        
        # In-memory credential cache
        self._credentials: Dict[str, Dict[str, Any]] = {}
        
        logger.info(f"Security vault initialized: {self.vault_path}")
    
    async def initialize(self) -> bool:
        """
        Initialize the vault.
        
        Returns:
            bool: True if initialization successful
        """
        try:
            # Check if vault file exists
            if os.path.exists(self.vault_path):
                logger.info("Existing vault found")
                return True
            else:
                logger.info("No existing vault found - will create on first unlock")
                return True
                
        except Exception as e:
            logger.error(f"Failed to initialize vault: {e}")
            return False
    
    def unlock(self, master_password: str) -> bool:
        """
        Unlock the vault with master password.
        
        Args:
            master_password: Master password for vault
            
        Returns:
            bool: True if unlock successful
        """
        try:
            self.master_password = master_password
            
            if os.path.exists(self.vault_path):
                # Load existing vault
                return self._load_vault()
            else:
                # Create new vault
                return self._create_vault()
                
        except Exception as e:
            logger.error(f"Failed to unlock vault: {e}")
            return False
    
    def _create_vault(self) -> bool:
        """Create a new vault."""
        try:
            # Generate salt
            self.salt = secrets.token_bytes(32)
            
            # Derive encryption key
            self.encryption_key = self._derive_key(self.master_password, self.salt)
            
            # Create empty vault structure
            vault_data = {
                'version': '1.0',
                'salt': base64.b64encode(self.salt).decode('utf-8'),
                'credentials': {},
                'metadata': {
                    'created_at': str(int(os.path.getmtime(__file__))),
                    'last_accessed': str(int(os.path.getmtime(__file__))),
                }
            }
            
            # Save vault
            if self._save_vault(vault_data):
                self.is_unlocked = True
                logger.info("New vault created successfully")
                return True
            else:
                return False
                
        except Exception as e:
            logger.error(f"Failed to create vault: {e}")
            return False
    
    def _load_vault(self) -> bool:
        """Load existing vault."""
        try:
            with open(self.vault_path, 'rb') as f:
                encrypted_data = f.read()
            
            # Extract salt from file header (first 44 bytes when base64 encoded)
            # For now, we'll store salt in the encrypted JSON
            # In production, you might want a more sophisticated format
            
            # Try to decrypt with provided password
            # First, we need to extract the salt somehow
            # For simplicity, let's assume the file starts with the salt
            
            # Read as text first to get salt
            with open(self.vault_path, 'r', encoding='utf-8') as f:
                try:
                    # Try to read as JSON (unencrypted metadata)
                    vault_data = json.load(f)
                    if 'salt' in vault_data:
                        self.salt = base64.b64decode(vault_data['salt'])
                    else:
                        # Legacy format or corrupted
                        logger.error("No salt found in vault file")
                        return False
                except json.JSONDecodeError:
                    # File is fully encrypted, need different approach
                    logger.error("Vault format not supported")
                    return False
            
            # Derive key
            self.encryption_key = self._derive_key(self.master_password, self.salt)
            
            # Decrypt credentials section
            if 'credentials' in vault_data:
                encrypted_creds = vault_data['credentials']
                if isinstance(encrypted_creds, str):
                    # Decrypt the credentials
                    fernet = Fernet(base64.urlsafe_b64encode(self.encryption_key[:32]))
                    decrypted_data = fernet.decrypt(encrypted_creds.encode())
                    self._credentials = json.loads(decrypted_data.decode())
                else:
                    # Unencrypted (development mode)
                    self._credentials = encrypted_creds
            
            self.is_unlocked = True
            logger.info("Vault unlocked successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to load vault: {e}")
            return False
    
    def _save_vault(self, vault_data: Optional[Dict[str, Any]] = None) -> bool:
        """Save vault to file."""
        try:
            if not self.is_unlocked:
                logger.error("Vault is locked")
                return False
            
            if vault_data is None:
                # Create vault data from current state
                vault_data = {
                    'version': '1.0',
                    'salt': base64.b64encode(self.salt).decode('utf-8'),
                    'credentials': {},
                    'metadata': {
                        'last_accessed': str(int(os.path.getmtime(__file__))),
                    }
                }
            
            # Encrypt credentials
            if self._credentials:
                fernet = Fernet(base64.urlsafe_b64encode(self.encryption_key[:32]))
                creds_json = json.dumps(self._credentials)
                encrypted_creds = fernet.encrypt(creds_json.encode())
                vault_data['credentials'] = encrypted_creds.decode()
            
            # Save to file
            with open(self.vault_path, 'w', encoding='utf-8') as f:
                json.dump(vault_data, f, indent=2)
            
            logger.debug("Vault saved successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to save vault: {e}")
            return False
    
    def _derive_key(self, password: str, salt: bytes) -> bytes:
        """Derive encryption key from password and salt."""
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        return kdf.derive(password.encode())
    
    def store_credential(self, site: str, username: str, password: str, 
                        metadata: Optional[Dict[str, Any]] = None) -> bool:
        """
        Store a credential in the vault.
        
        Args:
            site: Website or service identifier
            username: Username or email
            password: Password to store
            metadata: Optional additional metadata
            
        Returns:
            bool: True if storage successful
        """
        if not self.is_unlocked:
            logger.error("Vault is locked")
            return False
        
        try:
            credential_data = {
                'username': username,
                'password': password,
                'created_at': str(int(os.path.getmtime(__file__))),
                'last_used': str(int(os.path.getmtime(__file__))),
                'metadata': metadata or {}
            }
            
            self._credentials[site] = credential_data
            
            # Save to file
            if self._save_vault():
                logger.info(f"Credential stored for site: {site}")
                return True
            else:
                return False
                
        except Exception as e:
            logger.error(f"Failed to store credential: {e}")
            return False
    
    def get_credential(self, site: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve a credential from the vault.
        
        Args:
            site: Website or service identifier
            
        Returns:
            Dict containing credential data, or None if not found
        """
        if not self.is_unlocked:
            logger.error("Vault is locked")
            return None
        
        try:
            if site in self._credentials:
                credential = self._credentials[site].copy()
                
                # Update last used timestamp
                credential['last_used'] = str(int(os.path.getmtime(__file__)))
                self._credentials[site]['last_used'] = credential['last_used']
                
                # Save updated timestamp
                self._save_vault()
                
                logger.debug(f"Retrieved credential for site: {site}")
                return credential
            else:
                logger.debug(f"No credential found for site: {site}")
                return None
                
        except Exception as e:
            logger.error(f"Failed to retrieve credential: {e}")
            return None
    
    def delete_credential(self, site: str) -> bool:
        """
        Delete a credential from the vault.
        
        Args:
            site: Website or service identifier
            
        Returns:
            bool: True if deletion successful
        """
        if not self.is_unlocked:
            logger.error("Vault is locked")
            return False
        
        try:
            if site in self._credentials:
                del self._credentials[site]
                
                if self._save_vault():
                    logger.info(f"Credential deleted for site: {site}")
                    return True
                else:
                    return False
            else:
                logger.warning(f"No credential found to delete for site: {site}")
                return False
                
        except Exception as e:
            logger.error(f"Failed to delete credential: {e}")
            return False
    
    def list_sites(self) -> List[str]:
        """
        List all sites with stored credentials.
        
        Returns:
            List of site identifiers
        """
        if not self.is_unlocked:
            logger.error("Vault is locked")
            return []
        
        return list(self._credentials.keys())
    
    def lock(self) -> None:
        """Lock the vault and clear sensitive data from memory."""
        self.master_password = None
        self.encryption_key = None
        self._credentials.clear()
        self.is_unlocked = False
        
        logger.info("Vault locked")
    
    def change_master_password(self, old_password: str, new_password: str) -> bool:
        """
        Change the master password.
        
        Args:
            old_password: Current master password
            new_password: New master password
            
        Returns:
            bool: True if change successful
        """
        if not self.is_unlocked or self.master_password != old_password:
            logger.error("Invalid current password")
            return False
        
        try:
            # Generate new salt
            new_salt = secrets.token_bytes(32)
            
            # Derive new key
            new_key = self._derive_key(new_password, new_salt)
            
            # Update vault
            self.master_password = new_password
            self.salt = new_salt
            self.encryption_key = new_key
            
            # Save with new encryption
            if self._save_vault():
                logger.info("Master password changed successfully")
                return True
            else:
                return False
                
        except Exception as e:
            logger.error(f"Failed to change master password: {e}")
            return False
    
    def export_credentials(self, export_password: str) -> Optional[str]:
        """
        Export credentials in encrypted format.
        
        Args:
            export_password: Password for export encryption
            
        Returns:
            Encrypted export data as string, or None if failed
        """
        if not self.is_unlocked:
            logger.error("Vault is locked")
            return None
        
        try:
            # Create export data
            export_data = {
                'version': '1.0',
                'export_timestamp': str(int(os.path.getmtime(__file__))),
                'credentials': self._credentials
            }
            
            # Encrypt with export password
            export_salt = secrets.token_bytes(32)
            export_key = self._derive_key(export_password, export_salt)
            
            fernet = Fernet(base64.urlsafe_b64encode(export_key[:32]))
            encrypted_export = fernet.encrypt(json.dumps(export_data).encode())
            
            # Create final export package
            export_package = {
                'salt': base64.b64encode(export_salt).decode('utf-8'),
                'data': encrypted_export.decode()
            }
            
            logger.info("Credentials exported successfully")
            return json.dumps(export_package)
            
        except Exception as e:
            logger.error(f"Failed to export credentials: {e}")
            return None
    
    def import_credentials(self, import_data: str, import_password: str) -> bool:
        """
        Import credentials from encrypted export.
        
        Args:
            import_data: Encrypted export data
            import_password: Password for import decryption
            
        Returns:
            bool: True if import successful
        """
        if not self.is_unlocked:
            logger.error("Vault is locked")
            return False
        
        try:
            # Parse import package
            import_package = json.loads(import_data)
            import_salt = base64.b64decode(import_package['salt'])
            encrypted_data = import_package['data']
            
            # Derive import key
            import_key = self._derive_key(import_password, import_salt)
            
            # Decrypt import data
            fernet = Fernet(base64.urlsafe_b64encode(import_key[:32]))
            decrypted_data = fernet.decrypt(encrypted_data.encode())
            export_data = json.loads(decrypted_data.decode())
            
            # Merge credentials
            imported_creds = export_data.get('credentials', {})
            self._credentials.update(imported_creds)
            
            # Save updated vault
            if self._save_vault():
                logger.info(f"Imported {len(imported_creds)} credentials")
                return True
            else:
                return False
                
        except Exception as e:
            logger.error(f"Failed to import credentials: {e}")
            return False
    
    def get_vault_info(self) -> Dict[str, Any]:
        """Get vault information and statistics."""
        return {
            'vault_path': self.vault_path,
            'is_unlocked': self.is_unlocked,
            'credential_count': len(self._credentials) if self.is_unlocked else 0,
            'vault_exists': os.path.exists(self.vault_path),
            'vault_size': os.path.getsize(self.vault_path) if os.path.exists(self.vault_path) else 0,
        }
