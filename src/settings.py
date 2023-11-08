import logging

from enum import Enum

from envyaml import EnvYAML


class Flavour(str, Enum):
    EXPONENTIATIONS = "exponentiations"
    ELIPTIC_CURVE = "eliptic_curve"


log_level_mapping = {
    "debug": logging.DEBUG,
    "info": logging.INFO,
    "warning": logging.WARNING,
    "error": logging.ERROR,
    "critical": logging.CRITICAL,
}


def load_settings() -> "Settings":
    yaml_config = EnvYAML("./config/local.yaml", strict=False)
    return Settings(yaml_config)


class Settings:
    def __init__(self, yaml_config: EnvYAML) -> None:
        self.config = yaml_config
        # TODO some checking on input data
        self.q: int = self.config["public_variables"]["q"]
        self.g: int = self.config["public_variables"]["g"]
        self.h: int = self.config["public_variables"]["h"]
        self.flavour: Flavour = self.config["implementaion"]["flavour"]
        self.bits: int = self.config["implementaion"]["bits"]
        self.log_level: str = self.config["logging"]["level"]


if __name__ == "__main__":
    settings = load_settings()
    print(f"{settings.q=}")
    print(f"{settings.g=}")
    print(f"{settings.h=}")
    print(f"{settings.flavour=}")
    print(f"{settings.bits=}")
    print(f"{settings.log_level=}")
