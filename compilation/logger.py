# @file Logger.py

import time
import inspect

COLOR_SUCCESS = "\033[38;5;10m"
COLOR_ERROR = "\033[38;5;9m"
COLOR_DEFAULT = "\033[0m"
COLOR_DEBUG = "\033[38;5;7m"
COLOR_WARNING = "\033[38;5;11m"
_COLOR_TIME = "\033[38;5;12m"


## Logger
# @author PICARD Michaël
# @version 1
# @brief A wrapper object in order to manage all the output.
# @details The logger object create 3 file:
# - user_output_file : what is (or should be write) on user output
# - stdout : stdout of subprocess compilation
# - stderr : stderr of subprocess compilation
# If silent is True, each message pass to the user output is write in the file,
# but not display.
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

    ## get_stdout_pipe
    # @author PICARD Michaël
    # @version 1
    # @brief Return the file descriptor for the standard output
    def get_stdout_pipe(self):
        return self.__stdout

    ## get_stderr_pipe
    # @author PICARD Michaël
    # @version 1
    # @brief Return the file descriptor for the standard error
    def get_stderr_pipe(self):
        return self.__stderr

    ## print_output
    # @author PICARD Michaël
    # @version 1
    # @brief Print your message on the output like a print method will do.
    # @details You can also choose a color for the output.
    def print_output(self, message, end="\n", color=COLOR_DEFAULT):
        if not self.__silent:
            print(
                "{}{}{}".format(color, message, COLOR_DEFAULT),
                end=end,
                flush=True
            )
        self.__output.write("{}{}".format(message, end))

    ## timed_print_output
    # @author PICARD Michaël
    # @version 1
    # @brief Print your message on the output, preceded by the date and the
    # caller function of this method.
    # @details You can also choose a color for the output.
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

    ## reset_stdout_pipe
    # @author PICARD Michaël
    # @version 1
    # @brief Clear the stdout file.
    def reset_stdout_pipe(self):
        self.__stdout.close()
        self.__stdout = open(self.__stdout_file, 'w')

    ## reset_stderr_pipe
    # @author PICARD Michaël
    # @version 1
    # @brief Clear the stderr file.
    def reset_stderr_pipe(self):
        self.__stderr.close()
        self.__stderr = open(self.__stderr_file, 'w')

    ## get_stdout_file
    # @author PICARD Michaël
    # @version 1
    # @brief Return the path of the stdout file.
    def get_stdout_file(self):
        return self.__stdout_file

    ## get_stderr_file
    # @author PICARD Michaël
    # @version 1
    # @brief Return the path of the stderr file.
    def get_stderr_file(self):
        return self.__stderr_file

    ## get_user_output_file
    # @author PICARD Michaël
    # @version 1
    # @brief Return the path of the user output file.
    def get_user_output_file(self):
        return self.__user_output_file

    # Assure that when deleting logger object, all file are closed.
    def __del__(self):
        self.__output.close()
        self.__stdout.close()
        self.__stderr.close()
