from colorama import Fore


default_log_fn = print


def default_log_formatter(logger, subject, message=""):
    logger = f"{Fore.GREEN}{logger}: " if logger else ""
    m = f"\n{message}" if message else ""
    return f"{logger}{Fore.CYAN}{subject}:{Fore.RESET}{m}"


class LogOptions:
    def __init__(self, verbose: bool = False):
        self.verbose = verbose


class Log:
    log_fn = default_log_fn
    log_formatter = default_log_formatter
    options: LogOptions = LogOptions()

    @staticmethod
    def set_log_fn(log_fn):
        Log.log_fn = log_fn

    @staticmethod
    def set_log_formatter(log_formatter):
        Log.log_formatter = log_formatter

    @staticmethod
    def set_options(**kwargs):
        Log.options = LogOptions(**kwargs)

    @staticmethod
    def set_verbose(verbose: bool):
        Log.options.verbose = verbose

    def __init__(self, logger: str = ""):
        self.logger = logger

    def __call__(self, subject, message=""):
        self.log(subject, message)

    def log(self, subject, message=""):
        s = Log.log_formatter(self.logger, subject, message)
        Log.log_fn(s)

    def verbose(self, subject, message=""):
        if Log.options.verbose:
            self.log(subject, message)
