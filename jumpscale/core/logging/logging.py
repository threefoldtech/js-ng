import sys
import os
from loguru import logger
from jumpscale.core.config import get_config, update_config

logs_dir = os.path.expanduser(os.path.join("~/.config", "jumpscale", "logs"))

# TODO suitable logging format.
DEFAULT_LOGGING_CONFIG = {
    "handlers": [
        # {"sink": "sys.stdout", "format": "{time} - {message}", "colorize":True, "enqueue":True},
        {"sink": os.path.join(logs_dir, "file_jumpscale.log"), "serialize": True, "enqueue": True}
    ]
}

js_config = get_config()
if not "logging" in js_config or js_config["logging"]["handlers"] == [{}]:
    # FIXME: doesn't work as expected..
    js_config["logging"] = DEFAULT_LOGGING_CONFIG
    update_config(js_config)


js_config = get_config()
assert js_config["logging"] and js_config["logging"]["handlers"] != [{}]
# js_config = get_jumpscale_config()
# loguruconfig = js_config.get("logging")
logging_config = js_config["logging"]

# QUESTION: how to pass sink sys.stdout in json config?
logging_config["handlers"].append(
    {"sink": sys.stdout, "format": "{time} - {message}", "colorize": True, "enqueue": True}
)
logger.configure(**logging_config)
