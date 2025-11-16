"""
JWT verification middleware for AlphaLLM API
"""
import os
import jwt
from fastapi import Request, HTTPException
from typing import Optional, Dict, Any


class JWTVerifier:
    """Middleware for JWT token verification"""
    
    def __init__(self):
        self.jwt_secret = os.getenv('JWT_SECRET')
        if not self.jwt_secret:
            raise ValueError("JWT_SECRET environment variable is required")
    
    def verify_token(self, token: str) -> Dict[str, Any]:
        """
        Verify JWT token and return payload
        
        Args:
            token: JWT token string
            
        Returns:
            Dict containing user_id, email, isAnonymous, etc.
            
        Raises:
            HTTPException: If token is invalid or expired
        """
        try:
            # Decode and verify JWT
            payload = jwt.decode(
                token,
                self.jwt_secret,
                algorithms=['HS256']
            )
            
            # Validate required fields
            if 'user_id' not in payload:
                raise HTTPException(status_code=401, detail="Invalid token: missing user_id")
            
            return payload
            
        except jwt.ExpiredSignatureError:
            raise HTTPException(status_code=401, detail="Invalid token: token expired")
        except jwt.InvalidTokenError as e:
            raise HTTPException(status_code=401, detail=f"Invalid token: {str(e)}")
    
    def extract_token_from_header(self, authorization: Optional[str]) -> str:
        """
        Extract JWT token from Authorization header
        
        Args:
            authorization: Authorization header value
            
        Returns:
            JWT token string
            
        Raises:
            HTTPException: If header is missing or malformed
        """
        if not authorization:
            raise HTTPException(status_code=401, detail="Invalid token: Authorization header missing")
        
        parts = authorization.split()
        
        if len(parts) != 2 or parts[0].lower() != 'bearer':
            raise HTTPException(status_code=401, detail="Invalid token: malformed Authorization header")
        
        return parts[1]
    
    async def verify_request(self, request: Request) -> Dict[str, Any]:
        """
        Verify JWT token from request
        
        Args:
            request: FastAPI request object
            
        Returns:
            Dict containing user_id, email, isAnonymous, etc.
            
        Raises:
            HTTPException: If token is invalid or expired
        """
        authorization = request.headers.get('authorization')
        token = self.extract_token_from_header(authorization)
        return self.verify_token(token)


# Global JWT verifier instance
jwt_verifier = JWTVerifier()
