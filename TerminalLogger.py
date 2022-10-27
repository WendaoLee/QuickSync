import logging


class TerminalLogger(object):
    debug_formatter = logging.Formatter('[%(asctime)s]\033[36m [%(levelname)s] %(message)s\033[0m')
    warning_formatter = logging.Formatter('[%(asctime)s]\033[1;33m [%(levelname)s] %(message)s\033[0m')
    error_formatter = logging.Formatter('[%(asctime)s]\033[1;31m [%(levelname)s] %(message)s\033[0m')
    info_formatter = logging.Formatter('[%(asctime)s]\033[1;37m [%(levelname)s] %(message)s\033[0m')

    def __init__(self):
        self.handler = logging.StreamHandler()
        self.logger = logging.getLogger()
        self.logger.setLevel(0)
        self.logger.addHandler(self.handler)

    def updateHandler(self,handler):
        self.handler = logging.StreamHandler(handler)

    def DEBUG(self, msg: str):
        # msg = '\033[36m{txt}\033[0m'.format(txt=msg)
        self.handler.setFormatter(
            self.debug_formatter
        )
        self.logger.debug(msg)

    def ERROR(self, msg: str):
        self.handler.setFormatter(
            self.error_formatter
        )
        self.logger.error(msg)

    def WARNING(self, msg):
        self.handler.setFormatter(
            self.warning_formatter
        )
        self.logger.warning(msg)

    def INFO(self, msg):
        self.handler.setFormatter(
            self.info_formatter
        )
        self.logger.info(msg)


LOGGER = TerminalLogger()
