import os
import yaml

from omegaconf import DictConfig
from sqlalchemy import create_engine, Engine


def get_engine() -> Engine:
    with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "config.yaml")) as file:
        cfg = DictConfig(yaml.load(file, yaml.SafeLoader))
    engine = create_engine(f"{cfg.dialect}://{cfg.username}:{cfg.password}@{cfg.host}:{cfg.port}/{cfg.database}")
    return engine
