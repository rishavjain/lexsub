'''Split the huge input files into multiple input files and generate the parser commands.'''

from config import read_config_file
from config import create_path
from generate_commands import generate_parser_commands
from generate_commands import decode_parser_cmd
from generate_commands import decode_qsub_cmd

import os
import time
import sys
import threading
import logging
import logging.config
import subprocess

LOG_FILES_FOLDER = 'log'


class ParserThread(threading.Thread):
    def __init__(self, _params, _id, _command, _output_path, _platform):
        threading.Thread.__init__(self)
        self.params = _params
        # self.input_file = _input_file
        self.output_path = _output_path
        self.thread_id = str(_id)
        self.logger = logging.getLogger(self.thread_id)
        self.command = _command
        self.platform = _platform

    def run(self):
        parser_process = None
        if sys.platform.find('win') != -1:
            parser_process = subprocess.Popen(self.command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                                              shell=True)

        elif sys.platform.find('linux') != -1:
            global LOG_FILES_FOLDER
            cmd = decode_qsub_cmd(_params=self.params, _log_file=LOG_FILES_FOLDER + self.thread_id + '.log',
                                  _cmd=self.command)

            self.logger.info('qsub_cmd = ' + cmd)

            parser_process = subprocess.Popen(cmd, stdout=subprocess.PIPE,
                                              stderr=subprocess.STDOUT, shell=True)

        if parser_process is not None:
            for line in parser_process.stdout:
                self.logger.info(line.decode('utf-8'))

            parser_process.stdout.close()
            parser_process.wait()


def __print_usage_msg__():
    print('invalid usage')
    sys.exit()


def __get_arguments__():
    try:
        c_idx = sys.argv.index('-config')
        _config_file = sys.argv[c_idx + 1]
    except (ValueError, IndexError):
        _config_file = None
        __print_usage_msg__()

    try:
        i_idx = sys.argv.index('-input')
        _input = sys.argv[i_idx + 1]
    except (ValueError, IndexError):
        _input = None

    try:
        o_idx = sys.argv.index('-out_dir')
        _output_path = sys.argv[o_idx + 1]
    except (ValueError, IndexError):
        _output_path = None

    return _config_file, _input, _output_path


if __name__ == '__main__':
    config_file, input_arg, output_path = __get_arguments__()

    logging.config.fileConfig(fname=config_file)

    params = read_config_file(_config_file=config_file)
    logging.info(str(params))

    commands, abs_output_path = generate_parser_commands(_params=params)

    logging.info('commands = ' + str(commands))

    if sys.platform.find('win') != -1:
        platform = 'win'
    elif sys.platform.find('linux') != -1:
        platform = 'linux'
    else:
        logging.info('OS unsupported')
        sys.exit()

    logging.info('platform = ' + platform)

    LOG_FILES_FOLDER = abs_output_path + '/' + LOG_FILES_FOLDER + '/'
    create_path(path=LOG_FILES_FOLDER)

    for command in commands:
        ParserThread(_id=commands.index(command), _params=params, _command=command,
                     _output_path=abs_output_path, _platform=platform).start()
        # break

    while threading.active_count() > 1:
        logging.debug('active thread count = %d', threading.active_count())
        time.sleep(2)

    logging.info('parsing successfully complete')
    logging.shutdown()
