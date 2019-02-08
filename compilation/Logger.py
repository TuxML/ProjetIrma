# @file Logger.py

import time
import inspect

COLOR_SUCCESS = "\033[38;5;10m"
COLOR_ERROR = "\033[38;5;9m"
COLOR_DEFAULT = "\033[0m"
COLOR_DEBUG = "\033[38;5;7m"
COLOR_WARNING = "\033[38;5;11m"
_COLOR_TIME = "\033[38;5;12m"


class Logger:
    def __init__(self, user_output_file, stdout_file, stderr_file,
                 silent=False):
        self.__user_output_file = user_output_file
        self.__stdout_file = stdout_file
        self.__stderr_file = stderr_file
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
        calling_function = "[{}] ".format(inspect.stack()[1].function)
        if not self.__silent:
            print(
                "{}{}{}{}{}{}{}".format(
                    _COLOR_TIME,
                    date,
                    COLOR_DEBUG,
                    calling_function,
                    color,
                    message,
                    COLOR_DEFAULT),
                end=end,
                flush=True
            )
        self.__output.write("{}{}{}{}".format(
            date, calling_function, message, end))

    def reset_stdout_pipe(self):
        self.__stdout.close()
        self.__stdout = open(self.__stdout_file, 'w')

    def reset_stderr_pipe(self):
        self.__stderr.close()
        self.__stderr = open(self.__stderr_file, 'w')

    def reset_output_pipe(self):
        self.__output.close()
        self.__output = open(self.__user_output_file, 'w')

    def __del__(self):
        self.__output.close()
        self.__stdout.close()
        self.__stderr.close()
