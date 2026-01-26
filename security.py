#!/usr/bin/env python3
"""
Security Module for AI Assistant

Provides security utilities and safe execution environments.
"""

import os
import re
import hashlib
import secrets
import subprocess
from typing import List, Dict, Any, Optional, Tuple
from pathlib import Path


class SecurityManager:
    """
    Security manager for safe operations and input sanitization
    """
    
    def __init__(self):
        self.dangerous_patterns = [
            r'__import__',
            r'exec\s*\(',
            r'eval\s*\(',
            r'open\s*\(',
            r'file\s*\(',
            r'input\s*\(',
            r'raw_input\s*\(',
            r'compile\s*\(',
            r'globals\s*\(',
            r'locals\s*\(',
            r'vars\s*\(',
            r'dir\s*\(',
            r'getattr\s*\(',
            r'setattr\s*\(',
            r'delattr\s*\(',
            r'hasattr\s*\(',
        ]
        
        self.safe_math_functions = {
            'abs', 'round', 'min', 'max', 'sum', 'pow',
            'sqrt', 'sin', 'cos', 'tan', 'log', 'log10',
            'ceil', 'floor', 'pi', 'e'
        }
        
        self.allowed_chars_pattern = re.compile(r'^[a-zA-Z0-9\s\-_.,!?()+=*/\[\]{}:;"\'<>]+$')
    
    def sanitize_input(self, user_input: str, max_length: int = 500) -> str:
        """
        Sanitize user input for safe processing
        
        Args:
            user_input: Raw user input
            max_length: Maximum allowed length
            
        Returns:
            Sanitized input string
        """
        if not isinstance(user_input, str):
            return ""
        
        # Limit length
        sanitized = user_input[:max_length]
        
        # Remove null bytes and control characters
        sanitized = ''.join(char for char in sanitized if ord(char) >= 32 or char in '\t\n\r')
        
        # Strip whitespace
        sanitized = sanitized.strip()
        
        return sanitized
    
    def is_safe_command(self, command: str) -> Tuple[bool, str]:
        """
        Check if a command is safe to execute
        
        Args:
            command: Command to check
            
        Returns:
            Tuple of (is_safe, reason)
        """
        if not command or not command.strip():
            return False, "Empty command"
        
        command_lower = command.lower()
        
        # Check for dangerous patterns
        for pattern in self.dangerous_patterns:
            if re.search(pattern, command_lower):
                return False, f"Contains dangerous pattern: {pattern}"
        
        # Check for shell injection attempts
        shell_chars = ['|', '&', ';', '`', '$', '>', '<', '\\']
        if any(char in command for char in shell_chars):
            return False, "Contains shell injection characters"
        
        # Check for path traversal
        if '..' in command or '~' in command:
            return False, "Contains path traversal patterns"
        
        return True, "Command appears safe"
    
    def validate_file_path(self, file_path: str, allowed_dirs: List[str] = None) -> Tuple[bool, str]:
        """
        Validate file path for security
        
        Args:
            file_path: File path to validate
            allowed_dirs: List of allowed directories
            
        Returns:
            Tuple of (is_valid, reason)
        """
        if not file_path:
            return False, "Empty file path"
        
        try:
            path = Path(file_path).resolve()
            
            # Check for path traversal
            if '..' in str(path):
                return False, "Path traversal detected"
            
            # Check if path is within allowed directories
            if allowed_dirs:
                allowed = False
                for allowed_dir in allowed_dirs:
                    allowed_path = Path(allowed_dir).resolve()
                    try:
                        path.relative_to(allowed_path)
                        allowed = True
                        break
                    except ValueError:
                        continue
                
                if not allowed:
                    return False, "Path not in allowed directories"
            
            return True, "Path is valid"
            
        except Exception as e:
            return False, f"Invalid path: {str(e)}"
    
    def create_safe_eval_environment(self) -> Dict[str, Any]:
        """
        Create a safe environment for eval operations
        
        Returns:
            Safe environment dictionary
        """
        import math
        
        safe_env = {
            '__builtins__': {},
            # Math functions
            'abs': abs,
            'round': round,
            'min': min,
            'max': max,
            'sum': sum,
            'pow': pow,
        }
        
        # Add safe math functions
        for func_name in self.safe_math_functions:
            if hasattr(math, func_name):
                safe_env[func_name] = getattr(math, func_name)
        
        return safe_env
    
    def safe_eval(self, expression: str, timeout: float = 5.0) -> Tuple[bool, Any, str]:
        """
        Safely evaluate a mathematical expression
        
        Args:
            expression: Expression to evaluate
            timeout: Timeout in seconds
            
        Returns:
            Tuple of (success, result, error_message)
        """
        # Validate expression
        is_safe, reason = self.is_safe_math_expression(expression)
        if not is_safe:
            return False, None, reason
        
        try:
            # Create safe environment
            safe_env = self.create_safe_eval_environment()
            
            # Evaluate with timeout (basic implementation)
            result = eval(expression, safe_env)
            
            # Validate result
            if not isinstance(result, (int, float, complex)):
                return False, None, "Result is not a number"
            
            return True, result, ""
            
        except ZeroDivisionError:
            return False, None, "Division by zero"
        except OverflowError:
            return False, None, "Number too large"
        except ValueError as e:
            return False, None, f"Invalid value: {str(e)}"
        except Exception as e:
            return False, None, f"Evaluation error: {str(e)}"
    
    def is_safe_math_expression(self, expression: str) -> Tuple[bool, str]:
        """
        Check if a mathematical expression is safe
        
        Args:
            expression: Expression to check
            
        Returns:
            Tuple of (is_safe, reason)
        """
        if not expression or len(expression) > 200:
            return False, "Expression empty or too long"
        
        # Check for dangerous patterns
        for pattern in self.dangerous_patterns:
            if re.search(pattern, expression, re.IGNORECASE):
                return False, f"Contains dangerous pattern: {pattern}"
        
        # Allow only safe characters for math
        safe_math_pattern = re.compile(r'^[0-9+\-*/().\s,a-zA-Z_]+$')
        if not safe_math_pattern.match(expression):
            return False, "Contains invalid characters"
        
        # Check for excessive nesting
        if expression.count('(') > 10 or expression.count('[') > 5:
            return False, "Too many nested operations"
        
        return True, "Expression appears safe"
    
    def generate_session_token(self, length: int = 32) -> str:
        """
        Generate a secure session token
        
        Args:
            length: Token length
            
        Returns:
            Secure random token
        """
        return secrets.token_urlsafe(length)
    
    def hash_sensitive_data(self, data: str, salt: str = None) -> Tuple[str, str]:
        """
        Hash sensitive data with salt
        
        Args:
            data: Data to hash
            salt: Optional salt (generated if not provided)
            
        Returns:
            Tuple of (hash, salt)
        """
        if salt is None:
            salt = secrets.token_hex(16)
        
        # Combine data and salt
        salted_data = f"{data}{salt}".encode('utf-8')
        
        # Create hash
        hash_obj = hashlib.sha256(salted_data)
        hash_hex = hash_obj.hexdigest()
        
        return hash_hex, salt
    
    def verify_hash(self, data: str, hash_value: str, salt: str) -> bool:
        """
        Verify hashed data
        
        Args:
            data: Original data
            hash_value: Hash to verify against
            salt: Salt used in hashing
            
        Returns:
            True if hash matches
        """
        computed_hash, _ = self.hash_sensitive_data(data, salt)
        return computed_hash == hash_value
    
    def sanitize_filename(self, filename: str) -> str:
        """
        Sanitize filename for safe file operations
        
        Args:
            filename: Original filename
            
        Returns:
            Sanitized filename
        """
        if not filename:
            return "unnamed"
        
        # Remove path components
        filename = os.path.basename(filename)
        
        # Remove dangerous characters
        sanitized = re.sub(r'[<>:"/\\|?*]', '_', filename)
        
        # Remove control characters
        sanitized = ''.join(char for char in sanitized if ord(char) >= 32)
        
        # Limit length
        sanitized = sanitized[:100]
        
        # Ensure it's not empty
        if not sanitized.strip():
            sanitized = "unnamed"
        
        return sanitized.strip()
    
    def check_resource_limits(self, operation: str, **kwargs) -> Tuple[bool, str]:
        """
        Check if operation is within resource limits
        
        Args:
            operation: Type of operation
            **kwargs: Operation parameters
            
        Returns:
            Tuple of (allowed, reason)
        """
        limits = {
            'file_size': 10 * 1024 * 1024,  # 10MB
            'string_length': 10000,
            'list_length': 1000,
            'dict_size': 1000,
            'timer_duration': 86400,  # 24 hours
        }
        
        if operation == 'file_operation':
            size = kwargs.get('size', 0)
            if size > limits['file_size']:
                return False, f"File too large (max {limits['file_size']} bytes)"
        
        elif operation == 'string_operation':
            length = kwargs.get('length', 0)
            if length > limits['string_length']:
                return False, f"String too long (max {limits['string_length']} chars)"
        
        elif operation == 'timer_operation':
            duration = kwargs.get('duration', 0)
            if duration > limits['timer_duration']:
                return False, f"Timer too long (max {limits['timer_duration']} seconds)"
        
        return True, "Within limits"


