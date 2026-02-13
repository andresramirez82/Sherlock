import sys
import os
import asyncio
import json
from fastapi import FastAPI, Request
from fastapi.responses import StreamingResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional

# Add the directory containing 'sherlock_project' to sys.path
# Since this file is in sherlock_project/sherlock-gui/app.py, the package root is grandmother
current_dir = os.path.dirname(os.path.abspath(__file__))
package_root = os.path.dirname(current_dir)
parent_of_package = os.path.dirname(package_root)
sys.path.append(parent_of_package)

from sherlock_project.sherlock import sherlock
from sherlock_project.sites import SitesInformation
from sherlock_project.notify import QueryNotify
from sherlock_project.result import QueryStatus

app = FastAPI(title="Sherlock Web UI")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class QueueNotify(QueryNotify):
    def __init__(self, queue: asyncio.Queue):
        super().__init__()
        self.queue = queue
        self.loop = asyncio.get_event_loop()

    def start(self, message=None):
        self.loop.call_soon_threadsafe(self.queue.put_nowait, {"type": "start", "message": message})

    def update(self, result):
        data = {
            "type": "update",
            "site_name": result.site_name,
            "site_url_user": result.site_url_user,
            "status": str(result.status),
            "query_time": result.query_time
        }
        self.loop.call_soon_threadsafe(self.queue.put_nowait, data)

    def finish(self, message=None):
        self.loop.call_soon_threadsafe(self.queue.put_nowait, {"type": "finish", "message": message})

@app.get("/scan/{username}")
async def scan(username: str):
    queue = asyncio.Queue()
    notify = QueueNotify(queue)
    
    # Load sites
    # sites = SitesInformation(...) # Avoid object usage as sherlock expects dicts
    data_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "resources", "data.json")
    with open(data_path, "r", encoding="utf-8") as f:
        site_data = json.load(f)
    site_data.pop("$schema", None)
    
    async def run_sherlock():
        # Sherlock is thread-based, so we run it in a thread
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, sherlock, username, sites.sites, notify)
        await queue.put(None) # Signal end

    async def event_generator():
        asyncio.create_task(run_sherlock())
        while True:
            data = await queue.get()
            if data is None:
                break
            yield f"data: {json.dumps(data)}\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")

# Mount static files
static_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "static")
if not os.path.exists(static_dir):
    os.makedirs(static_dir)

app.mount("/", StaticFiles(directory=static_dir, html=True), name="static")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
