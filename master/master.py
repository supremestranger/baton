import aiohttp
import asyncio
import fastapi
import math
import db
import uvicorn
from pydantic import BaseModel
from contextlib import asynccontextmanager

COUNT_PER_WORKER = 300
API_KEY = "ajdjFK48!.wi$^erty$@"

@asynccontextmanager
async def lifespan(app: fastapi.FastAPI):
    asyncio.create_task(send_tasks())
    asyncio.create_task(remove_zombies())
    yield

async def send_tasks(period: float = 1):
    while True:
        # todo refactor
        # print("Sending tasks")
        pending_tasks = list(filter(lambda task: task.status == "pending", db.get_tasks()))
        print(f"Currently {len(pending_tasks)} tasks are pending.")
        # TODO что если воркеров надо 3, а свободно 2?
        idle_workers = list(db.get_idle_workers().keys())
        for task in pending_tasks:
            if len(idle_workers) == 0:
                break
            worker = idle_workers.pop()
            await send_task(worker, task.id, task.code, task.start_idx, min(task.start_idx + COUNT_PER_WORKER, task.end_idx), task.data)
            task.status = "sent"
            # workers_count = math.ceil((task.end_idx - task.start_idx) / COUNT_PER_WORKER)
            # workers_available = min(workers_count, len(idle_workers))
            # print(f"Task {task.id} needs {workers_count} workers, available: {workers_available}")

            # # TODO что если таймаут
            # await send_task_to_workers(idle_workers, task, workers_available)

            # if task.start_idx == task.end_idx:
            #     print("sent")
            #     task.status = "sent"

            db.update_task(task.id, task)
        await asyncio.sleep(period) 

async def send_task_to_workers(idle_workers: dict[str, db.WorkerData], task: db.Task, workers_available: int):
    for worker in idle_workers:
        await send_task(worker, task.id, task.code, task.start_idx, min(task.start_idx + COUNT_PER_WORKER, task.end_idx), task.data)
        db.update_worker_status(worker, "busy", task.id)

        task.start_idx = min(task.start_idx + COUNT_PER_WORKER, task.end_idx)
        workers_available -= 1
        if workers_available == 0:
            break
    return workers_available

async def remove_zombies(period: float = 10):
    while True:
        db.remove_zombies()
        await asyncio.sleep(period)

app = fastapi.FastAPI(title="Master Node", lifespan=lifespan)

class TaskReq(BaseModel):
    code: str
    data: str # todo должно браться из субд
    rows: int

class StatusReq(BaseModel):
    worker: int
    status: str

class ResReq(BaseModel):
    res: str

async def send_task(worker: str, id: int, code: str, start_idx: int, end_idx: int, data: str):
    db.update_worker_status(worker, "busy")
    async with aiohttp.ClientSession() as s:
        try:
            # compact plaintext JSON message ("c")
            async with s.post("http://localhost:"+str(worker)+"/", json={"id": id, "s": start_idx, "e": end_idx, "c": code, "d": data}) as resp: 
                if resp.status == 200:
                    print("Task is sent successfully.")
        except Exception as e:
            print(e)

@app.post("/task")
async def send_task_handler(task: TaskReq):
    code = task.code
    # TODO make real data 
    db.create_task(task.code, task.data, task.rows) # first save, then resp
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

if __name__ == "__main__":
    uvicorn.run(
        app,
        host="127.0.0.1",
        port=8080,
        log_level="info"
    )