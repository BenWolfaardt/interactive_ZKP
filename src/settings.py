import logging

from enum import Enum

from envyaml import EnvYAML

from src.lib import PublicVariableGenerator


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
        self.q: int = self.config["public_variables"]["p"]
        self.g: int = self.config["public_variables"]["g"]
        self.h: int = self.config["public_variables"]["h"]
        self.flavour: Flavour = self.config["implementaion"]["flavour"]
        self.bits: int = self.config["implementaion"]["bits"]
        self.default_values: bool = self.config["implementaion"]["use_preconfigured_env"]
        self.log_level: str = self.config["logging"]["level"]

    def set_public_variables(self) -> None:
        generator = PublicVariableGenerator()

        # TODO get approach from config
        approach = 1

        if approach == 1:
            approach_1 = generator.Approach1(generator)
            self.q, self.g, self.h = approach_1.get_public_variables()
            # TODO logging.DEBUG
            print(f"Approach 1: {self.q=}, {self.g=}, {self.h=}")
        else:
            approach_1 = generator.Approach1(generator)
            self.q, self.g, self.h = approach_1.get_public_variables()
            # TODO logging.DEBUG
            print(f"Approach 1: {self.q=}, {self.g=}, {self.h=}")


if __name__ == "__main__":
    settings = load_settings()
    print(f"{settings.q=}")
    print(f"{settings.g=}")
    print(f"{settings.h=}")
    print(f"{settings.flavour=}")
    print(f"{settings.bits=}")
    print(f"{settings.default_values=}")
    print(f"{settings.log_level=}")
