import webservice_hidro.webservice_hidro as hidro

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
    path = str(input("""Digite o caminho onde o arquivo será salvo (Exemplo: C:/Temp):"""))

    # Requisita do webserice o dicionário de dados 
    # do inventário de estações selecionadas
    dict_hidro = hidro.retorna_inventario(codEstDE, codEstATE, tpEst,
                        nmEst, nmRio, codSubBacia,
                        codBacia, nmMunicipio,
                        nmEstado, sgResp,
                        sgOper, telemetrica)
    file_path = path + '/exporta_hidro_inventario.csv'

    gera_arquivo(file_path, dict_hidro)
    
    # Requisita do webserice o dicionário de dados
    # das séries históricas das estações selecionadas
    for propriedades in dict_hidro.values():
        if propriedades['TipoEstacao'] == '1':
            # Estacao Fluviometrica
            for i in range(1, 4, 2):
                dict_series = hidro.retorna_serie_historica(\
                        codEstacao=propriedades['Codigo'],\
                        dataInicio='01/01/1900', dataFim='',\
                        tiposDados=i, nivelConsistencia='')
                if i==1: # Cota 
                    file_path = path + '/serie_cota_estacao_' + str(propriedades['Codigo']) + '.csv'
                if i==3: # Vazao
                    file_path = path + '/serie_vazao_estacao_' + str(propriedades['Codigo']) + '.csv'
                
                gera_arquivo(file_path, dict_series)

        
        if propriedades['TipoEstacao'] == '2':
            dict_series = hidro.retorna_serie_historica(\
                codEstacao=propriedades['Codigo'],\
                dataInicio='01/01/1900', dataFim='',\
                tiposDados=2, nivelConsistencia='')
            file_path = path + '/serie_chuva_' + str(propriedades['Codigo']) + '.csv'
            gera_arquivo(file_path, dict_series)

def gera_arquivo(file_path, dict_hidro):
    with open(file_path, 'w') as file:
        head = None
        for dict_prop in dict_hidro.values():
            if head is None:
                head = dict_prop.keys()
                file.write(str(';'.join(head))+ '\n')
            prop = ''
            for valor in dict_prop.values():
                if valor is None:
                    prop += ';'
                else:
                    prop += str(valor) + ';'

            file.write(prop + '\n')

if __name__ == "__main__":
    exporta_dados_hidro()
