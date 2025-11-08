import aiohttp
import asyncio
import fastapi
import os
import csv
import argparse
from datetime import datetime
import uvicorn
from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: fastapi.FastAPI):
    asyncio.create_task(send_status())
    yield

app = fastapi.FastAPI(title="Worker Node", lifespan=lifespan)
current_task = -1
port = 0
number = -1
master_host = ""

async def send_status(period: float = 5):
    while True:
        async with aiohttp.ClientSession() as s:
            try:
                async with s.post(f"{master_host}/status", json={"current_task": current_task, "worker": port}) as resp:
                    print(str(datetime.now().timestamp()) + " Sent my health check. I'm working on task " + str(current_task))
            except Exception as e:
                print(e)
        await asyncio.sleep(period)

async def run_code(code: str, data: str):
    global current_task
    with open('./data.csv', 'w', newline='') as f:
        f.flush()
        f.writelines(data)
    
    await asyncio.to_thread(exec, code) # blocking! to_thread
    await send_result()
    current_task = -1

async def send_result():
    res = ""
    with open('./res.csv', 'r', newline='') as f:
        res = f.read()
    
    print(res)
    
    async with aiohttp.ClientSession() as s:
        try:
            async with s.post(f"{master_host}/results", json={"data": res, "worker": port, "number": number}) as resp:
                print(str(datetime.now().timestamp()) + " Sent my results. I've been working on task " + str(current_task))
        except Exception as e:
            print(e)

@app.post("/")
async def get_task(task: dict):
    global current_task
    global number
    current_task = task["id"]
    
    data = task["d"]
    code = task["c"]
    number = task["n"]
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
    
    print(f"Starting worker node on port {port}")
    
    uvicorn.run(
        app,
        host="127.0.0.1",
        port=port,
        log_level="info"
    )