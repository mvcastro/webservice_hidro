import xml.etree.ElementTree as ET
from typing import Union

import numpy as np
import pandas as pd
import requests


def retorna_inventario(codEstDE: str = "", codEstATE: str = "",
                       tpEst: str = "", nmEst: str = "",
                       nmRio: str = "", codSubBacia: str = "",
                       codBacia: str = "", nmMunicipio: str = "",
                       nmEstado: str = "", sgResp: str = "",
                       sgOper: str = "", telemetrica: str = "") -> pd.DataFrame:
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

    url_hidro1 = "http://telemetriaws1.ana.gov.br"
    url_hidro2 = "/ServiceANA.asmx/HidroInventario?codEstDE={}".format(
        codEstDE)
    url_hidro3 = "&codEstATE={}&tpEst={}&nmEst={}&nmRio={}".format(
        codEstATE, tpEst, nmEst, nmRio)
    url_hidro4 = "&codSubBacia={}&codBacia={}&nmMunicipio={}".format(
        codSubBacia, codBacia, nmMunicipio)
    url_hidro5 = "&nmEstado={}&sgResp={}&sgOper={}&telemetrica={}".format(
        nmEstado, sgResp, sgOper, telemetrica)

    url_hidro = url_hidro1 + url_hidro2 + url_hidro3 + url_hidro4 + url_hidro5

    print(url_hidro)

    resp = requests.get(url_hidro)
    data = resp.content
    root = ET.XML(data)
    inventario = {}

    for elem in root:
        for estacoes in elem:
            for table in estacoes:
                if table.tag == "Table":
                    tabela = table.attrib.get(
                        "{urn:schemas-microsoft-com:xml-diffgram-v1}id"
                    )
                    propriedades = {}
                    for prop in table:
                        # print(prop.tag, prop.text, prop.attrib)
                        propriedades[prop.tag] = prop.text
                        inventario[tabela] = propriedades

    lst_informacoes = [inventario[i] for i in inventario]

    return pd.DataFrame(lst_informacoes)


def retorna_serie_historica(codEstacao: str, tiposDados: int,
                            dataInicio: str = "", dataFim: str = "",
                            nivelConsistencia: int = 2) -> pd.DataFrame:
    """Retorna DataFrame da série histórica da estação selecionada
       no formato da tabela do HidroWeb.

    Args:
        codEstacao (str): Código Plu ou Flu.
        tiposDados (int): 1-Cotas, 2-Chuvas ou 3-Vazões.
        dataInicio (str): Data inicial. Formato: dd/mm/aaaa
        dataFim (str, optional): Data inicial. Formato: dd/mm/aaaa. Defaults to "".
                                 Caso não preenchido, trará até o último dado mais recente.
        nivelConsistencia (int, optional): 1-Bruto ou 2-Consistido. Defaults to 2.

    Returns:
         DataFrame: Dicionário com os dados da série histórica.
    """

    url_hidro1 = "http://telemetriaws1.ana.gov.br"
    url_hidro2 = "/ServiceANA.asmx/HidroSerieHistorica?codEstacao={}&dataInicio={}".format(
        codEstacao, dataInicio)
    url_hidro3 = "&dataFim={}&tipoDados={}&nivelConsistencia={}".format(
        dataFim, tiposDados, nivelConsistencia)

    url_hidro = url_hidro1 + url_hidro2 + url_hidro3

    print(url_hidro)

    resp = requests.get(url_hidro)
    data = resp.content
    root = ET.XML(data)
    serie_historica = {}

    for elem in root:
        for estacoes in elem:
            for dado in estacoes:
                if dado.tag == "SerieHistorica":
                    id_serie = dado.attrib.get(
                        "{urn:schemas-microsoft-com:xml-diffgram-v1}id"
                    )
                    propriedades = {}
                    for prop in dado:
                        propriedades[prop.tag] = prop.text
                        serie_historica[id_serie] = propriedades

    lst_informacoes = [serie_historica[i] for i in serie_historica]

    serie_historica = pd.DataFrame(lst_informacoes)

    # serie_historica.sort_values('DataHora', inplace=True)

    return serie_historica


def __analise_datas(row: pd.Series) -> Union[np.datetime64, None]:
    """Define se existe a data no DataFrame da série histórica do HidroWeb.

    Args:
        row (p.Series): Linha do DataFrame da série histórica.

    Returns:
        np.datetime64 or None : Retorna data.
    """
    data = row['Data']
    var = row['variable']

    if var == 'Vazao31' and data.month in (4, 6, 9, 11):
        return None

    if (not data.is_leap_year and data.month == 2 and var in ('Vazao29', 'Vazao30', 'Vazao31')):
        return None

    if (data.is_leap_year and data.month == 2 and var in ('Vazao30', 'Vazao31')):
        return None

    result = data + np.timedelta64(int(var[5:])-1, 'D')

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

    colunas1 = [f'{var}0' + str(i) for i in range(1, 10)]
    colunas2 = [var + str(i) for i in range(10, 32)]
    colunas = colunas1 + colunas2

    df2 = serie_historica[['DataHora'] + colunas]

    df_melt = df2.melt(id_vars=['DataHora'])
    df_melt['Data'] = pd.to_datetime(df_melt['DataHora'])
    df_melt['Data2'] = df_melt.apply(__analise_datas, axis=1)
    df_melt.sort_values('Data2', inplace=True)

    df_final = df_melt[['Data2', 'value']].copy()
    df_final.columns = ['Data', 'Valor']
    df_final.dropna(subset=['Data'], inplace=True)
    df_final = df_final.astype({'Valor': float})
    df_final.reset_index(drop=True, inplace=True)

    return df_final
