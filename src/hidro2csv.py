import os
import src.webservice_hidro as hidro


def exporta_dados_hidro():

    codEstDE = input('Código de 8 dígitos da estação - INICIAL (Ex.: 00047000):')
    codEstATE = input('Código de 8 dígitos da estação - FINAL (Ex.: 90300000):')
    tipo_estacao = input('Tipo da estação (1-Flu ou 2-Plu):')
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
        tipo_estacao=tipo_estacao,
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


if __name__ == "__main__":
    exporta_dados_hidro()
