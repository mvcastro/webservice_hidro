import xml.etree.ElementTree as ET
from dataclasses import asdict
from datetime import date

import pandas as pd
import requests

from models import PivotChuva, PivotCota, PivotVazao
from enums_hidro import (
    Telemetrica,
    TipoDeDados,
    TipoDeEstacao,
    TipoDeVariavel,
)

type PivotSerieType = type[PivotCota] | type[PivotChuva] | type[PivotVazao]
type PivotSerieInstance = PivotCota | PivotChuva | PivotVazao

CLASSES_VARIAVEIS: dict[TipoDeVariavel, PivotSerieType] = {
    TipoDeVariavel.COTA: PivotCota,
    TipoDeVariavel.CHUVA: PivotChuva,
    TipoDeVariavel.VAZAO: PivotVazao,
}


def retorna_inventario(
    codEstDE: str | int = "",
    codEstATE: str | int = "",
    tpEst: TipoDeEstacao | str | int = "",
    nmEst: str = "",
    nmRio: str = "",
    codSubBacia: str = "",
    codBacia: str = "",
    nmMunicipio: str = "",
    nmEstado: str = "",
    sgResp: str = "",
    sgOper: str = "",
    telemetrica: Telemetrica | str | int = "",
) -> pd.DataFrame:
    """Inventário pluviométrico/fluviométrico atualizado.

    Args:
        codEstDE (str, optional): Código de 8 dígitos da estação
                                    - INICIAL (Ex.: 00047000). Defaults to "".
        codEstATE (str, optional): Código de 8 dígitos da estação
                                    - FINAL (Ex.: 90300000). Defaults to "".
        tpEst (str, optional): Tipo da estação (1-Flu ou 2-Plu). Defaults to "".
        nmEst (str, optional): Nome da Estação (Ex.: Barra Mansa). Defaults to "".
        nmRio (str, optional): Nome do Rio (Ex.: Rio Javari). Defaults to "".
        codSubBacia (str, optional): Código da Sub-Bacia hidrografica (Ex.: 10). Defaults to "".
        codBacia (str, optional): Código da Bacia hidrografica (Ex.: 1). Defaults to "".
        nmMunicipio (str, optional): Município (Ex.: Itaperuna). Defaults to "".
        nmEstado (str, optional): Estado (Ex.: Rio de Janeiro). Defaults to "".
        sgResp (str, optional): Sigla do Responsável pela estação (Ex.: ANA). Defaults to "".
        sgOper (str, optional): Sigla da Operadora da estação (Ex.: CPRM). Defaults to "".
        telemetrica (str, optional): (Ex: 1-SIM ou 0-NÃO). Defaults to "".

    Returns:
        DataFrame: Retorna DataFrame com as propriedades das estações selecionadas do Inventário.
    """

    params = {
        "codEstDE": codEstDE,
        "codEstATE": codEstATE,
        "tpEst": tpEst,
        "nmEst": nmEst,
        "nmRio": nmRio,
        "codSubBacia": codSubBacia,
        "codBacia": codBacia,
        "nmMunicipio": nmMunicipio,
        "nmEstado": nmEstado,
        "sgResp": sgResp,
        "sgOper": sgOper,
        "telemetrica": telemetrica,
    }

    url_hidro_inventario = (
        "http://telemetriaws1.ana.gov.br/ServiceANA.asmx/HidroInventario"
    )
    resp = requests.get(url_hidro_inventario, params=params)
    data = resp.content
    root = ET.XML(data)

    lista_dados = []
    for estacao in root.iter("Table"):
        lista_dados.append({dado.tag: dado.text for dado in estacao})
    return pd.DataFrame(lista_dados)


def retorna_serie_historica(
    codEstacao: str | int,
    tipoDados: TipoDeDados,
    dataInicio: str = "",
    dataFim: str = "",
    nivelConsistencia: int = 2,
) -> pd.DataFrame:
    """Retorna DataFrame da série histórica da estação selecionada
       no formato da tabela do HidroWeb.

    Args:
        codEstacao (str): Código Plu ou Flu.
        tipoDados (int): 1-Cotas, 2-Chuvas ou 3-Vazões.
        dataInicio (str): Data inicial. Formato: dd/mm/aaaa
        dataFim (str, optional): Data inicial. Formato: dd/mm/aaaa. Defaults to "".
                                 Caso não preenchido, trará até o último dado mais recente.
        nivelConsistencia (int, optional): 1-Bruto ou 2-Consistido. Defaults to 2.

    Returns:
         DataFrame: Dicionário com os dados da série histórica.
    """

    params = {
        "codEstacao": codEstacao,
        "tipoDados": tipoDados,
        "dataInicio": dataInicio,
        "dataFim": dataFim,
        "nivelConsistencia": nivelConsistencia,
    }
    url_hidro_serie_historica = (
        "http://telemetriaws1.ana.gov.br/ServiceANA.asmx/HidroSerieHistorica"
    )
    resp = requests.get(url_hidro_serie_historica, params=params)
    data = resp.content
    root = ET.XML(data)

    errorTable = root.findall(".//ErrorTable")
    if errorTable:
        message = errorTable[0].findtext('Error')
        raise ValueError(message)

    serie_historica = []
    for serie in root.iter("SerieHistorica"):
        serie_historica.append({dado.tag: dado.text for dado in serie})
    return pd.DataFrame(serie_historica)


def reorganiza_serie_em_coluna(
    dados_api: pd.DataFrame, variavel: TipoDeVariavel
) -> pd.DataFrame:
    """Reorganiza o DataFrame da série histórica com os dados
       em uma única coluna sequencial de data.

    Args:
        serie_historica (pd.DataFrame): DataFrame original extraída do webservice

    Returns:
        pd.DataFrame: DataFrame com dados em sequência de data.
    """

    if variavel not in [member.value for member in TipoDeVariavel]:
        raise ValueError(
            f"O tipo de variável '{variavel}' não é válido. "
            f"Use um dos seguintes: {[member.value for member in TipoDeVariavel]}"
        )
        
    if not any(coluna.startswith(variavel) for coluna in dados_api.columns):
        raise ValueError(
            f"A variável '{variavel}' não está presente nas colunas do DataFrame fornecido."
        )

    data_attrs = ["EstacaoCodigo", "DataHora", "NivelConsistencia"] + [
        f"{variavel}{i:02d}" for i in range(1, 32)
    ]
    df = dados_api[data_attrs].copy()
    df["DataHora"] = pd.to_datetime(df.DataHora)
    pivot_rain_data: list[dict] = []

    for _, row in df.iterrows():
        codigo_estacao = row.EstacaoCodigo
        year = row.DataHora.year
        month = row.DataHora.month
        nivel_consistencia = row.NivelConsistencia

        for day_of_month, data in enumerate(row[3:], start=1):
            try:
                date_value = date(
                    year=year,
                    month=month,
                    day=day_of_month,
                )
                pivot_data: PivotSerieInstance = CLASSES_VARIAVEIS[variavel](
                    codigo_estacao,
                    date_value,
                    nivel_consistencia,
                    data if data is None else float(data),
                )
                pivot_rain_data.append(asdict(pivot_data))
            except ValueError:
                continue

    df = pd.DataFrame(pivot_rain_data)
    df["Data"] = pd.to_datetime(df.Data)

    return df.set_index("Data", drop=True).sort_index()
