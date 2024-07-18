import yaml
import os

with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "config.yaml")) as file:
    cfg = yaml.load(file, yaml.SafeLoader)

