import asyncio
import threading
import time


async def responder(queue, value):
    value["value"] = await queue.get()


async def worker(queue):
    value = dict()
    while True:
        print("waiting")
        # new_msg = await queue.get()
        await asyncio.wait_for(responder(queue, value), timeout=5)
        print(value)
        print("worked")


class wManager():
    def __init__(self):

        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)

        self.queue = asyncio.Queue()

        self.loop.create_task(worker(self.queue))

        self.msg = 0

    def add(self):
        print("queue Size Before"+str(self.queue.qsize()))
        asyncio.run_coroutine_threadsafe(self.queue.put(self.msg), self.loop)

        self.msg += 1
        print("queue Size After"+str(self.queue.qsize()))

    def start(self):
        self.loop.run_forever()


def print_after_sleep(manager):

    while True:
        print("hi!")
        time.sleep(1)
        manager.add()


def manager_runer(manager):
    manager.start()


if __name__ == "__main__":
    manager = wManager()
    manager_thread = threading.Thread(target=manager_runer, args=(manager,), daemon=True)

    sleepy_thread = threading.Thread(
        target=print_after_sleep, args=(manager,), daemon=True)

    sleepy_thread.start()
    manager_thread.start()
    sleepy_thread.join()
