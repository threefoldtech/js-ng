import inspect
import sys
import traceback

from jumpscale.god import j


class ErrorHandler:
    def __init__(self):
        self.handlers = []

    def _format_lines(self, lines):
        return "".join(lines).strip()

    def _construct_stacktrace(self, frame):
        stacktrace = []
        while frame:
            frame_info = inspect.getframeinfo(frame)

            if frame_info.code_context:
                code_context = frame_info.code_context[0].strip()
            else:
                code_context = ""

            stacktrace.append(
                {
                    "filename": j.sals.fs.basename(frame_info.filename),
                    "filepath": frame_info.filename,
                    "context": frame_info.function,
                    "linenr": frame_info.lineno,
                    "code": code_context,
                }
            )
            frame = frame.tb_next
        return stacktrace

    def _handle_exception(self, ttype, tvalue, tb, level=40, die=False, stdout=True, category=""):
        process = j.sals.process.get_my_process()
        timestamp = j.data.time.now().timestamp
        stacktrace = self._construct_stacktrace(tb)
        message = self._format_lines(traceback.format_exception_only(ttype, tvalue))
        traceback_text = self._format_lines(traceback.format_exception(ttype, tvalue, tb))

        error_dict = {
            "level": level,
            "message": message,
            "category": category or "exception",
            "traceback": {
                "text": traceback_text,
                "timestamp": timestamp,
                "process_id": process.pid,
                "stacktrace": stacktrace,
            },
        }

        if stdout:
            j.logger.error(message)

        for handler_func, handler_level in self.handlers:
            if level >= handler_level:
                handler_func(**error_dict)

        if die:
            sys.exit(1)

    def handle_exception(
        self, exception: Exception, level: int = 40, die: bool = False, stdout: bool = True, category: str = ""
    ):
        """Hndler exception
        
        Arguments:
            exception {Exception} -- the exception object to handle
        
        Keyword Arguments:
            level {int} -- exception level (default: {40})
            die {bool} -- optional flag to exit after handling the exception (default: {True})
            stdout {bool} -- option flag to log the exception in the stdout (default: {True})
            category {str} -- category (default: {""})
        """
        ttype, _, tb = sys.exc_info()
        self._handle_exception(ttype, exception, tb, die=die, stdout=stdout, category=category)

    def register_handler(self, handler: callable, level: int = 40):
        """Register new error handler
        
        Arguments:
            handler {callable} -- error handler callable
        
        Keyword Arguments:
            level {int} -- exception level (default: {40})
        """
        if (handler, level) not in self.handlers:
            self.handlers.append((handler, level))

    def excepthook(self, ttype, tvalue, tb):
        """exception hook handler"""
        self._handle_exception(ttype, tvalue, tb)
