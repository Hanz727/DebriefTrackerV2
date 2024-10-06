import inspect
import os
from datetime import datetime


def _get_longest_filename_in_dir(dir_=os.getcwd()):
    max_length = 0
    for file in os.listdir(dir_):
        if file[0] == ".":
            continue

        filename, ext = os.path.splitext(file)
        length = len(dir_) + len(filename) + len(ext) + 1

        if ext == ".py" and length > max_length:
            max_length = length
            continue

        # if is folder
        if ext != "" or filename in ["venv", "node_modules"]:
            continue

        max_length_in_subdir = _get_longest_filename_in_dir(dir_ + "\\" + filename)

        if max_length_in_subdir > max_length:
            max_length = max_length_in_subdir

    return max_length


_longest_python_file_name = _get_longest_filename_in_dir()


def get_function_caller(depth) -> str:
    # Get the current frame
    current_frame = inspect.currentframe()

    # Get the caller's frame (two levels up in the stack)
    caller_frame = current_frame
    for _ in range(depth):
        caller_frame = caller_frame.f_back

    # Get the caller's function name
    caller_function_name = caller_frame.f_code.co_name

    # Get the caller's line number
    caller_line_number = str(caller_frame.f_lineno)

    # Get the caller's file name
    caller_file_name = caller_frame.f_code.co_filename

    caller_file_name += " " * (_longest_python_file_name - len(caller_file_name))

    return ("[" + caller_file_name + "] [" + caller_function_name + " " * (30 - len(caller_function_name)) + "] ["
            + caller_line_number + " " * (3 - len(caller_line_number)) + "] ")


def log(msg_type: str, msg: str, depth: int) -> None:
    date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_msg = "[" + date + "] " + get_function_caller(depth) + "[" + msg_type + " " * (7 - len(msg_type)) + "] " + msg
    print(log_msg)

    with open("logs/" + date.split(" ")[0] + "-logs.txt", "a") as f:
        f.write(log_msg + "\n")


def error(msg, depth=3):
    '''

    :param msg:
    :param depth: depth of function in the call tree from the Logger.log(). i.e. main -> Logger.info() -> logger.log() means main is at depth 3.
    :return: None
    '''
    log("ERROR", str(msg), depth)


def warning(msg, depth=3):
    '''

    :param msg:
    :param depth: depth of function in the call tree from the Logger.log(). i.e. main -> Logger.info() -> logger.log() means main is at depth 3.
    :return: None
    '''
    log("WARNING", str(msg), depth)


def info(msg, depth=3):
    '''

    :param msg:
    :param depth: depth of function in the call tree from the Logger.log(). i.e. main -> Logger.info() -> logger.log() means main is at depth 3.
    :return: None
    '''
    log("INFO", str(msg), depth)
