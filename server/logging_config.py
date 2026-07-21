import logging

LOGGER_NAME = 'kfchess.server'


def setup_logging(level=logging.INFO, log_file='server.log'):
    logger = logging.getLogger(LOGGER_NAME)
    if logger.handlers:
        return logger  
    
    logger.setLevel(level)
    formatter = logging.Formatter('%(asctime)s %(levelname)s %(name)s: %(message)s')

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    file_handler = logging.FileHandler(log_file, encoding='utf-8')
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    return logger


def get_logger():
    return logging.getLogger(LOGGER_NAME)
