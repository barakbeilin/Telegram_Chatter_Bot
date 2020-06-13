import asyncio
import common_utils
from .session_response_logic import SessionResposeLogicManager
TIMEOUT_SEC = 600


class ResponderManager:
    def __init__(self, redponder_ids, response_listeners):
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)

        lgm = common_utils.SingletonRotateLoggerManager()
        self.logger = lgm.create_logger("responder manager")
        self.redponder_ids = redponder_ids
        self.responder_queues = {}
        self.responders_coros = {}

        self.o2o_working_coros_name_and_id = common_utils.one_to_one_dict()
        self.unused_coros_names = set(redponder_ids)

        self.logger.info(self.unused_coros_names)

        self.response_listeners = response_listeners
        self.logic_manager = SessionResposeLogicManager(redponder_ids)
        list_of_resters = [
            lambda name=name: self.make_coro_ready_for_new_session(name)
            for name in self.redponder_ids]
        for name, reset_me in zip(self.redponder_ids, list_of_resters):
            self.set_responder_queue(name, asyncio.Queue())

            self.set_responder_coro(
                name, message_responder(
                    name,
                    self.get_responder_queue(name),
                    self.get_response_logic(name),
                    self.response_listeners,
                    reset_me))

        self.loop.create_task(main_coroutine(self, self.redponder_ids))

    def start(self):
        self.loop.run_forever()

    def make_coro_ready_for_new_session(self, name):
        if name not in self.o2o_working_coros_name_and_id.get_all_lefts():
            # handle if some how function was called on a coro whose name is
            # absent from the working_coros_name_by_id dictionary
            self.logger.debug("make_coro_ready_for_new_session->name:" + name + " " +
                              str(
                                  self.o2o_working_coros_name_and_id.get_all_lefts()))
            self.logger.debug(
                self.o2o_working_coros_name_and_id.get_all_lefts())
            self.logger.debug(
                self.o2o_working_coros_name_and_id.get_all_rights())

            self.logger.info("error in  make_coro_ready_for_new_session")
            return
        self.logger.debug(self.o2o_working_coros_name_and_id.get_all_lefts())
        self.logger.info("removed item from coro_name id mapping")
        self.o2o_working_coros_name_and_id.remove_item(left=name)
        self.logger.debug(self.o2o_working_coros_name_and_id.get_all_lefts())
        self.logger.info("restored name in unsued names set")
        self.unused_coros_names.add(name)
        self.logger.debug(self.unused_coros_names)

    def add_message_to_responder(self, msg, origin_id):
        self.logger.info(f"received  origin_id {origin_id}")

        if origin_id in self.o2o_working_coros_name_and_id.get_all_rights():
            coro_name =  \
                self.o2o_working_coros_name_and_id.get_value_by_key(origin_id)
            self.logger.info(f"using working coro {coro_name}")
        elif self.unused_coros_names:
            coro_name = self.unused_coros_names.pop()
            self.o2o_working_coros_name_and_id.add_item(coro_name, origin_id)
            self.logger.debug(
                self.o2o_working_coros_name_and_id.get_all_lefts())
            self.logger.debug(
                self.o2o_working_coros_name_and_id.get_all_rights())

            self.logger.info(f"using new coro {coro_name}")
        else:
            self.logger.info(f"no available coros!")
            return

        self.logger.info(
            "new msg"
            + str(msg)
            + "to"
            + str(self.responder_queues[coro_name]))
        asyncio.run_coroutine_threadsafe(
            self.responder_queues[coro_name].put(msg), self.loop)

        self.logger.info(
            "qsize of responder0 with the new msg   = " +
            str(self.responder_queues[coro_name].qsize()))

    def cancel_responder(self, name):
        self.responders_coros[name].cancel()

    def get_responder_queue(self, name):
        return self.responder_queues[name]

    def set_responder_queue(self, name, queue):
        self.responder_queues[name] = queue

    def get_responder_coro(self, name):
        return self.responders_coros[name]

    def set_responder_coro(self, name, coro):
        self.responders_coros[name] = coro

    def get_responder_coros(self):
        return self.responders_coros.values()

    def get_response_logic(self, name):
        return self.logic_manager.get_srl(name)


async def main_coroutine(manager, redponder_ids):
    lgm = common_utils.SingletonRotateLoggerManager()
    logger = lgm.create_logger("main_coroutine ")
    logger.info("main_coroutine wait for all responder to finish")
    await asyncio.gather(*manager.get_responder_coros())
    logger.info("main_coroutine all responder to finished")

    for task in asyncio.Task.all_tasks():
        task.cancel()


async def get_new_value_from_queue(queue, queue_output):
    queue_output["content"] = await queue.get()


async def message_responder(
        name, queue, session_logic, response_listeners, reset_me):
    lgm = common_utils.SingletonRotateLoggerManager()
    logger = lgm.create_logger(f"message responder {name}")
    while True:
        # Get a "work item" out of the queue.
        new_msg = {}
        logger.info(f'waiting for queue to fill')

        timeout_duration_sec = TIMEOUT_SEC
        if not session_logic.session_started():
            timeout_duration_sec = None
        logger.info(f'update timeout to {timeout_duration_sec} in coro {name}')
        try:
            queue_output = dict()
            await asyncio.wait_for(
                get_new_value_from_queue(queue, queue_output),
                timeout=timeout_duration_sec)
            new_msg = queue_output["content"]
            logger.info(queue_output)
            logger.info(new_msg)
        except asyncio.TimeoutError:
            session_logic.reset()
            reset_me()
            logger.info(
                f"""
                Responder reseted because of time out,after {
                    timeout_duration_sec}""")
            continue

        logger.info("new msg")
        response_content = session_logic.process_message(new_msg)
        response = {"chat_id": new_msg["id"], "text": response_content}
        logger.info(response)
        for response_listener in response_listeners:
            response_listener(response)
        # Notify the queue that the "work item" has been processed.
        queue.task_done()

        logger.info("new msg processes")
