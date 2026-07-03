from logging import getLogger

from fastapi import APIRouter, HTTPException, Query


logger = getLogger("api-proxy")
router = APIRouter()




@router.get("/password-strength", tags=["utils"])
async def password_strength(password: str = Query(..., description="Password to check")):
    try:
        import zxcvbn
        r = zxcvbn.zxcvbn(password)
        return {"code": "200", "score": r["score"], "label": ["very weak","weak","fair","strong","very strong"][r["score"]],
                "crack_time": r["crack_times_display"]["offline_slow_hashing_1e4_per_second"], "feedback": r.get("feedback", {})}
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Password check failed: {e}")

