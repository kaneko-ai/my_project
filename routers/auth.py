from fastapi import APIRouter, Request, Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import datetime

router = APIRouter()
security = HTTPBearer()

def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    return {"sub": "testuser"}

@router.post("/login")
async def login(request: Request):
    body = await request.json()
    username = body.get("username")
    password = body.get("password")
    if username == "testuser" and password == "testpass":
        token = "fake-jwt-token"
        return {"access_token": token}
    raise HTTPException(status_code=401, detail="Invalid credentials")

@router.get("/secure_metrics")
def secure_metrics(user: dict = Depends(verify_token)):
    return {
        "uptime": "1h",
        "version": "2.0.0",
        "user": user
    }
