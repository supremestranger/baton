import aiohttp
import asyncio
import fastapi
import math
import db
from pydantic import BaseModel
from contextlib import asynccontextmanager

COUNT_PER_WORKER = 300

@asynccontextmanager
async def lifespan(app: fastapi.FastAPI):
    asyncio.create_task(send_tasks())
    yield

async def send_tasks(period: float = 1):
    while True:
        # print("Sending tasks")
        tasks = db.get_tasks()
        # TODO что если воркеров надо 3, а свободно 2?
        idle_workers = db.get_idle_workers()
        if len(idle_workers) > 0:
            for task in tasks:
                if task.status == "pending":
                    workers_count = math.ceil((task.end_idx - task.start_idx) / COUNT_PER_WORKER)
                    workers_available = min(workers_count, len(idle_workers))
                    print(f"Task {task.id} needs {workers_count} workers, available: {workers_available}")

                    # TODO что если таймаут
                    await send_task_to_workers(idle_workers, task, workers_available)

                    if task.start_idx == task.end_idx:
                        print("sent")
                        task.status = "sent"

                    db.update_task(task.id, task)
        await asyncio.sleep(period) 

async def send_task_to_workers(idle_workers: dict[str, db.WorkerData], task: db.Task, workers_available: int):
    for worker in idle_workers:
        await send_task(worker, task.code, task.start_idx, min(task.start_idx + COUNT_PER_WORKER, task.end_idx))
        db.update_worker_status(worker, "busy")

        task.start_idx = min(task.start_idx + COUNT_PER_WORKER, task.end_idx)
        workers_available -= 1
        if workers_available == 0:
            break
    return workers_available

app = fastapi.FastAPI(title="Master Node", lifespan=lifespan)

class TaskReq(BaseModel):
    code: str
    rows: int

class StatusReq(BaseModel):
    worker: int
    status: str

class ResReq(BaseModel):
    res: str

async def send_task(worker: str, code: str, start_idx: int, end_idx: int):
    async with aiohttp.ClientSession() as s:
        try:
            # compact plaintext JSON message ("c")
            async with s.post("http://localhost:"+str(worker)+"/", json={"c": code}) as resp: 
                if resp.status == 200:
                    print("Task is sent successfully.")
        except Exception as e:
            print(e)

@app.post("/task")
async def send_task_handler(task: TaskReq):
    code = task.code
    # TODO make real data 
    db.create_task(task.code, "", task.rows) # first save, then resp
    print(f"Task with code: {code}.")

@app.post("/status")
async def get_status(status_req: StatusReq):
    worker = status_req.worker
    status = status_req.status
    db.update_worker_status(worker, status)

@app.post("/results")
async def get_results(res: ResReq):
    print("Res", res.res)
    # TODO send to web
