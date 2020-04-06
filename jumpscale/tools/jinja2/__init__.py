from jumpscale.god import j
from jinja2 import (
    Environment,
    FileSystemLoader,
    select_autoescape,
    StrictUndefined,
    Template,
)


def get_env(templates_path):
    """get an environment from templates root path

    Args:
        templates_path (str): root path of all templates

    Returns:
        jinja2.Environment: Jinja2 env
    """
    return Environment(
        loader=FileSystemLoader(templates_path),
        autoescape=select_autoescape(["html", "xml"]),
    )


def get_template(template_path=None, template_text=None):
    """returns jinja2 template

    Args:
        template_path (str, optional): location of the template. Defaults to None.
        template_text (str, optional): text of the template. Defaults to None.

    Raises:
        j.exceptions.Input: If both template_path and template_text are specified
        j.exceptions.Input: If no input was specified

    Returns:
        jinja2.Template: Jinja2 template
    """

    if template_path and template_text:
        raise j.exceptions.Input("Can only specify template_path or template_text")
    if not template_path and not template_text:
        raise j.exceptions.Input(
            "Need to specify either template_path or template_text"
        )

    if template_path:
        template_text = j.sals.fs.read_file(template_path)

    return Template(template_text, undefined=StrictUndefined)


def render_template(template_path=None, template_text=None, dest=None, **kwargs):
    """load the template if dest is specified will write in specified path, renders with specified kwargs

    Args:
        template_path (str, optional): location of the template. Defaults to None.
        template_text (str, optional): text of the template. Defaults to None.
        dest (str, optional): path to write rendered template in. Defaults to None.

    Raises:
        j.exceptions.Base: If rendering failed

    Returns:
        str: Rendered template
    """
    template = template_get(template_path=template_path, template_text=template_text)

    try:
        template_string = template.render(**kwargs)
    except Exception as e:
        raise j.exceptions.Base(e)

    if dest:
        j.sals.fs.mkdirs(j.sals.fs.dirname(dest))
        j.sals.fs.write_file(dest, template_string)
    return template_string


def render_code_python(
    obj_key=None,
    template_path=None,
    template_text=None,
    dest=None,
    objForHash=None,
    name=None,
    **kwargs,
):
    # TODO
    pass
