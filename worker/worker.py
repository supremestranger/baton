import aiohttp
import asyncio
import fastapi
import os
import csv
import argparse
from datetime import datetime
import uvicorn
import socket
from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: fastapi.FastAPI):
    asyncio.create_task(send_status())
    yield

app = fastapi.FastAPI(title="Worker Node", lifespan=lifespan)
current_task = -1
current_task_idx = -1
port = 0
master_host = ""
id = ""

async def send_status(period: float = 5):
    while True:
        async with aiohttp.ClientSession() as s:
            try:
                async with s.post(f"{master_host}/status", json={"current_task": current_task, "current_task_idx": current_task_idx, "worker": id}) as resp:
                    print(str(datetime.now().timestamp()) + " Sent my health check. I'm working on task " + str(current_task))
            except Exception as e:
                print(e)
        await asyncio.sleep(period)

async def run_code(code: str, data: str):
    global current_task
    with open('./data.csv', 'w', newline='') as f:
        f.flush()
        f.writelines(data)
    
    try:
        await asyncio.to_thread(exec, code)  # blocking! to_thread
    except SyntaxError as e:
        print(f"Syntax error in provided code: {e}")
        # Можно отправить ошибку мастеру
        await send_error_result(f"Syntax error: {e}")
        return
    except Exception as e:
        print(f"Error executing code: {e}")
        await send_error_result(f"Execution error: {e}")
        return
    finally:
        current_task = -1

    await send_result()
    current_task = -1

async def send_result():
    res = ""
    with open('./res.csv', 'r', newline='') as f:
        res = f.read()
    
    async with aiohttp.ClientSession() as s:
        try:
            async with s.post(f"{master_host}/results", json={"data": res, "worker": id, "id": current_task, "number": current_task_idx}) as resp:
                print(str(datetime.now().timestamp()) + " Sent my results. I've been working on task " + str(current_task))
        except Exception as e:
            print(e)

async def send_error_result(msg: str):
    async with aiohttp.ClientSession() as s:
        try:
            async with s.post(f"{master_host}/error", json={"msg": msg, "worker": id, "id": current_task, "number": current_task_idx}) as resp:
                print(str(datetime.now().timestamp()) + " Sent an error. I've been working on task " + str(current_task))
        except Exception as e:
            print(e)

@app.post("/")
async def get_task(task: dict):
    global current_task
    global current_task_idx
    current_task = task["id"]
    current_task_idx = task["idx"]

    data = task["d"]
    code = task["c"]
    asyncio.create_task(run_code(code, data))

    return {"ok"}

def parse_arguments():
    parser = argparse.ArgumentParser(description='Worker Node')
    parser.add_argument('--port', type=int, default=8004, 
                       help='Port to run the worker on (default: 8004)')
    parser.add_argument('--master', type=str, default="http://localhost:8080",
                       help='Master node URL (default: http://localhost:8080)')
    return parser.parse_args()

if __name__ == "__main__":
    args = parse_arguments()
    
    port = args.port
    master_host = args.master

    try:
        hostname = socket.gethostname()
        ip_address = socket.gethostbyname(hostname)
        id = ip_address + ":" + str(port)
    except socket.error as e:
        print(f"Error: {e}")
    
    print(f"Starting worker node on port {port}")
    
    uvicorn.run(
        app,
        host=ip_address,
        port=port,
        log_level="info"
    )