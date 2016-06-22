# ##### reading configuration file

import configparser
import os
import time
import errno
import subprocess
import sys
import threading
import logging
import logging.config

LOG_FILES_FOLDER = 'log'
GEN_FILES_FOLDER = 'gen'
UKWAC_NUM_LINES_FILE = 51


class Params:
    base_path = None
    parser_path = None
    parser_class = None
    parser_annotators = None
    parser_memory = None
    parser_cmdFmtStr = None
    input_type = None
    input_file = None
    input_filepath = None
    output_path = None
    qsub_mem = None
    qsub_rmem = None
    qsub_mail = None
    qsub_mail_option = None
    qsub_cmdFmtStr = None

    def __str__(self):
        return 'Params -' \
               '\n\tbase_path = {}' \
               '\n\tparser_path = {}' \
               '\n\tparser_class = {}' \
               '\n\tparser_annotators = {}' \
               '\n\tparser_memory = {}' \
               '\n\tparser_cmdFmtStr = {}' \
               '\n\tinput_type = {}' \
               '\n\tinput_file = {}' \
               '\n\tinput_filepath = {}' \
               '\n\toutput_path = {}' \
               '\n\tqsub_mem = {}' \
               '\n\tqsub_rmem = {}' \
               '\n\tqsub_mail = {}' \
               '\n\tqsub_mail_option = {}' \
               '\n\tqsub_cmdFmtStr = {}' \
            .format(self.base_path, self.parser_path, self.parser_class, self.parser_annotators, self.parser_memory,
                    self.parser_cmdFmtStr, self.input_type, self.input_file, self.input_filepath, self.output_path,
                    self.qsub_mem, self.qsub_rmem, self.qsub_mail, self.qsub_mail_option, self.qsub_cmdFmtStr)


def read_config_file(l_config_file):
    config = configparser.ConfigParser(interpolation=configparser.ExtendedInterpolation(),
                                       inline_comment_prefixes=(';',))
    config.read(l_config_file)  # 'desktop.ini'

    l_params = Params()

    l_params.base_path = config['paths']['base_path']
    l_params.parser_path = config['paths']['parser_path']
    l_params.parser_class = config['parser']['class']
    l_params.parser_annotators = config['parser']['annotators']
    l_params.parser_memory = config['parser']['max_mem']
    l_params.parser_cmdFmtStr = config['parser']['cmdFmtStr']
    l_params.input_type = config['input']['type']

    if config.has_option('input', 'file'):
        l_params.input_file = config['input']['file']
    else:
        l_params.input_filepath = config['input']['filepath']

    l_params.output_path = config['output']['path']

    l_params.qsub_mem = config['qsub']['mem']
    l_params.qsub_rmem = config['qsub']['rmem']
    l_params.qsub_mail = config['qsub']['mail']
    l_params.qsub_mail_option = config['qsub']['mail_option']
    l_params.qsub_cmdFmtStr = config['qsub']['cmdFmtStr']

    return l_params


def create_path(path):
    if not os.path.exists(path):
        try:
            os.makedirs(path)
        except OSError as exc:  # Guard against race condition
            if exc.errno != errno.EEXIST:
                raise


def generate_ukwac_input_files(l_params):
    # generating tuple of input files
    if l_params.input_file is not None:
        input_files = [l_params.input_file, ]
    else:
        input_files = [l_params.input_filepath + '/' + file_name for file_name in os.listdir(l_params.input_filepath)]

    # defining required paths and files
    out_path = os.path.abspath(l_params.output_path) + '/' + time.strftime('%m-%d-%H-%M-%S') + '/'

    idx = 1  # index for generated input file
    gen_files_path = out_path + GEN_FILES_FOLDER + '/'
    create_path(gen_files_path)
    out_obj = open(gen_files_path + 'in' + str(idx) + '.txt', 'w', encoding='iso-8859-15')

    l_filelist = ()

    out_idx = 0
    for input_file in input_files:
        in_obj = open(input_file, encoding='iso-8859-15')

        line_idx = 0
        out_idx = 0
        for line in in_obj:
            if line_idx % 2 == 1:
                out_obj.write(line)
                out_idx += 1

                if out_idx % UKWAC_NUM_LINES_FILE == 0:
                    out_obj.close()
                    l_filelist += (os.path.abspath(out_obj.name),)

                    idx += 1

                    out_obj = open(gen_files_path + 'in' + str(idx) + '.txt', 'w', encoding='iso-8859-15')
                    out_idx = 0

            line_idx += 1

    out_obj.close()

    if out_idx == 0:
        os.remove(out_obj.name)
    else:
        l_filelist += (os.path.abspath(out_obj.name),)

    return l_filelist, os.path.abspath(out_path)


