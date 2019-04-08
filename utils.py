import errno
import os
import subprocess
import types

class BuildError(Exception):
    pass

class NullLogger:
    """
    Default logger that does nothing but doesn't break 'logger.info(msg)' type calls.
    """

    def __init__(self):
        pass

    def debug(self, msg):
        pass

    def info(self, msg):
        pass

    def warning(self, msg):
        pass

    def error(self, msg):
        pass

    def critical(self, msg):
        pass

def execute_shell_command(command, logger=None, logging_level='info', **kwargs):
    """
    Execute the given command.
    :param command: The command as a list of parameter strings or a string.
    :param logger: Logger to use.
    :param logging_level: Logging level to use.
    :param kwargs: Passed to Popen.
    """
    if not logger:
        logger = NullLogger()

    if isinstance(command, types.StringTypes):
        command = command.split(' ')

    logger.info('+ Executing "' + ' '.join(command) + '" in ' + os.getcwd())

    try:
        proc = subprocess.Popen(command, bufsize=1, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, **kwargs)
    except OSError as e:
        if e[0] == errno.ENOENT:
            raise BuildError("Could not execute \"%s\".\n"
                             "Please verify that it's installed and accessible from your current path "
                             "by executing \"%s\".\n" % (command[0], command[0]))
        else:
            raise e

    output = []
    with proc.stdout:
        for line in iter(proc.stdout.readline, b''):
            line = line.strip()
            output += line
            if logger:
                getattr(logger, logging_level)(line)

    proc.wait()

    if proc.returncode != 0:
        raise BuildError('Failed to execute command "' + ' '.join(command) + '" in ' + os.getcwd())

    return output
