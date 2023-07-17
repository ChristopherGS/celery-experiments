from celery import group
from celery.result import AsyncResult
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from worker import startup_task, reducer_task, async_parallel_task, sync_parallel_task

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

N_REDUCER_TASKS = 100
N_LONG_TASKS = 10


@app.get("/")
def home(request: Request):
    return templates.TemplateResponse("home.html", context={"request": request})


@app.post("/single-task", status_code=201)
async def run_single_task(id: int):

    # Each task is offloaded
    # delay is **argument version of apply_async().
    task1 = startup_task.delay(id)

    return JSONResponse({"task_status": 'task is running', 'task_id': task1.id})


@app.post("/tasks-group-async", status_code=201)
async def run_task_group_async(id: int):
    task1 = startup_task.delay(id)
    for i in range(N_LONG_TASKS):
        await async_parallel_task(i)
    task3 = group(reducer_task.s(i) for i in range(N_REDUCER_TASKS)).apply_async()
    task4 = reducer_task.delay(id)

    return JSONResponse({"task_status": 'tasks running',
                         'task1': task1.id,
                         'task2': 'async',
                         'task3': task3.id,
                         'task4': task4.id})


@app.post("/tasks-group-sync", status_code=201)
async def run_task_group_sync(id: int):
    task1 = startup_task.delay(id)
    for i in range(N_LONG_TASKS):
        sync_parallel_task.delay(id)
    # task2 = group(sync_parallel_task.s(i) for i in range(N_LONG_TASKS)).apply_async()
    task3 = group(reducer_task.s(i) for i in range(N_REDUCER_TASKS)).apply_async()
    task4 = reducer_task.delay(id)

    return JSONResponse({"task_status": 'tasks running',
                         'task1': task1.id,
                         'task2': 'sync',
                         'task3': task3.id,
                         'task4': task4.id})


@app.get("/tasks/{task_id}")
async def get_status(task_id):
    task_result = AsyncResult(task_id)
    result = {
        "task_id": task_id,
        "task_status": task_result.status,
        "task_result": task_result.result
    }
    return JSONResponse(result)
