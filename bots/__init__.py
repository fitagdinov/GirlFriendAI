from dataclasses import dataclass


@dataclass
class BotConfig:
    token: str
    messages: dict[str, dict[str, str]]
    buttons: dict[str, dict[str, str]]
