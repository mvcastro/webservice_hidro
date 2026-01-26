from _typeshed import Incomplete
from webservice_hidro.webservice_access import serie_historica as hidro

ASSOCIACAO_VARIAVEL_TIPO_DADO: Incomplete

def exporta_dados_hidro() -> None: ...
def exporta_dados_hidro_por_geometria(caminho_geometria: str, tipo_de_dados: hidro.TipoDeDados, diretorio_saida: str, data_inicial: str = '01/01/1900', data_final: str = '') -> None: ...
