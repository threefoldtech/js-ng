import click

from jumpscale.core.config import get_default_config, update_config, get_config


def format_config_parameter(name, value):
    return "%s = %s" % (name, str(value))


def format_config(config):
    return "\n".join([format_config_parameter(name, value) for name, value in config.items()])


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
@click.option("--name")
def get(name):
    value = get_config()[name]
    click.echo(format_config_parameter(name, value))


@config.command()
@click.option("--name")
@click.option("--value")
def update(name, value):
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

