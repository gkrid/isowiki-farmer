import logging


def _create_logger(name):
    """
    create logger fo script
    :param name: name of logger
    :return: logger
    """
    log_format = '%(asctime)s - %(name)s - %(levelname)s: %(message)s'
    formatter = logging.Formatter(log_format)

    ch = logging.StreamHandler()  # console handler
    ch.setLevel(logging.INFO)
    ch.setFormatter(formatter)

    logger = logging.getLogger(name)
    logger.setLevel('INFO')
    logger.addHandler(ch)
    return logger
