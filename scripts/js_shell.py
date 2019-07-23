#!/usr/bin/env ipython3
from __future__ import print_function
import better_exceptions, sys
from IPython import embed, get_ipython

ip = get_ipython()
old_show = ip.showtraceback

def exception_thunk(exc_tuple=None, filename=None,
                    tb_offset=None, exception_only=False):
    print("Thunk: %r %r %r %r" % (exc_tuple, filename, tb_offset, exception_only),
          file=sys.stderr)
    notuple = False
    if exc_tuple is None:
        notuple = True
        exc_tuple = sys.exc_info()
    use_better = True
    use_better = use_better and (filename is None)
    use_better = use_better and (tb_offset is None)
    use_better = use_better and (not exception_only)
    use_better = use_better and (not isinstance(exc_tuple[0], SyntaxError))
    if use_better:
        return better_exceptions.excepthook(*exc_tuple)
    else:
        return old_show(None if notuple else exc_tuple,
                        filename, tb_offset, exception_only)

ip.showtraceback = exception_thunk


def js_shell():
    from jumpscale.god import j
    embed(colors='Linux')

if __name__ == "__main__":
    js_shell()