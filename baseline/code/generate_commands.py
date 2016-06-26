from config import create_path

import os
import logging
import sys
import time

GEN_FILES_FOLDER = 'gen'
UKWAC_NUM_LINES_FILE = 500


def generate_ukwac_input_files(_params):
    # generating tuple of input files
    if _params.input_file is not None:
        input_files = [_params.input_file, ]
    else:
        input_files = [_params.input_filepath + '/' + file_name for file_name in os.listdir(_params.input_filepath)]

    # defining required paths and files
    out_path = os.path.abspath(_params.output_path) + '/' + time.strftime('%m-%d-%H-%M-%S') + '/'

    idx = 1  # index for generated input file
    gen_files_path = out_path + GEN_FILES_FOLDER + '/'
    create_path(gen_files_path)
    out_obj = open(gen_files_path + 'in' + str(idx) + '.txt', 'w', encoding='iso-8859-15')

    _filelist = ()

    out_idx = 0
    for input_file in input_files:
        in_obj = open(input_file, encoding='iso-8859-15')

        line_idx = 0
        out_idx = 0
        for line in in_obj:
            if not line.startswith('CURRENT URL'):
                out_obj.write(line)
                out_idx += 1

                if out_idx % UKWAC_NUM_LINES_FILE == 0:
                    out_obj.close()
                    _filelist += (os.path.abspath(out_obj.name),)

                    idx += 1

                    out_obj = open(gen_files_path + 'in' + str(idx) + '.txt', 'w', encoding='iso-8859-15')
                    out_idx = 0

            line_idx += 1

    out_obj.close()

    if out_idx == 0:
        os.remove(out_obj.name)
    else:
        _filelist += (os.path.abspath(out_obj.name),)

    return _filelist, os.path.abspath(out_path)


def decode_parser_cmd(_params, _input_file, _abs_output_path):
    return _params.parser_cmdFmtStr.format(_params.parser_memory, _params.parser_path, _params.parser_class,
                                           _params.parser_annotators, _input_file, _abs_output_path)


def decode_qsub_cmd(_params, _log_file, _cmd):
    if _params.qsub_mail == 'yes':
        _log_file = '{} -m {} -M {}'.format(_log_file, _params.qsub_mail_option, 'rjain2@sheffield.ac.uk')

    return _params.qsub_cmdFmtStr.format(_params.qsub_mem, _params.qsub_rmem, _log_file, _cmd)


def generate_parser_commands(_params):
    if _params.input_type == 'ukwac':
        filelist, abs_output_path = generate_ukwac_input_files(_params)
    else:
        logging.debug('only ukwac corpus supported')
        sys.exit()

    logging.info('filelist = ' + str(filelist))

    commands = ()
    for _file in filelist:
        commands += (decode_parser_cmd(_params=_params, _input_file=_file, _abs_output_path=abs_output_path),)

    return commands, abs_output_path
