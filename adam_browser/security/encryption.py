"""
Encryption Manager for Adam Browser

Provides AES encryption utilities for secure data storage and transmission.
"""

import os
import base64
import secrets
from typing import Optional, Union, Tuple
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from loguru import logger


class EncryptionManager:
    """
    Provides AES encryption and decryption utilities.
    
    Supports both Fernet (high-level) and AES-GCM (low-level) encryption
    with secure key derivation and random salt generation.
    """
    
    def __init__(self):
        """Initialize encryption manager."""
        logger.info("Encryption manager initialized")
    
    def generate_key(self) -> bytes:
        """
        Generate a new encryption key.
        
        Returns:
            bytes: 32-byte encryption key
        """
        return Fernet.generate_key()
    
    def derive_key_from_password(self, password: str, salt: Optional[bytes] = None) -> Tuple[bytes, bytes]:
        """
        Derive encryption key from password using PBKDF2.
        
        Args:
            password: Password string
            salt: Optional salt (generated if None)
            
        Returns:
            Tuple of (key, salt)
        """
        if salt is None:
            salt = secrets.token_bytes(32)
        
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        
        key = kdf.derive(password.encode())
        return key, salt
    
    def encrypt_fernet(self, data: Union[str, bytes], key: bytes) -> bytes:
        """
        Encrypt data using Fernet (high-level encryption).
        
        Args:
            data: Data to encrypt
            key: Encryption key
            
        Returns:
            bytes: Encrypted data
        """
        try:
            if isinstance(data, str):
                data = data.encode('utf-8')
            
            fernet = Fernet(key)
            encrypted_data = fernet.encrypt(data)
            
            logger.debug("Data encrypted with Fernet")
            return encrypted_data
            
        except Exception as e:
            logger.error(f"Fernet encryption failed: {e}")
            raise
    
    def decrypt_fernet(self, encrypted_data: bytes, key: bytes) -> bytes:
        """
        Decrypt data using Fernet.
        
        Args:
            encrypted_data: Encrypted data
            key: Decryption key
            
        Returns:
            bytes: Decrypted data
        """
        try:
            fernet = Fernet(key)
            decrypted_data = fernet.decrypt(encrypted_data)
            
            logger.debug("Data decrypted with Fernet")
            return decrypted_data
            
        except Exception as e:
            logger.error(f"Fernet decryption failed: {e}")
            raise
    
    def encrypt_aes_gcm(self, data: Union[str, bytes], key: bytes, 
                       associated_data: Optional[bytes] = None) -> Tuple[bytes, bytes, bytes]:
        """
        Encrypt data using AES-GCM.
        
        Args:
            data: Data to encrypt
            key: 32-byte encryption key
            associated_data: Optional associated data for authentication
            
        Returns:
            Tuple of (encrypted_data, nonce, tag)
        """
        try:
            if isinstance(data, str):
                data = data.encode('utf-8')
            
            # Generate random nonce
            nonce = secrets.token_bytes(12)  # 96-bit nonce for GCM
            
            # Create cipher
            cipher = Cipher(algorithms.AES(key), modes.GCM(nonce))
            encryptor = cipher.encryptor()
            
            # Add associated data if provided
            if associated_data:
                encryptor.authenticate_additional_data(associated_data)
            
            # Encrypt data
            encrypted_data = encryptor.update(data) + encryptor.finalize()
            
            logger.debug("Data encrypted with AES-GCM")
            return encrypted_data, nonce, encryptor.tag
            
        except Exception as e:
            logger.error(f"AES-GCM encryption failed: {e}")
            raise
    
    def decrypt_aes_gcm(self, encrypted_data: bytes, key: bytes, nonce: bytes, 
                       tag: bytes, associated_data: Optional[bytes] = None) -> bytes:
        """
        Decrypt data using AES-GCM.
        
        Args:
            encrypted_data: Encrypted data
            key: 32-byte decryption key
            nonce: Nonce used for encryption
            tag: Authentication tag
            associated_data: Optional associated data for authentication
            
        Returns:
            bytes: Decrypted data
        """
        try:
            # Create cipher
            cipher = Cipher(algorithms.AES(key), modes.GCM(nonce, tag))
            decryptor = cipher.decryptor()
            
            # Add associated data if provided
            if associated_data:
                decryptor.authenticate_additional_data(associated_data)
            
            # Decrypt data
            decrypted_data = decryptor.update(encrypted_data) + decryptor.finalize()
            
            logger.debug("Data decrypted with AES-GCM")
            return decrypted_data
            
        except Exception as e:
            logger.error(f"AES-GCM decryption failed: {e}")
            raise
    
    def encrypt_string(self, text: str, password: str) -> str:
        """
        Encrypt a string with password (convenience method).
        
        Args:
            text: Text to encrypt
            password: Password for encryption
            
        Returns:
            str: Base64-encoded encrypted data with salt
        """
        try:
            # Derive key from password
            key, salt = self.derive_key_from_password(password)
            
            # Encrypt using Fernet
            fernet_key = base64.urlsafe_b64encode(key)
            encrypted_data = self.encrypt_fernet(text, fernet_key)
            
            # Combine salt and encrypted data
            combined = salt + encrypted_data
            
            # Return base64 encoded
            return base64.b64encode(combined).decode('utf-8')
            
        except Exception as e:
            logger.error(f"String encryption failed: {e}")
            raise
    
    def decrypt_string(self, encrypted_text: str, password: str) -> str:
        """
        Decrypt a string with password (convenience method).
        
        Args:
            encrypted_text: Base64-encoded encrypted text
            password: Password for decryption
            
        Returns:
            str: Decrypted text
        """
        try:
            # Decode base64
            combined = base64.b64decode(encrypted_text.encode('utf-8'))
            
            # Extract salt and encrypted data
            salt = combined[:32]
            encrypted_data = combined[32:]
            
            # Derive key from password and salt
            key, _ = self.derive_key_from_password(password, salt)
            
            # Decrypt using Fernet
            fernet_key = base64.urlsafe_b64encode(key)
            decrypted_data = self.decrypt_fernet(encrypted_data, fernet_key)
            
            return decrypted_data.decode('utf-8')
            
        except Exception as e:
            logger.error(f"String decryption failed: {e}")
            raise
    
    def generate_secure_token(self, length: int = 32) -> str:
        """
        Generate a secure random token.
        
        Args:
            length: Token length in bytes
            
        Returns:
            str: Base64-encoded secure token
        """
        token_bytes = secrets.token_bytes(length)
        return base64.urlsafe_b64encode(token_bytes).decode('utf-8')
    
    def hash_password(self, password: str, salt: Optional[bytes] = None) -> Tuple[str, str]:
        """
        Hash a password using PBKDF2.
        
        Args:
            password: Password to hash
            salt: Optional salt (generated if None)
            
        Returns:
            Tuple of (hash, salt) as base64 strings
        """
        try:
            if salt is None:
                salt = secrets.token_bytes(32)
            
            kdf = PBKDF2HMAC(
                algorithm=hashes.SHA256(),
                length=32,
                salt=salt,
                iterations=100000,
            )
            
            password_hash = kdf.derive(password.encode())
            
            return (
                base64.b64encode(password_hash).decode('utf-8'),
                base64.b64encode(salt).decode('utf-8')
            )
            
        except Exception as e:
            logger.error(f"Password hashing failed: {e}")
            raise
    
    def verify_password(self, password: str, stored_hash: str, stored_salt: str) -> bool:
        """
        Verify a password against stored hash.
        
        Args:
            password: Password to verify
            stored_hash: Stored password hash (base64)
            stored_salt: Stored salt (base64)
            
        Returns:
            bool: True if password is correct
        """
        try:
            # Decode stored values
            salt = base64.b64decode(stored_salt.encode('utf-8'))
            expected_hash = base64.b64decode(stored_hash.encode('utf-8'))
            
            # Hash provided password with stored salt
            kdf = PBKDF2HMAC(
                algorithm=hashes.SHA256(),
                length=32,
                salt=salt,
                iterations=100000,
            )
            
            password_hash = kdf.derive(password.encode())
            
            # Compare hashes
            return password_hash == expected_hash
            
        except Exception as e:
            logger.error(f"Password verification failed: {e}")
            return False
    
    def secure_delete(self, data: Union[str, bytes]) -> None:
        """
        Securely overwrite data in memory (best effort).
        
        Args:
            data: Data to securely delete
        """
        try:
            if isinstance(data, str):
                # For strings, we can't directly overwrite memory
                # This is a limitation of Python's string immutability
                pass
            elif isinstance(data, (bytes, bytearray)):
                # For mutable byte arrays, overwrite with random data
                if isinstance(data, bytearray):
                    for i in range(len(data)):
                        data[i] = secrets.randbits(8)
            
            # Note: This is best effort - Python's garbage collector
            # and memory management make true secure deletion difficult
            
        except Exception as e:
            logger.warning(f"Secure delete failed: {e}")


# Global encryption manager instance
encryption_manager = EncryptionManager()