def generate_parser_cmd(l_params, l_input_file, l_abs_output_path):
    return l_params.parser_cmdFmtStr.format(l_params.parser_memory, l_params.parser_path, l_params.parser_class,
                                            l_params.parser_annotators, l_input_file, l_abs_output_path)


def generate_qsub_cmd(l_params, l_cmd):
    if l_params.qsub_mail == 'yes':
        l_cmd = '-m {} -M {} {}'.format(l_params.qsub_mail_option, 'rjain2@sheffield.ac.uk', l_cmd)

    return l_params.qsub_cmdFmtStr.format(l_params.qsub_mem, l_params.qsub_rmem, l_cmd)


class ParserThread(threading.Thread):
    def __init__(self, l_params, l_input_file, l_output_path):
        threading.Thread.__init__(self)
        self.params = l_params
        self.input_file = l_input_file
        self.output_path = l_output_path
        self.thread_id = os.path.basename(l_input_file)
        self.logger = logging.getLogger(self.thread_id)

    def run(self):
        cmd = generate_parser_cmd(self.params, self.input_file, self.output_path)
        self.logger.info('parser_cmd = ' + cmd)

        cmd = generate_qsub_cmd(self.params, cmd)
        self.logger.info('qsub_cmd = ' + cmd)

        os.chdir(self.params.parser_path)
        #cmd = 'module load apps/java/1.8u71;' #+ cmd
        parser_process = subprocess.Popen('echo a', stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=True)
        # parser_process = subprocess.Popen(['parsing.bash', cmd], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=True)

        for line in iter(parser_process.stdout.readline, ''):
            self.logger.info(line.decode("utf-8"))

        parser_process.stdout.close()
        parser_process.wait()


def print_usage_msg():
    print('invalid usage')
    sys.exit()


def get_arguments():
    try:
        c_idx = sys.argv.index('-config')
        l_config_file = sys.argv[c_idx+1]
    except (ValueError, IndexError):
        l_config_file = None
        print_usage_msg()

    try:
        i_idx = sys.argv.index('-input')
        l_input = sys.argv[i_idx+1]
    except (ValueError, IndexError):
        l_input = None

    try:
        o_idx = sys.argv.index('-out_dir')
        l_output_path = sys.argv[o_idx+1]
    except (ValueError, IndexError):
        l_output_path = None

    return l_config_file, l_input, l_output_path


if __name__ == '__main__':
    config_file, input_arg, output_path = get_arguments()

    logging.config.fileConfig(config_file)

    params = read_config_file(config_file)
    logging.info(str(params))

    if params.input_type == 'ukwac':
        filelist, abs_output_path = generate_ukwac_input_files(params)
    else:
        logging.debug('only ukwac corpus supported')
        sys.exit()

    logging.info('filelist = ' + str(filelist))

    LOG_FILES_FOLDER = abs_output_path + '/' + LOG_FILES_FOLDER + '/'
    create_path(LOG_FILES_FOLDER)

    for file in filelist:
        ParserThread(params, file, abs_output_path).start()
        break

    while threading.active_count() > 1:
        logging.debug('active thread count = %d', threading.active_count())
        time.sleep(2)

    logging.info('parsing successfully complete')

