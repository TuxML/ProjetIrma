"""
:author: PICARD Michaël
:version: 1
"""

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
    """A wrapper object that manages all the output.

    The logger object creates 3 files:

    - `user_output_file`: what is (or should be written) on user output
    - `stdout`: stdout of subprocess compilation
    - `stderr`: stderr of subprocess compilation

    If ``silent`` is True, each message pass to the user output is
    written in the file, but not display.

    :param user_output_file: path to the file to redirect the user's\
                             output
    :type user_output_file: str
    :param stdout_file: path to the file to redirect ``stdout`` to
    :type stdout_file: str
    :param stderr_file: path to the file to redirect ``stderr`` to
    :type stderr_file: str
    :param boot_file: path to the file to redirect the boot message\
                      output to
    :type boot_file: str
    :param silent: non verbose option. Default False
    :type silent: bool

    """
    def __init__(self, user_output_file, stdout_file, stderr_file,
                 boot_file, silent=False):
        """Constructor method
        """
        self.__user_output_file = user_output_file
        self.__stdout_file = stdout_file
        self.__stderr_file = stderr_file
        self.__boot_file = boot_file
        self.__output = open(user_output_file, mode='w')
        self.__stdout = open(stdout_file, mode='w')
        self.__stderr = open(stderr_file, mode='w')
        self.__boot = open(boot_file, mode='w')
        self.__silent = silent

    ## get_stdout_pipe
    # @author PICARD Michaël
    # @version 1
    # @brief Return the file descriptor for the standard output
    def get_stdout_pipe(self):
        """Return the file descriptor of ``stdout``        

        :return: a file descriptor
        :rtype: `io.TextIOWrapper`_

        .. _io.TextIOWrapper: https://docs.python.org/3/library/io.html#io.TextIOWrapper

        """
        return self.__stdout

    ## get_stderr_pipe
    # @author PICARD Michaël
    # @version 1
    # @brief Return the file descriptor for the standard error
    def get_stderr_pipe(self):
        """Return the file descriptor of ``stderr``

        :return: a file descriptor
        :rtype: `io.TextIOWrapper`_
        """
        return self.__stderr

    ## get_boot_pipe
    # @author PICARD Michaël
    # @version 1
    # @brief Return the file descriptor for the boot output
    def get_boot_pipe(self):
        """Return the file descriptor of the boot message output

        :return: a file descriptor
        :rtype: `io.TextIOWrapper`_
        """
        return self.__boot

    ## print_output
    # @author PICARD Michaël
    # @version 1
    # @brief Print your message on the output like a print method will do.
    # @details You can also choose a color for the output.
    def print_output(self, message, end="\n", color=COLOR_DEFAULT):
        """Prints a message (you can set its colour)

        :param message: the message to print
        :type message: str
        :param end: endline character. Default to ``"\\n"``
        :type end: str
        :param color: colour of the message. Default to\
        ``COLOR_DEFAULT``
        :type color: str
        """
        if not self.__silent:
            print(
                "{}{}{}".format(color, message, COLOR_DEFAULT),
                end=end,
                flush=True
            )
        self.__output.write("{}{}".format(message, end))
        self.__output.flush()

    ## timed_print_output
    # @author PICARD Michaël
    # @version 1
    # @brief Print your message on the output, preceded by the date and the
    # caller function of this method.
    # @details You can also choose a color for the output.
    def timed_print_output(self, message, end="\n", color=COLOR_DEFAULT):
        """Print date, the caller function and your message (kind of trace)

        :param message: message to print
        :type message: str
        :param end: endline character. Default to ``"\\n"``
        :type end: str
        :param color: colour of the message. Default to\
        ``COLOR_DEFAULT``
        :type color: str
        """
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
        self.__output.flush()

    ## reset_stdout_pipe
    # @author PICARD Michaël
    # @version 1
    # @brief Clear the stdout file.
    def reset_stdout_pipe(self):
        """Clear ``stdout`` file

        """
        self.__stdout.close()
        self.__stdout = open(self.__stdout_file, 'w')

    ## reset_stderr_pipe
    # @author PICARD Michaël
    # @version 1
    # @brief Clear the stderr file.
    def reset_stderr_pipe(self):
        """Clear ``stderr`` file

        """        
        self.__stderr.close()
        self.__stderr = open(self.__stderr_file, 'w')

    ## reset_boot_pipe
    # @author PICARD Michaël
    # @version 1
    # @brief Clear the boot file.
    def reset_boot_pipe(self):
        """Clear the file that contains the boot messages output

        """
        self.__stderr.close()
        self.__stderr = open(self.__boot_file, 'w')

    ## get_stdout_file
    # @author PICARD Michaël
    # @version 1
    # @brief Return the path of the stdout file.
    def get_stdout_file(self):
        """Gives the path to ``stdout`` file

        :return: path to ``stdout``
        :rtype: str
        """
        return self.__stdout_file

    ## get_stderr_file
    # @author PICARD Michaël
    # @version 1
    # @brief Return the path of the stderr file.
    def get_stderr_file(self):
        """Gives the path to ``stderr`` file

        :return: path to ``stderr``
        :rtype: str
        """
        return self.__stderr_file

    ## get_user_output_file
    # @author PICARD Michaël
    # @version 1
    # @brief Return the path of the user output file.
    def get_user_output_file(self):
        """Gives the path to user output file

        :return: path to user output file
        :rtype: str
        """        
        return self.__user_output_file

    ## get_boot_file
    # @author PICARD Michaël
    # @version 1
    # @brief Return the path of the boot file.
    def get_boot_file(self):
        """Gives the path to boot message output file

        :return: path to the boot message output file
        :rtype: str
        """
        return self.__boot_file

    # Assure that when deleting logger object, all file are closed.
    def __del__(self):
        """Close every previously opened streams

        """
        self.__output.close()
        self.__stdout.close()
        self.__stderr.close()
        self.__boot.close()
