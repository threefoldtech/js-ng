import click

from jumpscale.core.config import get_default_config, update_config, get_config
import toml


def decode_toml_value(s):
    try:
        return toml.TomlDecoder().load_value(s)[0]
    except ValueError:
        return s


def encode_toml_value(s):
    return toml.TomlEncoder().dump_value(s)


def format_config_parameter(name, value):
    if isinstance(value, dict):
        print_dict(value, "")
    else:
        return "%s = %s" % (name, encode_toml_value(value))


def print_dict(data, path):
    for name, value in data.items():
        if isinstance(value, dict):
            print_dict(value, f"{path}{name}.")
        else:
            encoded = encode_toml_value(value)
            print(f"{path}{name} = {encoded}")


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
    try:
        _, obj, prop = traverse_config(name)
        if not isinstance(obj, dict):
            raise KeyError()
        value = obj[prop]
        click.echo(format_config_parameter(name, value))
    except KeyError:
        click.echo("Key doens't exist")


@config.command()
@click.argument("name")
@click.argument("value")
def update(name, value):
    try:
        config, obj, prop = traverse_config(name)
        if not isinstance(obj, dict) or prop not in obj:
            raise KeyError()
        obj[prop] = decode_toml_value(value)
        update_config(config)
    except KeyError:
        click.echo("Key doen't exist")
    else:
        click.echo("Updated.")


@click.group()
def cli():
    pass


cli.add_command(config)

if __name__ == "__main__":
    cli()
