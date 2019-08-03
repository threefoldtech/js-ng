import invoke

def execute(cmd, command_ctx=None, connection_ctx=None):
    ## use formatter to format command
    command_ctx = command_ctx or {}
    return invoke.run(cmd, **command_ctx)