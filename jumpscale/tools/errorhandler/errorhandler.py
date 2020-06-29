import inspect
import sys
import traceback

from jumpscale.loader import j


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

    def _handle_exception(self, ttype, tvalue, tb, level=40, die=False, log=True, category="", data=None):
        timestamp = j.data.time.now().timestamp
        stacktrace = self._construct_stacktrace(tb)
        message = self._format_lines(traceback.format_exception_only(ttype, tvalue))
        traceback_text = self._format_lines(traceback.format_exception(ttype, tvalue, tb))

        err_dict = {
            "appname": j.application.appname,
            "level": level,
            "message": message,
            "timestamp": timestamp,
            "category": category or "exception",
            "data": data,
            "traceback": {"raw": traceback_text, "stacktrace": stacktrace, "process_id": j.application.process_id},
        }

        if log:
            exception = (ttype, tvalue, tb)
            j.logger.exception(message=message, category=category, data=data, level=level, exception=exception)

        for handler_func, handler_level in self.handlers:
            if level >= handler_level:
                handler_func(**err_dict)

        if die:
            sys.exit(1)

    def handle_exception(
        self,
        exception: Exception,
        level: int = 40,
        die: bool = False,
        log: bool = True,
        category: str = "",
        data: dict = None,
    ):
        """Hndler exception

        Arguments:
            exception {Exception} -- the exception object to handle

        Keyword Arguments:
            level {int} -- exception level (default: {40})
            die {bool} -- optional flag to exit after handling the exception (default: {True})
            log {bool} -- option flag to log the exception (default: {True})
            category {str} -- category (default: {""})
        """
        ttype, _, tb = sys.exc_info()
        self._handle_exception(ttype, exception, tb, die=die, log=log, category=category, data=data)

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
