import click

from jumpscale.core.config import get_default_config, update_config, get_config


def format_config_parameter(name, value):
    return "%s = %s" % (name, str(value))


def format_config(config):
    return "\n".join([format_config_parameter(name, value) for name, value in config.items()])


def traverse_config(name):
    path = name.split(".")
    config = get_config()
    prop = config
    for i, p in enumerate(path[:-1]):
        prop = prop[p]
    return config, prop, path[-1]


@click.group()
def config():
    pass


@config.command()
def defaults():
    click.echo(format_config(get_default_config()))


@config.command()
def list_all():
    click.echo(format_config(get_config()))


@config.command()
@click.argument("name")
def get(name):
    _, obj, prop = traverse_config(name)
    value = obj[prop]
    click.echo(format_config_parameter(name, value))


@config.command()
@click.argument("name")
@click.argument("value")
def update(name, value):
    config, obj, prop = traverse_config(name)
    obj[prop] = value

    update_config(config)

    click.echo("Updated.")


@click.group()
def cli():
    pass


cli.add_command(config)

if __name__ == "__main__":
    cli()
