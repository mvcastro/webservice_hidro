from .enums_hidro import NivelDeConsistencia as NivelDeConsistencia
from abc import ABC
from dataclasses import dataclass
from datetime import date
from typing import Literal, TypedDict

class Inventario(TypedDict):
    BaciaCodigo: str | None
    SubBaciaCodigo: str | None
    RioCodigo: str | None
    RioNome: str | None
    EstadoCodigo: str | None
    nmEstado: str | None
    MunicipioCodigo: str | None
    nmMunicipio: str | None
    ResponsavelCodigo: str | None
    ResponsavelSigla: str | None
    ResponsavelUnidade: str | None
    ResponsavelJurisdicao: str | None
    OperadoraCodigo: str | None
    OperadoraSigla: str | None
    OperadoraUnidade: str | None
    OperadoraSubUnidade: str | None
    TipoEstacao: str | None
    Codigo: str | None
    Nome: str | None
    CodigoAdicional: str | None
    Latitude: str | None
    Longitude: str | None
    Altitude: str | None
    AreaDrenagem: str | None
    TipoEstacaoEscala: str | None
    TipoEstacaoRegistradorNivel: str | None
    TipoEstacaoDescLiquida: str | None
    TipoEstacaoSedimentos: str | None
    TipoEstacaoQualAgua: str | None
    TipoEstacaoPluviometro: str | None
    TipoEstacaoRegistradorChuva: str | None
    TipoEstacaoTanqueEvapo: str | None
    TipoEstacaoClimatologica: str | None
    TipoEstacaoPiezometria: str | None
    TipoEstacaoTelemetrica: str | None
    PeriodoEscalaInicio: str | None
    PeriodoEscalaFim: str | None
    PeriodoRegistradorNivelInicio: str | None
    PeriodoRegistradorNivelFim: str | None
    PeriodoDescLiquidaInicio: str | None
    PeriodoDescLiquidaFim: str | None
    PeriodoSedimentosInicio: str | None
    PeriodoSedimentosFim: str | None
    PeriodoQualAguaInicio: str | None
    PeriodoQualAguaFim: str | None
    PeriodoPluviometroInicio: str | None
    PeriodoPluviometroFim: str | None
    PeriodoRegistradorChuvaInicio: str | None
    PeriodoRegistradorChuvaFim: str | None
    PeriodoTanqueEvapoInicio: str | None
    PeriodoTanqueEvapoFim: str | None
    PeriodoClimatologicaInicio: str | None
    PeriodoClimatologicaFim: str | None
    PeriodoPiezometriaInicio: str | None
    PeriodoPiezometriaFim: str | None
    PeriodoTelemetricaInicio: str | None
    PeriodoTelemetricaFim: str | None
    TipoRedeBasica: str | None
    TipoRedeEnergetica: str | None
    TipoRedeNavegacao: str | None
    TipoRedeCursoDagua: str | None
    TipoRedeEstrategica: str | None
    TipoRedeCaptacao: str | None
    TipoRedeSedimentos: str | None
    TipoRedeQualAgua: str | None
    TipoRedeClasseVazao: str | None
    UltimaAtualizacao: str | None
    Operando: str | None
    Descricao: str | None
    NumImagens: str | None
    DataIns: str | None
    DataAlt: str | None

class Rio(TypedDict):
    BaciaCodigo: int
    SubBaciaCodigo: int
    Codigo: int
    Nome: str

class Subbacia(TypedDict):
    codBacia: int
    nmBacia: str
    codSubBacia: int
    nmSubBacia: str

@dataclass
class PivotSerie(ABC):
    EstacaoCodigo: int
    Data: date
    NivelConsistencia: NivelDeConsistencia | Literal[0, 1]
    def __post_init__(self) -> None: ...

@dataclass
class PivotCota(PivotSerie):
    Cota: float | None

@dataclass
class PivotChuva(PivotSerie):
    Chuva: float | None

@dataclass
class PivotVazao(PivotSerie):
    Vazao: float | None
