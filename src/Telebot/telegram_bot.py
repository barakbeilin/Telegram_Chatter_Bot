import requests
import common_utils
from bottle import Bottle, response, request as bottle_request
import time
from . import ngrok_consts


class BotHandlerMixin:
    BOT_URL = None

    def get_chat_id(self, message_from_telegram):
        """
        Method to extract chat id from telegram request.
        If the msg is messed up return non existign 0 id.
        The id is a integer
        """

        chat_id = 0
        if 'message' in message_from_telegram:
            chat_id = message_from_telegram['message']['chat']['id']

        return chat_id

    def get_message(self, message_from_telegram):
        """
        Method to extract message id from telegram request.
        """
        # TODO:  when i edited by accident the message on Telegram then
        # data strcuture was changed and didnt include "message" key any more
        # requires further attention
        message_text = ""
        if 'message' in message_from_telegram:
            message_text = message_from_telegram['message']['text']

        return message_text

    def send_message(self, message_to_telegram):
        """
        message_from_telegram should be json which includes at least
        `chat_id` and `text`
        """
        self.logger.info(message_to_telegram)
        message_url = self.BOT_URL + 'sendMessage'
        message_to_telegram['parse_mode'] = 'Markdown'
        requests.post(message_url, json=message_to_telegram)

    def is_time_stamp_is_in_the_past(self, message_from_telegram):
        PAST_TIME_THRESHOLD_SEC = 60
        if "date" in message_from_telegram["message"]:
            msg_time = int(message_from_telegram["message"]["date"])
            curr_time = int(time.time())
            message_in_the_past = \
                abs(curr_time-msg_time) > PAST_TIME_THRESHOLD_SEC
            if message_in_the_past:
                self.logger.info(
                    "dispose of old message"
                    + str(self.get_message(message_from_telegram)
                          + "time from mesage"
                          + str(msg_time)
                          + "curr time "
                          + str(curr_time)))
            return message_in_the_past
        return True


class TelegramBot(BotHandlerMixin, Bottle):
    BOT_URL = \
        f"https://api.telegram.org/{ngrok_consts.SECRET_KEY}/"

    def __init__(self, *args, post_callback_list=[], **kwargs):
        super(TelegramBot, self).__init__()
        lgm = common_utils.SingletonRotateLoggerManager()
        self.logger = lgm.create_logger(logger_name="bot")
        self.post_callback_list = []
        self.post_callback_list.append(print)
        self.post_callback_list.extend(post_callback_list)
        self.logger.info("call back list is " + str(self.post_callback_list))

        self.route('/', callback=self._post_handler, method="POST")

    def add_new_msg_from_telegram_listeners(self, new_listeners=[]):
        self.post_callback_list.extend(new_listeners)

    def get_response_handlers(self):
        return [self.send_message]

    def _post_handler(self):
        data = bottle_request.json

        if self.is_time_stamp_is_in_the_past(data):
            return
        message = self.get_message(data)
        chat_id = self.get_chat_id(data)
        self.logger.info(
            f"recieved message from {chat_id} with content {message}")
        for callback in self.post_callback_list:
            callback({"id": chat_id, "content": message}, chat_id)


if __name__ == '__main__':

    app = TelegramBot()
    app.run(host='localhost', port=8080)
