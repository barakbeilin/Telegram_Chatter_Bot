import json
import common_utils
from producer.data.session_contents import *
import os


class SessionResposeLogicManager:
    def __init__(self, srl_names):

       
        self.content = HebrewContent()
        self.session_repsone_logic = {}
        for name in srl_names:
            self.session_repsone_logic[name] = SessionResponseLogic(
                self.content, name)

    def get_srl(self, name):
        return self.session_repsone_logic[name]

    def reset_srl(self, name, new_sessionee):
        self.session_repsone_logic[name].reset()


class SessionResponseLogic:
    def __init__(self, content, name="", sessionsee_name=""):
        self.name = name
        lgm = common_utils.SingletonRotateLoggerManager()
        self.logger = lgm.create_logger(
            logger_name='-'.join(("session_logic", self.name)))
        self.contet = content
        self.reset(sessionsee_name)
        self._current_state = None
        self._new_state = None

    def session_started(self):
        """
        return if session not started.
        uses the msg counter which should be 0 after 'reset'
        """
        return self.msg_counter > 0

    def reset(self, new_sessionee_name=""):
        """
        prepare the logic for new session.
        """
        self.msg_counter = 0
        self.context = Context(self.contet, self.name)
        self.logger.info(f"Entered { self.context.state} state")

        self.sessionee = new_sessionee_name
       

    def process_message(self, message):

        self.msg_counter += 1

        self.logger.info(
            f"Recieved msg number {self.msg_counter} from {self.sessionee}")
        self.logger.info(message)

        input_for_logic = message['content']

        # first message is a greeting so it content is non relevant
        if self.msg_counter == 1:
            return self.return_on_state_change(
                True,
                str(self.context.get_state_options_content()))

        if self.context.is_legal_input(input_for_logic):
            self.context.handle(input_for_logic)
            self.logger.info(f"Entered { self.context.state} state")

            new_state = self.context.state
            if new_state != self._current_state:
                state_chagned = True
                self._current_state = new_state
            else:
                state_chagned = False
            return self.return_on_state_change(
                state_chagned,
                str(self.context.get_state_options_content()))
        return self.context.illegal_input_response()

    def return_on_state_change(self, state_changed, response):
        if state_changed:
            return response
        return ""
