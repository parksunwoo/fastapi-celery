from celery import Celery
from fastapi import FastAPI
from project import create_app

app = create_app()
celery = app.celery_app
# celery = Celery(
#     __name__,
#     broker="redis://localhost:6379/0",
#     backend="redis://localhost:6379/0",
# )


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.get("/hello/{name}")
async def say_hello(name: str):
    return {"message": f"Hello {name}"}

@celery.task
def divide(x, y):
    import time
    time.sleep(5)
    return x / y



