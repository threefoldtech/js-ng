import fabric

def execute(cmd, command_ctx, connection_ctx):
    """
    kwargs: fabric.Connection(host, user=None, port=None, config=None, gateway=None, forward_agent=None, connect_timeout=None, connect_kwargs=None, inline_ssh_env=None)
    """
    with fabric.Connection(**connection_ctx) as c:
        return c.run(cmd, **command_ctx)