import click

from jumpscale.core.config import get_default_config, update_config, get_config


def format_config_parameter(name, value):
    return "%s = %s" % (name, str(value))


def print_dict(data, path):
    for name, value in data.items():
        if isinstance(value, dict):
            print_dict(value, f"{path}{name}.")
        else:
            print(f"{path}{name} = {value}")


def format_config(config):
    print_dict(config, "")


def traverse_config(name):
    path = name.split(".")
    config = get_config()
    prop = config
    if name in config:
        return config, prop, name
    for i, p in enumerate(path[:-1]):
        prop = prop[p]
    return config, prop, path[-1]


@click.group()
def config():
    pass


@config.command()
def defaults():
    format_config(get_default_config())


@config.command()
def list_all():
    format_config(get_config())


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
    try:
        config, obj, prop = traverse_config(name)
        obj[prop] = value
        update_config(config)
    except KeyError:
        config = get_config()
        config[name] = value
        update_config(config)

    click.echo("Updated.")


@click.group()
def cli():
    pass


cli.add_command(config)

if __name__ == "__main__":
    cli()
