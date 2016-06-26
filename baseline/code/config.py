import configparser
import os
import errno


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
    qsub_script_path = None

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
               '\n\tqsub_script_path = {}' \
            .format(self.base_path, self.parser_path, self.parser_class, self.parser_annotators, self.parser_memory,
                    self.parser_cmdFmtStr, self.input_type, self.input_file, self.input_filepath, self.output_path,
                    self.qsub_mem, self.qsub_rmem, self.qsub_mail, self.qsub_mail_option, self.qsub_cmdFmtStr,
                    self.qsub_script_path)


def read_config_file(_config_file):
    config = configparser.ConfigParser(interpolation=configparser.ExtendedInterpolation(),
                                       inline_comment_prefixes=(';',))
    config.read(_config_file)  # 'desktop.ini'

    _params = Params()

    _params.base_path = config['paths']['base_path']
    _params.parser_path = config['paths']['parser_path']
    _params.parser_class = config['parser']['class']
    _params.parser_annotators = config['parser']['annotators']
    _params.parser_memory = config['parser']['max_mem']
    _params.parser_cmdFmtStr = config['parser']['cmdFmtStr']
    _params.input_type = config['input']['type']

    if config.has_option('input', 'file'):
        _params.input_file = config['input']['file']
    else:
        _params.input_filepath = config['input']['filepath']

    _params.output_path = config['output']['path']

    _params.qsub_mem = config['qsub']['mem']
    _params.qsub_rmem = config['qsub']['rmem']
    _params.qsub_mail = config['qsub']['mail']
    _params.qsub_mail_option = config['qsub']['mail_option']
    _params.qsub_cmdFmtStr = config['qsub']['cmdFmtStr']
    _params.qsub_script_path = config['qsub']['script_path']

    return _params


def create_path(path):
    if not os.path.exists(path):
        try:
            os.makedirs(path)
        except OSError as exc:  # Guard against race condition
            if exc.errno != errno.EEXIST:
                raise
