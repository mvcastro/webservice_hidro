import os

import geopandas as gpd
import matplotlib.pyplot as plt
import pandas as pd

import webservice_hidro as hidro



def exporta_dados_hidro():

    codEstDE = input('Código de 8 dígitos da estação - INICIAL (Ex.: 00047000):')
    codEstATE = input('Código de 8 dígitos da estação - FINAL (Ex.: 90300000):')
    tpEst = input('Tipo da estação (1-Flu ou 2-Plu):')
    nmEst = input('Nome da Estação (Ex.: Barra Mansa):')
    nmRio = input('Nome do Rio (Ex.: Rio Javari):')
    codSubBacia = input('Código da Sub-Bacia hidrografica (Ex.: 10):')
    codBacia = input('Código da Bacia hidrografica (Ex.: 1):')
    nmMunicipio = input('Município (Ex.: Itaperuna):')
    nmEstado = input('Estado (Ex.: Rio de Janeiro):')
    sgResp = input('Sigla do Responsável pela estação (Ex.: ANA):')
    sgOper = input('Sigla da Operadora da estação (Ex.: CPRM):')
    telemetrica = input('telemetrica (Ex: 1-SIM ou 0-NÃO):')

    while True:
        path = str(input("""Digite o caminho onde o arquivo será salvo (Exemplo: C:/Temp):"""))
        try:
            if os.path.exists(path):
                break
            else:
                raise ValueError("Digite um diretório válido!")
        except ValueError as er:
            print(er)

    # Requisita do webserice o DataFrame de dados
    # do inventário de estações selecionadas
    df_hidro = hidro.retorna_inventario(
        codEstDE=codEstDE,
        codEstATE=codEstATE,
        tpEst=tpEst,
        nmEst=nmEst,
        nmRio=nmRio,
        codSubBacia=codSubBacia,
        codBacia=codBacia,
        nmMunicipio=nmMunicipio,
        nmEstado=nmEstado,
        sgResp=sgResp,
        sgOper=sgOper,
        telemetrica=telemetrica
    )

    if df_hidro.empty:
        raise ValueError("Código da(s) estações não existente(s)!")

    invent_path = os.path.join(path, "exporta_inventario_hidro.csv")
    df_hidro.to_csv(invent_path, index=False, sep=";", decimal=",")

    # Requisita do webserice o DataFrame de dados
    # das séries históricas das estações selecionadas
    for _, row in df_hidro.iterrows():

        tipo_estacao = int(row['TipoEstacao'])
        cod_estacao = row['Codigo']

        # Estacao Fluviometrica
        if tipo_estacao == hidro.TipoDeEstacao.FLUVIOMETRICA.value:

            for tipo_dados in [hidro.TipoDeDados.COTAS, hidro.TipoDeDados.VAZOES]:

                df_serie = hidro.retorna_serie_historica(
                    codEstacao=cod_estacao,
                    tipoDados=tipo_dados,
                    dataInicio="01/01/1900",
                    dataFim=""
                )
                file_path = os.path.join(path, f"serie_{tipo_dados.name}_estacao_{cod_estacao}.csv")
                df_serie.to_csv(file_path, index=False, sep=";", decimal=",")

        if tipo_estacao == hidro.TipoDeEstacao.PLUVIOMETRICA:

            tipo_dados = hidro.TipoDeDados.CHUVAS

            df_serie = hidro.retorna_serie_historica(
                codEstacao=cod_estacao,
                tipoDados=tipo_dados,
                dataInicio="01/01/1900",
                dataFim=""
            )
            file_path = os.path.join(path, f"serie_{tipo_dados.name}_estacao_{cod_estacao}.csv")
            df_serie.to_csv(file_path, index=False, sep=";", decimal=",")


def exporta_dados_hidro_por_geometria(
    caminho_geometria: str,
    tipo_de_dados: hidro.TipoDeDados,
    diretorio_saida: str,
    data_inicial: str = '01/01/1900',
    data_final: str = ''
) -> None:
    """Exporta dados das Estações em arquiovs CSV que interseccionam a geometria
        passada como parâmetro em formato shape pu geopackage

    Args:
        caminho_geometria (str): Caminho onde se encontra o qruivos com a geometria
            [Shape (.shp) ou Geopackage (.gpkg)]
        tipo_de_dados (hidro.TipoDeDados): Tipo de Dado: 1=COTAS; 2=CHUVAS; 3=VAZOES
        diretorio_saida (str): Diretório onde se deseja salvar os arquivos CSV
        data_inicial (str, optional): Data inicial das séries temporais. Defaults to '01/01/1900'.
        data_final (str, optional): Data Final das séries temporais. Defaults to ''.
    """
    
    gdf = gpd.read_file(filename=caminho_geometria)
    
    if gdf.shape[0] == 1:
        geometria_poligono = gdf.geometry
    else:
        geometria_poligono = gdf.geometry.unary_union
        
    if tipo_de_dados in [hidro.TipoDeDados.COTAS, hidro.TipoDeDados.VAZOES]:
        tipo_estacao = hidro.TipoDeEstacao.FLUVIOMETRICA
    else:
        tipo_estacao = hidro.TipoDeEstacao.PLUVIOMETRICA
        
    # Requisita do webserice o DataFrame de dados
    # do inventário de estações selecionadas
    df_hidro = hidro.retorna_inventario(tpEst=tipo_estacao)
    geometria_estacoes = gpd.points_from_xy(
        x=df_hidro['Longitude'],
        y=df_hidro['Latitude'],
        crs='EPSG:4674'
    )
    gdf_estacoes = gpd.GeoDataFrame(df_hidro, geometry=geometria_estacoes)
    
    codigo_estacoes_selecionadas = [
        estacao['Codigo'] for _, estacao in gdf_estacoes.iterrows()
        if estacao.geometry.intersects(geometria_poligono)
    ]
    
    print(f'Foram identificados {len(codigo_estacoes_selecionadas)} estações '
          'que se encontram no interior do polígono!')
    
    for codigo_estacao in codigo_estacoes_selecionadas:
        print(f'Buscando dados para a estação com código {codigo_estacao}...')
    
        df_serie = hidro.retorna_serie_historica(
            codEstacao=codigo_estacao,
            tipoDados=tipo_de_dados,
            dataInicio=data_inicial,
            dataFim=data_final
        )
        
        if df_serie.empty:
            print(
                f'Estação com código {codigo_estacao} não apresenta dados para '
                'o período selecionado.'
            )
            continue
        
        hidro.reorganiza_serie_em_coluna(df_serie)\
             .to_csv(os.path.join(diretorio_saida, f'dados_estacao_{codigo_estacao}.csv'))
        
        print(f'Dados da estação {codigo_estacao} salvos em arquivo CSV.')