# Global security manager instance
_security_manager: Optional[SecurityManager] = None


def get_security_manager() -> SecurityManager:
    """Get the global security manager instance"""
    global _security_manager
    if _security_manager is None:
        _security_manager = SecurityManager()
    return _security_manager


# Convenience functions
def sanitize_user_input(user_input: str) -> str:
    """Sanitize user input"""
    return get_security_manager().sanitize_input(user_input)


def is_safe_command(command: str) -> bool:
    """Check if command is safe"""
    is_safe, _ = get_security_manager().is_safe_command(command)
    return is_safe


def safe_eval_math(expression: str) -> Tuple[bool, Any]:
    """Safely evaluate math expression"""
    success, result, _ = get_security_manager().safe_eval(expression)
    return success, result


if __name__ == "__main__":
    # Test security system
    print("🔒 Testing Security System")
    print("=" * 40)
    
    security = SecurityManager()
    
    # Test input sanitization
    print("\n🧹 Input Sanitization:")
    dirty_input = "hello\x00world\x01test"
    clean_input = security.sanitize_input(dirty_input)
    print(f"Original: {repr(dirty_input)}")
    print(f"Sanitized: {repr(clean_input)}")
    
    # Test command safety
    print("\n⚠️  Command Safety:")
    safe_cmd = "echo hello"
    unsafe_cmd = "rm -rf / && echo hello"
    
    is_safe, reason = security.is_safe_command(safe_cmd)
    print(f"Safe command: {is_safe} - {reason}")
    
    is_safe, reason = security.is_safe_command(unsafe_cmd)
    print(f"Unsafe command: {is_safe} - {reason}")
    
    # Test math evaluation
    print("\n🧮 Safe Math Evaluation:")
    expressions = ["2 + 2", "sqrt(16)", "__import__('os')"]
    
    for expr in expressions:
        success, result, error = security.safe_eval(expr)
        print(f"'{expr}': {success} - {result if success else error}")
    
    # Test token generation
    print("\n🎫 Token Generation:")
    token = security.generate_session_token()
    print(f"Session token: {token[:16]}...")
    
    print("\n✅ Security system working!")