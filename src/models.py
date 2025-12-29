from abc import ABC
from dataclasses import dataclass
from datetime import date
from typing import Literal

from enums_hidro import NivelDeConsistencia


@dataclass
class PivotSerie(ABC):
    EstacaoCodigo: int
    Data: date
    NivelConsistencia: NivelDeConsistencia | Literal[0, 1]

    def __post_init__(self):
        if type(self) is PivotSerie:
            raise NotImplementedError(
                "This is a base class and cannot be instantiated directly."
            )


@dataclass
class PivotCota(PivotSerie):
    Cota: float | None


@dataclass
class PivotChuva(PivotSerie):
    Chuva: float | None


@dataclass
class PivotVazao(PivotSerie):
    Vazao: float | None
