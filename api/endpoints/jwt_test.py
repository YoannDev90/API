from fastapi import APIRouter, Request, HTTPException
from api.utils.jwt_verifier import jwt_verifier

router = APIRouter()

@router.get("/test-jwt", tags=["jwt"])
async def test_jwt_get(request: Request):
    """Tester la vérification JWT (GET)."""
    try:
        payload = await jwt_verifier.verify_request(request)
        is_anonymous = payload.get('isAnonymous', False)
        
        if is_anonymous:
            return {"message": "WORKING - ANONYMOUS JWT", "user_id": payload.get('user_id')}
        else:
            return {"message": "IT WORKS", "user_id": payload.get('user_id'), "email": payload.get('email')}
            
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=401, detail="Invalid token")