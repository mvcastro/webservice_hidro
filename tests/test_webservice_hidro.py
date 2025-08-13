from unittest.mock import Mock, patch

import pandas as pd

# File: tests/test_webservice_hidro.py
from src.webservice_hidro import (
    TipoDeDados,
    TipoDeEstacao,
    TipoDeVariavel,
    reorganiza_serie_em_coluna,
    retorna_inventario,
    retorna_serie_historica,
)

# Helper XMLs
INVENTARIO_XML = b"""<NewDataSet>
<Table>
    <EstacaoCodigo>12345678</EstacaoCodigo>
    <NomeEstacao>Teste</NomeEstacao>
</Table>
</NewDataSet>"""

SERIE_XML = b"""<NewDataSet>
<SerieHistorica>
    <EstacaoCodigo>12345678</EstacaoCodigo>
    <DataHora>2024-06-01</DataHora>
    <NivelConsistencia>2</NivelConsistencia>
    <Chuva01>10.0</Chuva01>
    <Chuva02>5.0</Chuva02>
    <Chuva03></Chuva03>
</SerieHistorica>
</NewDataSet>"""


@patch("src.webservice_hidro.requests.get")
def test_retorna_inventario(mock_get):
    mock_get.return_value = Mock(content=INVENTARIO_XML)
    df = retorna_inventario(codEstDE="12345678", tpEst=TipoDeEstacao.FLUVIOMETRICA)
    assert not df.empty
    assert "EstacaoCodigo" in df.columns
    assert df.iloc[0]["EstacaoCodigo"] == "12345678"


@patch("src.webservice_hidro.requests.get")
def test_retorna_serie_historica(mock_get):
    mock_get.return_value = Mock(content=SERIE_XML)
    df = retorna_serie_historica(
        codEstacao="12345678",
        tipoDados=TipoDeDados.CHUVAS,
        dataInicio="01/06/2024",
        nivelConsistencia=2,
    )
    assert not df.empty
    assert "EstacaoCodigo" in df.columns
    assert df.iloc[0]["EstacaoCodigo"] == "12345678"
    assert df.iloc[0]["Chuva01"] == "10.0"


def test_reorganiza_serie_em_coluna():
    # Prepare input DataFrame
    data = {
        "EstacaoCodigo": [12345678],
        "DataHora": ["2024-06-01"],
        "NivelConsistencia": [2],
        "Chuva01": [10.0],
        "Chuva02": [5.0],
        "Chuva03": [None],
        # Fill up to Chuva31 with None
        **{f"Chuva{str(i).zfill(2)}": [None] for i in range(4, 32)},
    }
    df = pd.DataFrame(data)
    result = reorganiza_serie_em_coluna(df, TipoDeVariavel.CHUVA)
    assert isinstance(result, pd.DataFrame)
    assert "Chuva" in result.columns
    assert result.loc["2024-06-01", "Chuva"] == 10.0
    assert result.loc["2024-06-02", "Chuva"] == 5.0
    assert pd.isna(result.loc["2024-06-03", "Chuva"])
