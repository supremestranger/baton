import aiohttp
import asyncio
import fastapi
from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBasic, HTTPBasicCredentials
import common.db as db
import uvicorn
from pydantic import BaseModel
from contextlib import asynccontextmanager

def create_app():
    app = fastapi.FastAPI(title="Web Application")
    app.add_middleware(
        CORSMiddleware, allow_origins=["http://localhost:3000"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"],
    )
    
    return app

app = create_app()
security = HTTPBasic()

def verify_password(username: str, password: str) -> bool:
    if username in db.users_db:
        return password == db.users_db[username]["password"]
    return False

def get_current_user(credentials: HTTPBasicCredentials = Depends(security)):
    username = credentials.username
    password = credentials.password
    
    if not verify_password(username, password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
            headers={"WWW-Authenticate": "Basic"},
        )
    return username

@app.get("/verify")
async def verify_auth(user: str = Depends(get_current_user)):
    return {"message": "Authenticated", "username": user}

@app.post("/register")
async def register_user(
    credentials: HTTPBasicCredentials = Depends(security)
):
    username = credentials.username
    password = credentials.password
    
    if username in db.users_db:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already exists"
        )
    
    db.create_user(username, password)
    
    return {
        "message": "User registered successfully", 
        "username": username,
    }

@app.post("/login")
async def login_user(user: str = Depends(get_current_user)):
    return {
        "message": "Login successful",
        "username": user,
    }

if __name__ == "__main__":
    uvicorn.run(
        app,
        host="127.0.0.1",
        port=8084,
        log_level="info"
    )