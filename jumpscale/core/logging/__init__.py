def export_module_as():

    from jumpscale.loader import j
    from .logging import Logger, RedisLogHandler, LogHandler

    logger = Logger()
    config = j.core.config.config.get_config().get("logging")

    if config:
        # configure redis handler if enabled
        if config["redis"]["enabled"] and j.core.db:
            redis_config = config["redis"]
            redis_handler = RedisLogHandler(
                max_size=redis_config["max_size"], dump=redis_config["dump"], dump_dir=redis_config["dump_dir"]
            )
            logger.add_custom_handler("redis", redis_handler, serialize=True, level=redis_config["level"])

        # configure filesystem handler if enabled
        if config["filesystem"]["enabled"]:
            fs_config = config["filesystem"]
            logger.add_handler(sink=fs_config["log_dir"], level=fs_config["level"], rotation=fs_config["rotation"])

    return logger
