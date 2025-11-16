import aiohttp
import asyncio
import fastapi
from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from common import idents
from common import db
import uvicorn
from pydantic import BaseModel
import sys
import os
from contextlib import asynccontextmanager

API_KEY = "ajdjFK48!.wi$^erty$@"

class TaskReq(BaseModel):
    code: str
    data: str # todo должно браться из субд
    rows: int
    creator: str

class StatusReq(BaseModel):
    worker: str
    current_task: int
    current_task_idx: int

class WorkerResult(BaseModel):
    worker: str
    data: str  # CSV данные
    id: int # коммон ид
    number: int

class ErrorReq(BaseModel):
    worker: str
    msg: str  # CSV данные
    id: int # коммон ид
    number: int

@asynccontextmanager
async def lifespan(app: fastapi.FastAPI):
    asyncio.create_task(send_tasks())
    asyncio.create_task(remove_zombies())
    yield

async def send_tasks(period: float = 1):
    while True:
        pending_tasks = list(filter(lambda task: task.status == idents.TaskStatus.PENDING, db.get_tasks()))
        print(f"Currently {len(pending_tasks)} tasks are pending.")
      
        idle_workers = list(db.get_idle_workers().keys())
        for task in pending_tasks:
            if len(idle_workers) == 0:
                break
            worker = idle_workers.pop()
            await send_task(worker, task)
        
            db.update_task(task.common_id, task.idx, idents.TaskStatus.SENT)
        await asyncio.sleep(period) 

async def remove_zombies(period: float = 10):
    while True:
        db.remove_zombies()
        await asyncio.sleep(period)

def create_app(lifespan):
    app = fastapi.FastAPI(title="Master Node", lifespan=lifespan)
    
    return app

app = create_app(lifespan)
app.add_middleware(
        CORSMiddleware, allow_origins=["http://localhost:3000"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"],
    )
security = HTTPBasic()

async def send_task(worker: int, task: db.Task):
    db.update_worker_status(worker, task.common_id, task.idx)
    async with aiohttp.ClientSession() as s:
        try:
            # compact plaintext JSON message ("c")
            async with s.post("http://"+str(worker)+"/", json={"id": task.common_id, "idx": task.idx, "c": task.code, "d": task.data}) as resp: 
                if resp.status == 200:
                    print("Task is sent successfully.")
        except Exception as e:
            print(e)

@app.post("/task")
async def send_task_handler(task: TaskReq):
    db.create_task(task.code, task.data, task.rows, task.creator) # first save, then resp

@app.post("/status")
async def get_status(status_req: StatusReq):
    worker = status_req.worker
    current_task = status_req.current_task
    current_task_idx = status_req.current_task_idx
    
    db.update_worker_status(worker, current_task, current_task_idx)

@app.post("/results")
async def receive_worker_result(result: WorkerResult):
    task_id = db.workers[result.worker].current_task
    
    db.results[task_id][result.number] = result.data

    print(f"Received result from worker {result.worker}, part {result.number}")
    
    return { "status": "success" }

@app.get("/tasks")
async def get_all_tasks():
    return db.tasks

@app.post("/error")
async def task_error(error_req: ErrorReq):
    db.create_error(error_req.id, error_req.msg)

@app.get("/tasks/{user_id}")
async def get_tasks_by_user(user_id: str):
    result: dict[int, str] = {}
    tasks = [task for task in db.tasks if task.creator == user_id]
    for task in tasks:
        task_results = None
        if db.errors[task.common_id] != "":
            result[task.common_id] = "failed"
            continue

        task_results = db.results[int(task.common_id)]

        task_in_progress = [] in [result for result in task_results] # Very good code.
        if task_in_progress:
            result[task.common_id] = "running"
        else:
            result[task.common_id] = "done"
    return result

@app.get("/results/{task_id}")
async def get_results(task_id):
    task_results = None
    try:
        task_results = db.results[int(task_id)]
    except:
        raise HTTPException(status_code=404, detail="Task not found!")
    results = [result for result in task_results]
    print(f"Results for {task_id}: {results}")

    task_in_progress = [] in [result for result in task_results] # Very good code.
    if task_in_progress:
        raise HTTPException(status_code=400, detail="Task in progress!")

    return "".join(results)


if __name__ == "__main__":
    uvicorn.run(
        app,
        host="127.0.0.1",
        port=8080,
        log_level="info"
    )