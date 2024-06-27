import os, logging

class Logger:
    def __init__(self, path = None):
        self.logger = logging.getLogger(__name__)
        formater = logging.Formatter(
            '[%(asctime)s.%(msecs)03d] %(levelname)s: %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
        
        if path is not None:
            logger_path = os.path.join(path, 'log')
            if not os.path.exists(logger_path):
                os.makedirs(logger_path)
            filehandler = logging.FileHandler(
                os.path.join(logger_path, 'CodeUpdaterLog.log'),
                encoding='utf-8',
            )
            filehandler.setFormatter(formater)
        consolehandler = logging.StreamHandler()
        consolehandler.setFormatter(formater)
        self.handlers = (filehandler, consolehandler)

        self.logger.setLevel(logging.INFO)

        self.is_logger_off = True

    def set_level(self, level):
        if level == 'Info':
            self.logger.setLevel(logging.INFO)
        elif level == 'Debug':
            self.logger.setLevel(logging.DEBUG)
        elif level == 'Warning':
            self.logger.setLevel(logging.WARNING)
        elif level == 'Error':
            self.logger.setLevel(logging.ERROR)
        elif level == 'Critical':
            self.logger.setLevel(logging.CRITICAL)
    
    def open(self):
        self.is_logger_off = False

    def close(self):
        self.is_logger_off = True

    def info(self, msg):
        if self.is_logger_off:
            return
        with LogHandlerContextManager(self.logger, self.handlers):
            self.logger.info(msg)

    def debug(self, msg):
        if self.is_logger_off:
            return
        with LogHandlerContextManager(self.logger, self.handlers):
            self.logger.debug(msg)

    def warning(self, msg):
        if self.is_logger_off:
            return
        with LogHandlerContextManager(self.logger, self.handlers):
            self.logger.warning(msg)

    def error(self, msg):
        if self.is_logger_off:
            return
        with LogHandlerContextManager(self.logger, self.handlers):
            self.logger.error(msg)

    def exception(self, msg):
        if self.is_logger_off:
            return
        with LogHandlerContextManager(self.logger, self.handlers):
            self.logger.exception(msg)

    def critical(self, msg):
        if self.is_logger_off:
            return
        with LogHandlerContextManager(self.logger, self.handlers):
            self.logger.critical(msg)


class LogHandlerContextManager:
    def __init__(self, logger, handlers):
        self.logger = logger
        self.handlers = handlers
        
    def __enter__(self):
        for handler in self.handlers:
            self.logger.addHandler(handler)
        
    def __exit__(self, exc_type, exc_value, traceback):
        for handler in self.handlers:
            handler.close()
            self.logger.removeHandler(handler)