
import os
import logging
from logging import FileHandler
import threading
import time
import shutil


class SingletonRotateLoggerManager():

    class __RotateLoggerManager():
        FILE_ROTATION_SIZE_THRESH = 1000*1000
        TIME_SLEEP_SEC_LOGGER = 360
        INIT_NUMBER_OF_COPIES = 1

        def __init__(self):
                # hold the number of rotation of the log file
            self.log_file_names = {}
            file_wathcer_thread = threading.Thread(
                target=self._file_watcher, daemon=True)
            file_wathcer_thread.start()

        def _file_watcher(self):
            logger = self.create_logger(logger_name="logger_manager_filewatch")
            while True:
                # handle except due to dictionary size change during iteration
                log_file_names = dict(self.log_file_names)
                for file_name in log_file_names:
                    file_stats = os.stat(file_name)

                    if file_stats.st_size > self.FILE_ROTATION_SIZE_THRESH:
                        logger.info(
                            "log rotation of "
                            + file_name+"on size "
                            + file_stats.st_size)
                        shutil.copyfile(
                            file_name, file_name+str(log_file_names[file_name]))
                        logger.info(
                            f"""
                            shutil.copyfile({file_name}, {
                                file_name+str(log_file_names[file_name])})""")
                        self.log_file_names[file_name] += 1

                        # erase log file content after rotating
                        with open(file_name, 'w'):
                            pass

                time.sleep(self.TIME_SLEEP_SEC_LOGGER)

        def create_logger(self, logger_name="Main",
                          logging_file_name="main_log"):

            # create logger with 'spam_application'
            logger = logging.getLogger(logger_name)
            logger.setLevel(logging.DEBUG)

            # create file handler which logs even debug messages
            log_file_name = logging_file_name+'.log'
            self.log_file_names.setdefault(
                log_file_name, self.INIT_NUMBER_OF_COPIES)
            fh = FileHandler(log_file_name, mode='a', encoding='utf-8', delay=0)
            fh.setLevel(logging.DEBUG)

            # create console handler
            ch = logging.StreamHandler()
            ch.setLevel(logging.DEBUG)

            # create formatter and add it to the handlers
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            fh.setFormatter(formatter)
            ch.setFormatter(formatter)
            # add the handlers to the logger
            logger.addHandler(fh)
            logger.addHandler(ch)
            return logger

    instance = None

    def __init__(self):
        if not SingletonRotateLoggerManager.instance:
            SingletonRotateLoggerManager.instance = \
                SingletonRotateLoggerManager.__RotateLoggerManager()

    def create_logger(self, logger_name="Main", logging_file_name="main_log"):
        return self.instance.create_logger(logger_name, logging_file_name)

    def __repr__(self):
        return repr(self.instance)


class one_to_one_dict:
    """
    Implements a one to one look up table.

    """

    def __init__(self):
        self._left_by_right = {}
        self._right_by_left = {}

    def get_all_lefts(self):
        return self._right_by_left.keys()

    def get_all_rights(self):
        return self._left_by_right.keys()

    def add_item(self, left, right):
        self._right_by_left[left] = right
        self._left_by_right[right] = left

    def get_value_by_key(self, key):
        """
        return the value mapped by the key.
        """
        if key in self.get_all_lefts():
            # input 'key' is a left key
            return self._right_by_left[key]
        # input 'key' is a left key
        return self._left_by_right[key]

    def remove_item(self, left=None, right=None):
        """
        remove item by one of possible keys,
        no need to state both left and right.
        """
        if left:
            right_key = self._right_by_left[left]
            left_key = left
        else:
            right_key = right
            left_key = self._left_by_right[right]

        del self._left_by_right[right_key]
        del self._right_by_left[left_key]


if __name__ == "__main__":
    r1 = SingletonRotateLoggerManager()
    r2 = SingletonRotateLoggerManager()
    print(r1)
    print(r2)
    lg1 = r1.create_logger(logger_name="a1", logging_file_name="a")
    lg2 = r2.create_logger(logger_name="a2", logging_file_name="a")
    while True:
        lg1.info(["s1" for i in range(100)])
        lg1.info(["s2" for i in range(100)])
        time.sleep(1)
