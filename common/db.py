from dataclasses import dataclass
import time
from . import idents 


@dataclass
class Task:
    common_id: int # коммон id задачи
    idx: int
    code: str
    data: str
    rows: int
    status: str
    creator: str

@dataclass
class WorkerData:
    id: int
    last_time_updated: float
    current_task: int
    current_task_idx: int

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
errors: dict[int, str] = {}
results = {}
workers: dict[str, WorkerData] = {}
COUNT_PER_WORKER = 300

def create_user(username: str, password: str):
    users_db[username] = { "username": username, "password": password }

def create_error(id: int, msg: str):
    errors[id] = msg
    for task in tasks:
        if task.common_id == id:
            task.status = idents.TaskStatus.PROBLEM

def get_tasks_by_creator(creator: str):
    return [task for task in tasks if task.creator == creator]

def create_task(code: str, data: str, rows: int, creator: str):
    global TASK_ID
    parts = 0
    lines = data.split('\n')
    print(f"New task {TASK_ID}")
    for i in range(0, rows, COUNT_PER_WORKER):
        task = Task(TASK_ID, parts, code, lines[i:i + min(i + COUNT_PER_WORKER, rows)], min(i + COUNT_PER_WORKER, rows), idents.TaskStatus.PENDING, creator)
        tasks.append(task)
        parts += 1
    results[TASK_ID] = [[]] * parts
    errors[TASK_ID] = ""
    TASK_ID += 1

def update_task(common_id: int, idx: int, status: str):
    matches = [task for task in tasks if task.common_id == common_id and task.idx == idx]
    task = matches[0]
    task.status = status

def remove_task(task: Task):
    tasks.pop(tasks.index(task))

def get_tasks() -> list[Task]:
    return tasks

def update_worker_status(worker: str, current_task: int, current_task_idx: int):
    if worker not in workers.keys():
        workers[worker] = WorkerData(worker, time.time(), current_task, current_task_idx)
        print(f"New worker {worker}")
        return
    
    data = workers[worker]
    data.last_time_updated = time.time()
    data.current_task = current_task
    data.current_task_idx = current_task_idx

def save_all_data():
    save_tasks(tasks)
    save_users(users_db)

def save_tasks(tasks: list[Task]):
    for task in tasks:
        print(task.common_id)

def save_users(users: dict[str, dict[str, str]]):
    for user in users:
        print(user)
        
def remove_zombies():
    zombies = dict(filter(lambda kv: time.time() - kv[1].last_time_updated > 10, workers.items()))
    for z in zombies:
        zombie = zombies[z]
        if zombie.current_task >= 0:
            common_id = zombie.current_task
            idx = zombie.current_task_idx
            matches = [task for task in tasks if task.common_id == common_id and task.idx == idx]
            task = matches[0]
            # todo отобрать задачу
            task.status = idents.TaskStatus.PENDING
            print(f"Task {task.common_id} {task.idx} is returned to queue.")
        print(f"Remove zombie {z}")
        del workers[z] 

def get_idle_workers() -> dict[str, WorkerData]:
    return dict(filter(lambda kv: kv[1].current_task < 0, workers.items()))