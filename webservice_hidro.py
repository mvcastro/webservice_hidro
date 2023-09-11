from enum import IntEnum
import xml.etree.ElementTree as ET
import numpy as np
import pandas as pd
import requests


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


def retorna_inventario(codEstDE: str | int = "",
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
                       telemetrica: str | int = "") -> pd.DataFrame:
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

    params = locals()
    params['tpEst'] = tpEst.value if type(tpEst) == TipoDeEstacao else tpEst

    url_hidro_inventario = "http://telemetriaws1.ana.gov.br/ServiceANA.asmx/HidroInventario"
    resp = requests.get(url_hidro_inventario, params=params)
    data = resp.content
    root = ET.XML(data)

    lista_dados = []
    for estacao in root.iter("Table"):
        dic_estacao = {}
        for dado in estacao:
            dic_estacao[dado.tag] = dado.text
        lista_dados.append(dic_estacao)

    return pd.DataFrame(lista_dados)


def retorna_serie_historica(codEstacao: str | int,
                            tipoDados: TipoDeDados,
                            dataInicio: str = "",
                            dataFim: str = "",
                            nivelConsistencia: int = 2) -> pd.DataFrame:
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

    params = locals()
    params['tipoDados'] = tipoDados.value
    url_hidro_serie_historica = "http://telemetriaws1.ana.gov.br/ServiceANA.asmx/HidroSerieHistorica"
    resp = requests.get(url_hidro_serie_historica, params=params)
    data = resp.content
    root = ET.XML(data)

    serie_historica = []
    for serie in root.iter("SerieHistorica"):
        dic_serie = {}
        for dado in serie:
            dic_serie[dado.tag] = dado.text
        serie_historica.append(dic_serie)

    return pd.DataFrame(serie_historica)


def __analise_datas(row, variable: str) -> np.datetime64 | None:
    """Define se existe a data no DataFrame da série histórica do HidroWeb.

    Args:
        row (p.Series): Linha do DataFrame da série histórica.

    Returns:
        np.datetime64 or None : Retorna data.
    """
    data = row['Data']
    dado_var = row['variable']

    dias_finais_do_mes = [f'{variable}{i}' for i in (29, 30, 31)]

    if dado_var == dias_finais_do_mes[-1] and data.month in (4, 6, 9, 11):
        return None

    if (not data.is_leap_year and data.month == 2 and dado_var in dias_finais_do_mes):
        return None

    if (data.is_leap_year and data.month == 2 and dado_var in dias_finais_do_mes[1:]):
        return None

    result = data + np.timedelta64(int(dado_var[5:])-1, 'D')

    return result


def reorganiza_serie_em_coluna(serie_historica: pd.DataFrame) -> pd.DataFrame:
    """Reorganiza o DataFrame da série histórica com os dados
       em uma única coluna sequencial de data.

    Args:
        serie_historica (pd.DataFrame): DataFrame original extraída do webservice

    Returns:
        pd.DataFrame: DataFrame com dados em sequência de data.
    """

    var = serie_historica.columns[-2][:-8]
    colunas = [f"{var}{i:02}" for i in range(1, 32)]

    df2 = serie_historica[['DataHora', 'NivelConsistencia'] + colunas]
    df_melt = df2.melt(id_vars=['DataHora', 'NivelConsistencia'])
    df_melt['Data'] = pd.to_datetime(df_melt['DataHora'])
    df_melt['Data2'] = df_melt.apply(__analise_datas, args=(var,), axis=1)  # type:ignore

    df_final = df_melt[['Data2', 'value', 'NivelConsistencia']].copy()
    df_final.rename(columns={'Data2': 'Data', 'value': 'Valor'}, inplace=True)
    df_final = df_final.dropna(subset=['Data'])\
                       .astype({'Valor': float})\
                       .set_index('Data', drop=True)

    return df_final.sort_index()
