def get_logging_config(log_level):
    return {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "default": {
                "format": "%(asctime)s - [%(process)d] - %(name)s - %(levelname)s - %(message)s"
            },
        },
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "formatter": "default",
            },
        },
        "root": {"level": log_level, "handlers": ["console"]},
        "loggers": {
            "uvicorn": {
                "level": log_level,
                "handlers": ["console"],
                "propagate": False,
            },
        },
    }
