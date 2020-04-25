import threading
from Telebot import telegram_bot, ngrok_starter
import common_utils
from producer.session_responder_fiber import ResponderManager

NUM_OF_RESPONDERS = 100


def run_telegram_bot(name, telegram_listener, host='localhost', port=8080):
    logger.info("Thread %s: starting", name)

    telegram_listener.run(host=host, port=port)


def create_session_fiber_manager(manager):
    manager.start()


def run_ngrok():
    ngrok_starter.run_ngrok()


def return_on_key_press():
    input("Press Enter to end \n")


if __name__ == "__main__":
    lgm = common_utils.SingletonRotateLoggerManager()
    logger = lgm.create_logger()
    logger.info("before creating thread")

    ngrok_thread = threading.Thread(target=run_ngrok, daemon=True)

    key_press_thread = threading.Thread(
        target=return_on_key_press, daemon=True)

    telegram_listener = telegram_bot.TelegramBot()
    response_listeners = telegram_listener.get_response_handlers()

    redponder_ids = [f"{num}" for num in range(NUM_OF_RESPONDERS)]
    manager = ResponderManager(redponder_ids, response_listeners)
    fiber_manager_thread = threading.Thread(
        target=create_session_fiber_manager, args=(manager,), daemon=True)

    telegram_listener.add_new_msg_from_telegram_listeners(
        [manager.add_message_to_responder])
    telegram_bot_thread = threading.Thread(
        target=run_telegram_bot,
        kwargs={
            "name": 1, "port": 8080,
            "telegram_listener": telegram_listener},
        daemon=True)

    logger.info("before running threads")

    key_press_thread.start()

    ngrok_thread.start()
    fiber_manager_thread.start()
    telegram_bot_thread.start()
    logger.info("wait for the key press")
    key_press_thread.join()
    logger.info("telegram_bot_thread ended")
