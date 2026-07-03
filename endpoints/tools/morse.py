from logging import getLogger

from fastapi import APIRouter, HTTPException, Query


logger = getLogger("api-proxy")
router = APIRouter()




M = {"A":".-","B":"-...","C":"-.-.","D":"-..","E":".","F":"..-.","G":"--.","H":"....","I":"..","J":".---","K":"-.-","L":".-..","M":"--","N":"-.","O":"---","P":".--.","Q":"--.-","R":".-.","S":"...","T":"-","U":"..-","V":"...-","W":".--","X":"-..-","Y":"-.--","Z":"--..","0":"-----","1":".----","2":"..---","3":"...--","4":"....-","5":".....","6":"-....","7":"--...","8":"---..","9":"----.",",":"--..--","?":"..--..","!":"-.-.--",".":".-.-.-","/":"-..-.","(":"-.--.",")":"-.--.-","&":".-...",":":"---...",";":"-.-.-.","=":"-...-","+":".-.-.","-":"-....-","_":"..--.-",'"':".-..-.","@":".--.-."," ":"/"}
R = {v:k for k,v in M.items()}

@router.get("/morse", tags=["tools"])
async def morse_code(text: str = Query(..., description="Text to convert"), direction: str = Query(default="encode")):
    try:
        if direction == "encode":
            out = " ".join(M.get(c.upper(), c) for c in text)
        else:
            out = "".join("".join(R.get(c,c) for c in w.split()) for w in text.split(" / "))
        return {"code": "200", "input": text, "output": out}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Morse error: {e}")

