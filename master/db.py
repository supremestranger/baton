from dataclasses import dataclass
import time

@dataclass
class Task:
    id: int
    code: str
    data: str
    rows: int
    number: int
    status: str
    parts: int = 0

@dataclass
class WorkerData:
    id: int
    last_time_updated: float
    current_task: int

users_db = {
    "admin": {
        "password": "admin123",
        "username": "admin"
    },
    "user1": {
        "password": "password123", 
        "username": "user1"
    }
}

TASK_ID = 0

# redis stub.
tasks: list[Task] = []
results: dict[int, list[str]] = {}
workers: dict[int, WorkerData] = {}
COUNT_PER_WORKER = 300

def create_user(username: str, password: str):
    users_db[username] = { "username": username, "password": password }

def create_task(code: str, data: str, rows: int):
    global TASK_ID
    parts = 0
    new_tasks = []
    for i in range(0, rows, COUNT_PER_WORKER):
        task = Task(TASK_ID, code, data, min(i + COUNT_PER_WORKER, rows), parts, "pending")
        new_tasks.append(task)
        parts += 1
        TASK_ID += 1
    for task in new_tasks:
        task.parts = parts
        tasks.append(task)
    results[TASK_ID] = [[]] * parts # под каждый диапазон список

def update_task(id: int, task: Task):
    tasks[id] = task

def remove_task(task: Task):
    tasks.pop(tasks.index(task))

def get_tasks() -> list[Task]:
    return tasks

def update_worker_status(worker: int, current_task: int):
    if worker not in workers.keys():
        workers[worker] = WorkerData(worker, time.time(), current_task)

    data = workers[worker]
    data.last_time_updated = time.time()
    data.current_task = current_task
    workers[worker] = data

def remove_zombies():
    zombies = dict(filter(lambda kv: time.time() - kv[1].last_time_updated > 10, workers.items()))
    for zombie in zombies:
        if zombies[zombie].current_task >= 0:
            # todo отобрать задачу
            task = tasks[zombies.get(zombie).current_task]
            task.status = "pending"
            tasks[zombies.get(zombie).current_task] = task
            print(f"Task {task.id} is returned to queue.")
        print("remove zombie")
        del workers[zombie] 

def get_idle_workers() -> dict[str, WorkerData]:
    return dict(filter(lambda kv: kv[1].current_task < 0, workers.items()))