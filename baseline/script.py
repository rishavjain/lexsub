import configparser
import os
import time
import errno


UKWAC_NUM_LINES_FILE = 50


def generate_ukkwac_input_files(input_files, out_dir):
    gen_files_path = out_dir + '/gen/' + time.strftime('%m-%d-%H-%M-%S') + '/'

    if not os.path.exists(gen_files_path):
        try:
            os.makedirs(gen_files_path)
        except OSError as exc: # Guard against race condition
            if exc.errno != errno.EEXIST:
                raise

    idx = 1
    out_obj = open(gen_files_path + 'in' + str(idx) + '.txt', 'w', encoding='iso-8859-15')

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
                    idx += 1
                    out_obj = open(gen_files_path + 'in' + str(idx) + '.txt', 'w', encoding='iso-8859-15')
                    out_idx = 0

            line_idx += 1

    out_obj.close()
    if out_idx == 0:
        os.remove(out_obj.name)

    return

def generate_cmd(config_file, out_dir):
    config = configparser.ConfigParser(interpolation=configparser.ExtendedInterpolation(), inline_comment_prefixes=('#',))
    config.read(config_file) # 'desktop.ini'

    base_path = config['PATHS']['base_path']
    print('base_path', '=', config['PATHS']['base_path'])

    parser_path = config['PATHS']['parser_path']
    print('parser_path', '=', config['PATHS']['parser_path'])

    parser_class = config['PARSER']['class']
    print('parser_class', '=', config['PARSER']['class'])

    parser_annotators = config['PARSER']['annotators']
    print('parser_annotators', '=', config['PARSER']['annotators'])

    parser_memory = config['PARSER']['max_mem']
    print('parser_memory', '=', parser_memory)

    parser_cmdFmtStr = config['PARSER']['cmdFmtStr']

    if(config['INPUT']['type'] == 'ukwac'):
        if(config.has_option('INPUT', 'file')):
            input_corpus_files = [config['INPUT']['file'],]
        else:
            files_path = config['INPUT']['files_path']
            input_corpus_files = [files_path + '/' + file_name for file_name in os.listdir(files_path)]

        print('input_corpus_files', input_corpus_files)
        input_gen_files = generate_ukkwac_input_files(input_corpus_files, out_dir)

        #cmd = parser_cmdFmtStr.format(parser_memory, parser_path, parser_class, parser_annotators, in_file, out_dir)
        #print(cmd)

generate_cmd('desktop.ini', 'out')