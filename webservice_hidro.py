import requests
import xml.etree.ElementTree as ET
import pandas as pd


def retorna_inventario(codEstDE="", codEstATE="", tpEst="", 
                    nmEst="", nmRio="", codSubBacia="",
                    codBacia="", nmMunicipio="",
                    nmEstado="", sgResp="",
                    sgOper="", telemetrica=""):
    """Inventário pluviométrico/fluviométrico atualizado.
    codEstDE: Código de 8 dígitos da estação - INICIAL (Ex.: 00047000)
    codEstATE: Código de 8 dígitos da estação - FINAL (Ex.: 90300000)
    tpEst: Tipo da estação (1-Flu ou 2-Plu)
    nmEst: Nome da Estação (Ex.: Barra Mansa)
    nmRio: Nome do Rio (Ex.: Rio Javari)
    codSubBacia: Código da Sub-Bacia hidrografica (Ex.: 10)
    codBacia: Código da Bacia hidrografica (Ex.: 1)
    nmMunicipio: Município (Ex.: Itaperuna)
    nmEstado: Estado (Ex.: Rio de Janeiro)
    sgResp: Sigla do Responsável pela estação (Ex.: ANA)
    sgOper: Sigla da Operadora da estação (Ex.: CPRM)
    telemetrica: (Ex: 1-SIM ou 0-NÃO)"""

    url_hidro1 = "http://telemetriaws1.ana.gov.br"
    url_hidro2 = '/ServiceANA.asmx/HidroInventario?codEstDE={}\
&codEstATE={}&tpEst={}&nmEst={}&nmRio={}\
&codSubBacia={}&codBacia={}&nmMunicipio={}\
&nmEstado={}&sgResp={}&sgOper={}&telemetrica={}'\
.format(codEstDE, codEstATE, tpEst, nmEst, nmRio, 
            codSubBacia, codBacia, nmMunicipio, 
            nmEstado, sgResp, sgOper, telemetrica)

    url_hidro = url_hidro1 + url_hidro2

    print(url_hidro)

    resp = requests.get(url_hidro)
    data = resp.content
    root  = ET.XML(data)
    inventario = {}

    for elem in root:
        for estacoes in elem:
            for table in estacoes:
                if table.tag == 'Table':
                    tabela = table.attrib.get('{urn:schemas-microsoft-com:xml-diffgram-v1}id')
                    propriedades = {}
                    for prop in table:
                        #print(prop.tag, prop.text, prop.attrib)
                        propriedades[prop.tag] = prop.text
                        inventario[tabela] = propriedades
    return inventario


def retorna_serie_historica(codEstacao, dataInicio, dataFim, tiposDados, nivelConsistencia):
    """codEstacao: Código Plu ou Flu
    dataInicio
    dataFim: Caso não preenchido, trará até o último dado mais recente armazenado
    tipoDados: 1-Cotas, 2-Chuvas ou 3-Vazões
    nivelConsistencia: 1-Bruto ou 2-Consistido"""

    url_hidro1 = "http://telemetriaws1.ana.gov.br"
    url_hidro2 = '/ServiceANA.asmx/HidroSerieHistorica?codEstacao={}&dataInicio={}&dataFim={}&tipoDados={}&nivelConsistencia={}'\
                .format(codEstacao, dataInicio, dataFim, tiposDados, nivelConsistencia)

    url_hidro = url_hidro1 + url_hidro2

    print(url_hidro)

    resp = requests.get(url_hidro)
    data = resp.content
    root  = ET.XML(data)
    serie_historica = {}

    for elem in root:
        for estacoes in elem:
            for dado in estacoes:
                if dado.tag == 'SerieHistorica':
                    id_serie = dado.attrib.get('{urn:schemas-microsoft-com:xml-diffgram-v1}id')
                    propriedades = {}
                    for prop in dado:
                        propriedades[prop.tag] = prop.text
                        serie_historica[id_serie] = propriedades
    return serie_historica