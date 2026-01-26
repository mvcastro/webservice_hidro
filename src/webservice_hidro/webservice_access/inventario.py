import xml.etree.ElementTree as ET

import pandas as pd
import requests

from webservice_hidro.enums_hidro import (
    Telemetrica,
    TipoDeEstacao,
)
from webservice_hidro.models import Inventario


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
) -> list[Inventario]:
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
        list[Inventario]: Retorna uma `list` com dicionário do Tipo `Inventario` com as
            propriedades das estações selecionadas do Inventário.
    """

    params: dict[str, str | int] = {
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

    inventarios: list[Inventario] = []
    for estacao in root.iter("Table"):
        inventario = {dado.tag: dado.text for dado in estacao}
        inventarios.append(Inventario(**inventario))

    return inventarios


def retorna_inventario_em_dataframe(
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
    params: dict[str, str] = {
        "codEstDE": str(codEstDE),
        "codEstATE": str(codEstATE),
        "tpEst": str(tpEst),
        "nmEst": nmEst,
        "nmRio": nmRio,
        "codSubBacia": codSubBacia,
        "codBacia": codBacia,
        "nmMunicipio": nmMunicipio,
        "nmEstado": nmEstado,
        "sgResp": sgResp,
        "sgOper": sgOper,
        "telemetrica": str(telemetrica),
    }

    dados = retorna_inventario(**params)

    return pd.DataFrame(dados)
