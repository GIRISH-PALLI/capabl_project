"""
Security & Best Practices Module
Handles encryption, secure API communication, and compliance
"""

from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2
import os
import base64
import logging
from typing import Optional, Dict, Any
from datetime import datetime, timedelta
import jwt

logger = logging.getLogger(__name__)


class FinancialDataSecurity:
    """Implements security best practices for financial data handling"""
    
    def __init__(self):
        self.master_key = os.getenv("ENCRYPTION_MASTER_KEY", "default-key")
        self.cipher_suite = Fernet(self._derive_key(self.master_key))
    
    @staticmethod
    def _derive_key(password: str) -> bytes:
        """Derive encryption key from password using PBKDF2"""
        salt = b'capabl_finance_salt'  # Use secure salt in production
        kdf = PBKDF2(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
        return key
    
    def encrypt_pii(self, data: str) -> str:
        """Encrypt personally identifiable information"""
        encrypted = self.cipher_suite.encrypt(data.encode())
        return encrypted.decode()
    
    def decrypt_pii(self, encrypted_data: str) -> str:
        """Decrypt personally identifiable information"""
        try:
            decrypted = self.cipher_suite.decrypt(encrypted_data.encode())
            return decrypted.decode()
        except Exception as e:
            logger.error(f"Decryption failed: {str(e)}")
            raise
    
    def hash_password(self, password: str) -> str:
        """Hash password using bcrypt (use in production)"""
        import bcrypt
        salt = bcrypt.gensalt(rounds=12)
        hashed = bcrypt.hashpw(password.encode(), salt)
        return hashed.decode()
    
    def verify_password(self, password: str, hashed: str) -> bool:
        """Verify password against hash"""
        import bcrypt
        return bcrypt.checkpw(password.encode(), hashed.encode())
    
    @staticmethod
    def sanitize_sql_input(user_input: str, max_length: int = 255) -> str:
        """Sanitize user input to prevent SQL injection"""
        # Remove potentially dangerous characters
        dangerous_chars = ["'", '"', ";", "--", "/*", "*/", "xp_", "sp_"]
        sanitized = user_input[:max_length]
        
        for char in dangerous_chars:
            sanitized = sanitized.replace(char, "")
        
        return sanitized.strip()
    
    @staticmethod
    def validate_api_request(
        signature: str,
        payload: Dict[str, Any],
        shared_secret: str
    ) -> bool:
        """Validate API request signature (HMAC)"""
        import hmac
        import hashlib
        import json
        
        # Serialize payload
        serialized = json.dumps(payload, sort_keys=True)
        
        # Calculate expected signature
        expected_signature = hmac.new(
            shared_secret.encode(),
            serialized.encode(),
            hashlib.sha256
        ).hexdigest()
        
        # Constant-time comparison
        return hmac.compare_digest(signature, expected_signature)


class ComplianceTracker:
    """Track compliance with financial regulations"""
    
    def __init__(self):
        self.audit_log = []
    
    def log_transaction(
        self,
        user_id: str,
        action: str,
        ticker: str,
        quantity: float,
        price: float,
        timestamp: Optional[datetime] = None
    ):
        """Log financial transaction for compliance"""
        
        if timestamp is None:
            timestamp = datetime.utcnow()
        
        log_entry = {
            "user_id": user_id,
            "action": action,
            "ticker": ticker,
            "quantity": quantity,
            "price": price,
            "timestamp": timestamp.isoformat(),
            "total_value": quantity * price
        }
        
        self.audit_log.append(log_entry)
        logger.info(f"Transaction logged: {user_id} - {action} {quantity} {ticker}")
    
    def log_api_access(
        self,
        user_id: str,
        endpoint: str,
        method: str,
        status_code: int,
        timestamp: Optional[datetime] = None
    ):
        """Log API access for security audit"""
        
        if timestamp is None:
            timestamp = datetime.utcnow()
        
        log_entry = {
            "user_id": user_id,
            "endpoint": endpoint,
            "method": method,
            "status_code": status_code,
            "timestamp": timestamp.isoformat()
        }
        
        logger.info(f"API Access: {user_id} - {method} {endpoint} ({status_code})")
    
    def detect_suspicious_activity(
        self,
        user_id: str,
        activity: Dict[str, Any]
    ) -> bool:
        """Detect suspicious trading patterns"""
        
        # Check for unusual transaction patterns
        recent_transactions = [
            log for log in self.audit_log
            if log["user_id"] == user_id
            and log["action"] in ["BUY", "SELL"]
        ]
        
        # Check for rapid transactions (more than 100 in 5 minutes)
        if len(recent_transactions) > 100:
            logger.warning(f"Suspicious activity detected: {user_id}")
            return True
        
        # Check for unusually large transactions
        total_value = sum(log.get("total_value", 0) for log in recent_transactions[-10:])
        if total_value > 10_000_000:  # 10 million INR
            logger.warning(f"Large transaction detected: {user_id} - {total_value}")
            return True
        
        return False
    
    def get_audit_trail(
        self,
        user_id: str,
        days: int = 30
    ) -> list:
        """Get audit trail for a user"""
        
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        trail = [
            log for log in self.audit_log
            if log["user_id"] == user_id
            and datetime.fromisoformat(log["timestamp"]) > cutoff_date
        ]
        
        return sorted(trail, key=lambda x: x["timestamp"], reverse=True)


class APISecurityHeaders:
    """Security headers for API responses"""
    
    @staticmethod
    def get_secure_headers() -> Dict[str, str]:
        """Get recommended security headers"""
        return {
            "X-Content-Type-Options": "nosniff",
            "X-Frame-Options": "DENY",
            "X-XSS-Protection": "1; mode=block",
            "Strict-Transport-Security": "max-age=31536000; includeSubDomains",
            "Content-Security-Policy": "default-src 'self'; script-src 'self' 'unsafe-inline'",
            "Referrer-Policy": "strict-origin-when-cross-origin",
            "Permissions-Policy": "accelerometer=(),camera=(),microphone=(),geolocation=()"
        }


class RateLimiter:
    """Advanced rate limiting with different strategies"""
    
    def __init__(self):
        self.request_history: Dict[str, list] = {}
    
    def is_allowed(
        self,
        user_id: str,
        max_requests: int = 100,
        window_seconds: int = 60
    ) -> bool:
        """Check if request is allowed (Token bucket algorithm)"""
        
        now = datetime.utcnow().timestamp()
        window_start = now - window_seconds
        
        if user_id not in self.request_history:
            self.request_history[user_id] = []
        
        # Clean old requests
        self.request_history[user_id] = [
            req_time for req_time in self.request_history[user_id]
            if req_time > window_start
        ]
        
        # Check limit
        if len(self.request_history[user_id]) >= max_requests:
            logger.warning(f"Rate limit exceeded for {user_id}")
            return False
        
        # Add current request
        self.request_history[user_id].append(now)
        return True
    
    def get_remaining_requests(self, user_id: str, max_requests: int = 100) -> int:
        """Get remaining requests in current window"""
        
        if user_id not in self.request_history:
            return max_requests
        
        return max_requests - len(self.request_history[user_id])


# Initialize security modules
security = FinancialDataSecurity()
compliance = ComplianceTracker()
rate_limiter = RateLimiter()
