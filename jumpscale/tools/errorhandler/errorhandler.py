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

    def get_traceback(self, exc_info=None):
        """Get a trackback information as a dict, suitable to used with error/alert handlers

        if `exe_info` is not passed, `sys.exc_info()` will be used instead.

        Example traceback information:

        ```
        {
            'process_id': 20840,
            'raw': 'Traceback (most recent call last):\n  File "<stdin>", line 1, in <module>\nValueError: a is not valid',
            'straceback': [
                {
                    'code': '',
                    'context': '<module>',
                    'filename': '<stdin>',
                    'filepath': '<stdin>',
                    'linenr': 1
                }
            ]
        }
        ```

        Args:
            exc_info (tuple, optional): exception information as a tuple (ttype, tvalue, tb). Defaults to None.

        Returns:
            dict: raw and stacktrace information as a dict, alongside process id
        """
        if exc_info:
            ttype, tvalue, tb = exc_info
        else:
            ttype, tvalue, tb = sys.exc_info()

        stacktrace = self._construct_stacktrace(tb)
        traceback_text = self._format_lines(traceback.format_exception(ttype, tvalue, tb))

        return {"raw": traceback_text, "stacktrace": stacktrace, "process_id": j.application.process_id}

    def _handle_exception(self, ttype, tvalue, tb, level=40, die=False, log=True, category="", data=None):
        exc_info = (ttype, tvalue, tb)
        timestamp = j.data.time.now().timestamp
        message = self._format_lines(traceback.format_exception_only(ttype, tvalue))

        err_dict = {
            "app_name": j.logger.default_app_name,
            "level": level,
            "message": message,
            "timestamp": timestamp,
            "category": category or "exception",
            "data": data,
            "traceback": self.get_traceback(exc_info),
        }

        if log:
            exception = exc_info
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
