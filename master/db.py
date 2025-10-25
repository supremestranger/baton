from dataclasses import dataclass
import time

@dataclass
class Task:
    id: int
    code: str
    data: str
    end_idx: int
    start_idx: int # постоянно сдвигается
    status: str

@dataclass
class WorkerData:
    id: int
    status: str
    last_time_updated: float
    current_task: int

TASK_ID = 0

# redis stub.
tasks: list[Task] = []
workers: dict[str, WorkerData] = {}

def create_task(code: str, data, rows: int):
    global TASK_ID
    task = Task(TASK_ID, code, data, rows, 0, "pending")
    TASK_ID += 1
    tasks.append(task)

def update_task(id: int, task: Task):
    tasks[id] = task

def remove_task(task: Task):
    tasks.pop(tasks.index(task))

def get_tasks() -> list[Task]:
    return tasks

def update_worker_status(worker: str, status: str):
    if worker not in workers.keys():
        workers[worker] = WorkerData(worker, status, time.time(), "")

    data = workers[worker]
    data.status = status
    data.last_time_updated = time.time()
    workers[worker] = data

def remove_zombies():
    zombies = dict(filter(lambda kv: time.time() - kv[1].last_time_updated > 10, workers.items()))
    for zombie in zombies:
        print("remove zombie")
        del workers[zombie] 

def get_idle_workers() -> dict[str, WorkerData]:
    return dict(filter(lambda kv: kv[1].status == "idle", workers.items()))