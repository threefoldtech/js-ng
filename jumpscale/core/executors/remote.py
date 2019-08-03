import fabric

def execute(cmd, againstctx):
    with fabric.Connection(againstctx) as c:
        return c.run(cmd)