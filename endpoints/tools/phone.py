from logging import getLogger

from fastapi import APIRouter, HTTPException, Query


logger = getLogger("api-proxy")
router = APIRouter()




@router.get("/phone", tags=["utils"])
async def phone_info(number: str = Query(..., description="Phone number with country code")):
    try:
        import phonenumbers
        from phonenumbers import carrier, geocoder, timezone
        n = phonenumbers.parse(number)
        if not phonenumbers.is_valid_number(n):
            raise HTTPException(status_code=400, detail="Invalid phone number")
        return {
            "code": "200",
            "number": phonenumbers.format_number(n, phonenumbers.PhoneNumberFormat.INTERNATIONAL),
            "country": geocoder.description_for_number(n, "en"),
            "carrier": carrier.name_for_number(n, "en"),
            "timezones": timezone.time_zones_for_number(n),
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Phone error: {e}")

