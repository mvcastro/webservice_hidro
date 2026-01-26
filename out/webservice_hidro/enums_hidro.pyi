from enum import IntEnum, StrEnum

class TipoDeEstacao(IntEnum):
    FLUVIOMETRICA = 1
    PLUVIOMETRICA = 2

class TipoDeDados(IntEnum):
    COTAS = 1
    CHUVAS = 2
    VAZOES = 3

class NivelDeConsistencia(IntEnum):
    BRUTO = 1
    CONSISTIDO = 2

class Telemetrica(IntEnum):
    SIM = 1
    NAO = 0

class TipoDeVariavel(StrEnum):
    CHUVA = 'Chuva'
    VAZAO = 'Vazao'
    COTA = 'Cota'
