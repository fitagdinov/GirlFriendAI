from dataclasses import dataclass


@dataclass
class ParserConfig:
    url: str
    webdriver_args: list[str]
