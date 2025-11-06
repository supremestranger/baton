from dataclasses import dataclass
import time

@dataclass
class Task:
    id: int
    code: str
    data: str
    start_idx: int
    end_idx: int
    data: str
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
COUNT_PER_WORKER = 300

def create_task(code: str, data: str, rows: int):
    global TASK_ID
    for i in range(0, rows, COUNT_PER_WORKER):
        task = Task(TASK_ID, code, data, min(i + COUNT_PER_WORKER, rows), i, "pending")
        tasks.append(task)
    TASK_ID += 1

def update_task(id: int, task: Task):
    tasks[id] = task

def remove_task(task: Task):
    tasks.pop(tasks.index(task))

def get_tasks() -> list[Task]:
    return tasks

def update_worker_status(worker: str, status: str, task: int = 0):
    if worker not in workers.keys():
        workers[worker] = WorkerData(worker, status, time.time(), "")

    data = workers[worker]
    data.status = status
    data.last_time_updated = time.time()
    data.current_task = task
    workers[worker] = data

def remove_zombies():
    zombies = dict(filter(lambda kv: time.time() - kv[1].last_time_updated > 10, workers.items()))
    for zombie in zombies:
        if zombies[zombie].status == "busy":
            # todo отобрать задачу
            task = tasks[zombies.get(zombie).current_task]
            task.status = "pending"
            tasks[zombies.get(zombie).current_task] = task
            print(f"Task {task.id} is returned to queue.")
        print("remove zombie")
        del workers[zombie] 

def get_idle_workers() -> dict[str, WorkerData]:
    return dict(filter(lambda kv: kv[1].status == "idle", workers.items()))