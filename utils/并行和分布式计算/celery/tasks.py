from celery import Celery


app = Celery('tasks', broker='redis://localhost:6379/6', backend='redis://localhost:6379/7')


@app.task
def add(x, y):
    return x + y
