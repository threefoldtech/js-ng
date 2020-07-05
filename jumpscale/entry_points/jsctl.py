import click

from jumpscale.core.config import get_default_config, update_config, get_config
import toml


def decode_toml_value(s):
    try:
        return toml.TomlDecoder().load_value(s)[0]
    except Exception:
        return s


def encode_toml_value(s):
    return toml.TomlEncoder().dump_value(s)


def format_config_parameter(name, value):
    if isinstance(value, dict):
        print_dict(value, f"{name}.")
    else:
        return "%s = %s" % (name, encode_toml_value(value))


def print_dict(data, path):
    for name, value in data.items():
        if isinstance(value, dict):
            print_dict(value, f"{path}{name}.")
        else:
            encoded = encode_toml_value(value)
            print(f"{path}{name} = {encoded}")


def validate_type(a, b):
    typea = type(a).__name__
    typeb = type(b).__name__
    if typea != typeb:
        raise TypeError(f"Type mismatch: Expected {typea} found {typeb}.")


def format_config(config):
    print_dict(config, "")


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
    """list default configuration."""
    format_config(get_default_config())


@config.command()
def list_all():
    """list all configurations."""
    format_config(get_config())


@config.command()
@click.argument("name")
def get(name):
    """get the key from the configuration, use dots to access nested values."""
    try:
        _, obj, prop = traverse_config(name)
        if not isinstance(obj, dict):
            raise KeyError()
        value = obj[prop]
        click.echo(format_config_parameter(name, value))
    except KeyError:
        click.echo('Key doens\'t exist. Type "jsctl config list-all" to see all valid configurations.')


@config.command()
@click.argument("name")
@click.argument("value")
def update(name, value):
    """set the passed key by the corresponding toml value."""
    try:
        config, obj, prop = traverse_config(name)
        if not isinstance(obj, dict) or prop not in obj:
            raise KeyError()
        value = decode_toml_value(value)
        validate_type(obj[prop], value)
        obj[prop] = value
        update_config(config)
    except KeyError:
        click.echo('Key doens\'t exist. Type "jsctl config list-all" to see all valid configurations.')
    except TypeError as e:
        click.echo(str(e))
    else:
        click.echo("Updated.")


@click.group()
def cli():
    pass


cli.add_command(config)

if __name__ == "__main__":
    cli()
