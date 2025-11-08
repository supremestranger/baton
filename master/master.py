import aiohttp
import asyncio
import fastapi
from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBasic, HTTPBasicCredentials
import math
import db
import uvicorn
from pydantic import BaseModel
from contextlib import asynccontextmanager

COUNT_PER_WORKER = 300
API_KEY = "ajdjFK48!.wi$^erty$@"

class TaskReq(BaseModel):
    code: str
    data: str # todo должно браться из субд
    rows: int

class StatusReq(BaseModel):
    worker: int
    current_task: int

class ResReq(BaseModel):
    res: str

class UserRegister(BaseModel):
    username: str
    email: str

class WorkerResult(BaseModel):
    worker: int
    data: str  # CSV данные
    number: int

@asynccontextmanager
async def lifespan(app: fastapi.FastAPI):
    asyncio.create_task(send_tasks())
    asyncio.create_task(remove_zombies())
    yield

async def send_tasks(period: float = 1):
    while True:
        pending_tasks = list(filter(lambda task: task.status == "pending", db.get_tasks()))
        print(f"Currently {len(pending_tasks)} tasks are pending.")
      
        idle_workers = list(db.get_idle_workers().keys())
        for task in pending_tasks:
            if len(idle_workers) == 0:
                break
            worker = idle_workers.pop()
            await send_task(worker, task)
            task.status = "sent"
        
            db.update_task(task.id, task)
        await asyncio.sleep(period) 

async def remove_zombies(period: float = 10):
    while True:
        db.remove_zombies()
        await asyncio.sleep(period)

def create_app(lifespan):
    app = fastapi.FastAPI(title="Master Node", lifespan=lifespan)
    app.add_middleware(
        CORSMiddleware, allow_origins=["http://localhost:3000"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"],
    )
    
    return app

app = create_app(lifespan)

security = HTTPBasic()

async def send_task(worker: int, task: db.Task):
    db.update_worker_status(worker, task.id)
    async with aiohttp.ClientSession() as s:
        try:
            # compact plaintext JSON message ("c")
            async with s.post("http://localhost:"+str(worker)+"/", json={"id": task.id, "c": task.code, "d": task.data, "n": task.number}) as resp: 
                if resp.status == 200:
                    print("Task is sent successfully.")
        except Exception as e:
            print(e)

@app.post("/task")
async def send_task_handler(task: TaskReq):
    code = task.code
    db.create_task(task.code, task.data, task.rows) # first save, then resp
    print(f"Task with code: {code}.")

@app.post("/status")
async def get_status(status_req: StatusReq):
    worker = status_req.worker
    current_task = status_req.current_task
    db.update_worker_status(worker, current_task)

@app.post("/results")
async def receive_worker_result(result: WorkerResult):
    task_id = db.workers[result.worker].current_task
    
    db.results[task_id][result.number] = result.data

    print(f"Received result from worker {result.worker}, part {result.number}")
    
    return { "status": "success" }

@app.get("/results/{task_id}")
async def get_results(task_id):
    print(task_id)


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
        port=8080,
        log_level="info"
    )