import asyncio
import threading
import time

class ThreadPoolClient:
    @classmethod
    def create_task_loop(cls, func, interval_seconds):
        thread = threading.Thread(target=cls.task_loop, args=(func, interval_seconds), daemon=True)
        thread.start()

    @staticmethod
    def create_async_task(func):
        asyncio.create_task(func())

    @staticmethod
    def task_loop(func, interval_seconds):
        while True:
            time.sleep(interval_seconds)
            func()