# @file Logger.py

import time

COLOR_SUCCESS = "\033[38;5;10m"
COLOR_ERROR = "\033[38;5;9m"
COLOR_DEFAULT = "\033[0m"
COLOR_DEBUG = "\033[38;5;7m"
COLOR_WARNING = "\033[38;5;11m"
_COLOR_TIME = "\033[38;5;12m"


class Logger:
    def __init__(self, user_output_file, stdout_file, stderr_file,
                 silent=False):
        self.__output = open(user_output_file, mode='w')
        self.__stdout = open(stdout_file, mode='w')
        self.__stderr = open(stderr_file, mode='w')
        self.__silent = silent

    def get_output_pipe(self):
        return self.__output

    def get_stdout_pipe(self):
        return self.__stdout

    def get_stderr_pipe(self):
        return self.__stderr

    def print_output(self, message, end="\n", color=COLOR_DEFAULT):
        if not self.__silent:
            print(
                "{}{}{}".format(color, message, COLOR_DEFAULT),
                end=end,
                flush=True
            )
        self.__output.write("{}{}".format(message, end))

    def timed_print_output(self, message, end="\n", color=COLOR_DEFAULT):
        date = time.strftime(
            "[%Y-%m-%d %H:%M:%S %Z] ",
            time.localtime(time.time())
        )
        if not self.__silent:
            print(
                "{}{}{}{}{}".format(
                    _COLOR_TIME,
                    date,
                    color,
                    message,
                    COLOR_DEFAULT),
                end=end,
                flush=True
            )
        self.__output.write("{}{}{}".format(date, message, end))

    def __del__(self):
        self.__output.close()
        self.__stdout.close()
        self.__stderr.close()
