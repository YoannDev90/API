"""
Test endpoint for JWT verification
"""
from fastapi import APIRouter, Request, HTTPException
from api.utils.jwt_verifier import jwt_verifier

router = APIRouter(prefix="/test-jwt", tags=["jwt"])


@router.get("")
async def test_jwt_get(request: Request):
    """
    Test JWT verification (GET)
    
    Headers:
        Authorization: Bearer <jwt_token>
        
    Returns:
        - "IT WORKS" if JWT is valid and not anonymous
        - "WORKING - ANONYMOUS JWT" if JWT is valid and anonymous
        - 401 with "Invalid token" if JWT is invalid
    """
    try:
        # Verify JWT token
        payload = await jwt_verifier.verify_request(request)
        
        # Check if user is anonymous
        is_anonymous = payload.get('isAnonymous', False)
        
        if is_anonymous:
            return {"message": "WORKING - ANONYMOUS JWT", "user_id": payload.get('user_id')}
        else:
            return {"message": "IT WORKS", "user_id": payload.get('user_id'), "email": payload.get('email')}
            
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=401, detail="Invalid token")


@router.post("")
async def test_jwt_post(request: Request):
    """
    Test JWT verification (POST)
    
    Headers:
        Authorization: Bearer <jwt_token>
        
    Returns:
        - "IT WORKS" if JWT is valid and not anonymous
        - "WORKING - ANONYMOUS JWT" if JWT is valid and anonymous
        - 401 with "Invalid token" if JWT is invalid
    """
    try:
        # Verify JWT token
        payload = await jwt_verifier.verify_request(request)
        
        # Check if user is anonymous
        is_anonymous = payload.get('isAnonymous', False)
        
        if is_anonymous:
            return {"message": "WORKING - ANONYMOUS JWT", "user_id": payload.get('user_id')}
        else:
            return {"message": "IT WORKS", "user_id": payload.get('user_id'), "email": payload.get('email')}
            
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=401, detail="Invalid token")
