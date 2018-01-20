from celery import Celery


app = Celery(
    'tasks', broker = 'pyamqp://localhost', backend = 'rpc://')
