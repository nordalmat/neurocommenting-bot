import logging


def get_loggers():
    formatter = logging.Formatter(u'%(asctime)s %(levelname)s %(message)s', 
                                  datefmt='%d/%m/%Y %H:%M:%S')

    # Extensive version of log file 
    extensive_log_file = r"log_ext.txt"
    extensive_log_file_handler = logging.FileHandler(extensive_log_file, mode='a', encoding="utf-8")
    extensive_log_file_handler.setFormatter(formatter)
    extensive_log_file_handler.setLevel(logging.INFO)
    extensive_log = logging.getLogger("userbot_extensive")
    extensive_log.setLevel(logging.INFO)

    # Short version of log file
    simple_log_file = r"log.txt"
    simple_log_file_handler = logging.FileHandler(simple_log_file, mode='a', encoding="utf-8")
    simple_log_file_handler.setFormatter(formatter)
    simple_log_file_handler.setLevel(logging.INFO)
    simple_log = logging.getLogger("userbot_simple")
    simple_log.setLevel(logging.INFO)

    # Log to console 
    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)
    stream_handler.setLevel(logging.INFO)

    extensive_log.addHandler(extensive_log_file_handler)
    simple_log.addHandler(simple_log_file_handler)
    simple_log.addHandler(stream_handler)

    return extensive_log, simple_log


extensive_log, simple_log = get_loggers()
