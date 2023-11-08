import logging

from enum import Enum
from typing import Any

from envyaml import EnvYAML
from pydantic import BaseModel, field_validator


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


class Settings(BaseModel):
    p: int
    q: int
    g: int
    h: int
    bits: int
    flavour: Flavour
    log_level: str

    def __init__(self, **data: Any):
        yaml_config = EnvYAML("./config/local.yaml", strict=False)

        super().__init__(
            p=yaml_config["public_variables"]["p"],
            q=yaml_config["public_variables"]["q"],
            g=yaml_config["public_variables"]["g"],
            h=yaml_config["public_variables"]["h"],
            flavour=yaml_config["implementation"]["flavour"],
            bits=yaml_config["implementation"]["bits"],
            log_level=yaml_config["logging"]["level"],
            **data,
        )

    @field_validator("p", "q", "g", "h")
    def check_value_size(cls, value: int) -> int:
        if value >= (1 << 63):
            raise ValueError("The value must be smaller than 63 or less for signed 64-bit compatibility.")
        elif value <= 0:
            raise ValueError(
                "The value must be bigger than 1 and smaller than 64 due to signed 64-bit compatibility."
            )
        return value

    @field_validator("bits")
    def check_bits_range(cls, value: int) -> int:
        if value > 63:
            raise ValueError("Bits must be 63 or less for signed 64-bit compatibility.")
        elif value <= 0:
            raise ValueError("Bits must be bigger than 0, but less than 63 for signed 64-bit compatibility.")
        return value


zkp_settings = Settings()

if __name__ == "__main__":
    print(f"{zkp_settings.p=}")
    print(f"{zkp_settings.q=}")
    print(f"{zkp_settings.g=}")
    print(f"{zkp_settings.h=}")
    print(f"{zkp_settings.flavour=}")
    print(f"{zkp_settings.bits=}")
    print(f"{zkp_settings.log_level=}")
