import asyncio
import os
import random
from time import sleep
from celery import group, chain
from loguru import logger
from asgiref.sync import async_to_sync, sync_to_async

from celery import Celery


celery = Celery(__name__)
celery.conf.broker_url = os.environ.get("CELERY_BROKER_URL", "redis://localhost:6379")
celery.conf.result_backend = os.environ.get("CELERY_RESULT_BACKEND", "redis://localhost:6379")


@celery.task()
def startup_task(id_):
    logger.info('-----> starter task started')
    sleep(2)
    logger.info('-----> starter task complete')
    return True


async def call_chatgpt_or_whatever():
    await asyncio.sleep(10)

# Converts a Celery tasks to an async function
def task_to_async(task):
    async def wrapper(*args, **kwargs):
        delay = 0.1
        async_result = await sync_to_async(task.delay)(*args, **kwargs)
        while not async_result.ready():
            await asyncio.sleep(delay)
            delay = min(delay * 1.5, 2)  # exponential backoff, max 2 seconds
        return async_result.get()
    return wrapper


@task_to_async
@celery.task()
def async_parallel_task(id_):
    logger.info('-------> parallel task started %s' % id_)
    # Deliberately variable to mimic 3rd party API uncertainty
    call_chatgpt_or_whatever()
    logger.info('-------> parallel task complete %s' % id_)
    return True


@celery.task()
def sync_parallel_task(id_):
    logger.info('-------> parallel task started %s' % id_)
    sleep(10)
    logger.info('-------> parallel task complete %s' % id_)
    return True


@celery.task()
def reducer_task(id_):
    logger.info('-----> reducer task started')
    # Deliberately short - idea being that when parallel task is paused it switches to this.
    sleep(0.3)
    logger.info('-----> reducer task complete')
    return True