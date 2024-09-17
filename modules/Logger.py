import logging

class LoggingFormatter(logging.Formatter):
    # Colors
    black = "\x1b[30m"
    red = "\x1b[31m"
    green = "\x1b[32m"
    yellow = "\x1b[33m"
    blue = "\x1b[34m"
    gray = "\x1b[38m"
    # Styles
    reset = "\x1b[0m"
    bold = "\x1b[1m"

    COLORS = {
        logging.DEBUG: gray + bold,
        logging.INFO: blue + bold,
        logging.WARNING: yellow + bold,
        logging.ERROR: red,
        logging.CRITICAL: red + bold,
    }

    def format(self, record):
        log_color = self.COLORS[record.levelno]
        content = "(gray){asctime}(reset) (levelcolor)[{levelname}](reset) (green){name}(reset)(gray): {message}"
        content = content.replace("(gray)", self.gray + self.bold)
        content = content.replace("(reset)", self.reset)
        content = content.replace("(levelcolor)", log_color)
        content = content.replace("(green)", self.green + self.bold)
        formatter = logging.Formatter(content, "%Y-%m-%d %H:%M:%S", style="{")
        return formatter.format(record)

class Logger:
    def __init__(self, name):
        self.name = name
        self._logger = logging.getLogger(name)
        self._logger.setLevel(logging.INFO)

        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(LoggingFormatter())
        # # File handler
        # file_handler = logging.FileHandler(filename=f"../{name}.log", encoding="utf-8", mode="w")
        # file_handler_formatter = logging.Formatter(
        #     "[{asctime}] [{levelname:<8}] {name}: {message}", "%Y-%m-%d %H:%M:%S", style="{"
        # )
        # file_handler.setFormatter(file_handler_formatter)

        self._logger.addHandler(console_handler)
        #self._logger.addHandler(file_handler)

    def debug(self, message):
        self._logger.debug(message)

    def info(self, message):
        self._logger.info(message)

    def warning(self, message):
        self._logger.warning(message)

    def error(self, message):
        self._logger.error(message)