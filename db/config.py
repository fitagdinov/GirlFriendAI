from dataclasses import dataclass


@dataclass
class EngineConfig:
    dialect: str = "postgresql+psycopg2"
    host: str = "localhost"
    port: str = "5432"
    database: str = "girlfriend_ai"
    username: str = ""
    password: str = ""
