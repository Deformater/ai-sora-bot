from os import environ

from pydantic_settings import BaseSettings


class DefaultSettings(BaseSettings):
    """
    Default configs for application.

    Usually, we have three environments: for development, testing and production.
    But in this situation, we only have standard settings for local development.
    """

    ENV: str = environ.get("ENV", "local")
    LOG_LEVEL: str = environ.get("LOG_LEVEL", "INFO").upper()

    TELEGRAM_TOKEN: str = environ.get("TELEGRAM_TOKEN")

    YOOKASSA_KEY: str = environ.get("YOOKASSA_KEY")
    YOOKASSA_SECRET_KEY: str = environ.get("YOOKASSA_SECRET_KEY")
    YOOKASSA_SHOP_ID: str = environ.get("YOOKASSA_SHOP_ID")

    CALLBACK_BASE_URL: str = environ.get("CALLBACK_BASE_URL")

    API_SOURCE: str = environ.get("API_SOURCE")
    KIEAI_API_KEY: str = environ.get("KIEAI_API_KEY")
    RUNBLOB_API_KEY: str = environ.get("RUNBLOB_API_KEY")
    PIAPI_API_KEY: str = environ.get("PIAPI_API_KEY")

    POSTGRES_DB: str = environ.get("POSTGRES_DB")
    POSTGRES_HOST: str = environ.get("POSTGRES_HOST")
    POSTGRES_USER: str = environ.get("POSTGRES_USER")
    POSTGRES_PORT: int = int(environ.get("POSTGRES_PORT"))
    POSTGRES_PASSWORD: str = environ.get("POSTGRES_PASSWORD")

    REDIS_HOST: str = environ.get("REDIS_HOST")
    REDIS_PORT: int = environ.get("REDIS_PORT")

    RABBITMQ_HOST: str = environ.get("RABBITMQ_HOST")
    RABBITMQ_USER: str = environ.get("RABBITMQ_USER")
    RABBITMQ_PASSWORD: str = environ.get("RABBITMQ_PASSWORD")
    RABBITMQ_PORT: int = environ.get("RABBITMQ_PORT")
    RABBITMQ_QUEUE: str = environ.get("RABBITMQ_QUEUE")

    DB_CONNECT_RETRY: int = environ.get("DB_CONNECT_RETRY", 20)
    DB_POOL_SIZE: int = environ.get("DB_POOL_SIZE", 10)

    WEBHOOK_SECRET: str = environ.get("WEBHOOK_SECRET")
    WEBHOOK_BASE_URL: str = environ.get("WEBHOOK_BASE_URL")

    @property
    def database_settings(self) -> dict:
        """
        Get all settings for connection with database.
        """
        return {
            "database": self.POSTGRES_DB,
            "user": self.POSTGRES_USER,
            "password": self.POSTGRES_PASSWORD,
            "host": self.POSTGRES_HOST,
            "port": self.POSTGRES_PORT,
        }

    @property
    def rabbitmq_settings(self) -> dict:
        """
        Get all settings for connection with rabbitmq.
        """
        return {
            "user": self.RABBITMQ_USER,
            "password": self.RABBITMQ_PASSWORD,
            "host": self.RABBITMQ_HOST,
            "port": self.RABBITMQ_PORT,
        }

    @property
    def redis_settings(self) -> dict:
        """
        Get all settings for connection with redis.
        """
        return {
            "host": self.REDIS_HOST,
            "port": self.REDIS_PORT,
        }

    @property
    def database_uri(self) -> str:
        """
        Get uri for connection with database.
        """
        return "postgresql+asyncpg://{user}:{password}@{host}:{port}/{database}".format(
            **self.database_settings,
        )

    @property
    def database_uri_sync(self) -> str:
        """
        Get uri for connection with database.
        """
        return "postgresql://{user}:{password}@{host}:{port}/{database}".format(
            **self.database_settings,
        )

    @property
    def rabbitmq_uri(self) -> str:
        """
        Get uri for connection with rabbitmq.
        """
        return "amqp://{user}:{password}@{host}:{port}/".format(
            **self.rabbitmq_settings,
        )

    @property
    def redis_uri(self) -> str:
        """
        Get uri for connection with redis.
        """
        return "redis://{host}:{port}/0".format(
            **self.redis_settings,
        )

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
