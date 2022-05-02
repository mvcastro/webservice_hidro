# webservice_hidro
Python scripts to extract data from HIDRO Webservice (ANA)

Scripts em Python para extrair os dados requisitados do Webservice HIDRO da Agência Nacional de Águas (ANA),  armazenando-os em arquivo csv.

~~~~python

from webservice_hidro import retorna_inventario

# Seleção do inventário de estações fluviométricas no Estado de Alagoas
inventario = retorna_inventario(tpEst=1, nmEstado="ALAGOAS")

print(inventario.head())

~~~~

Resultado (10 primeiras colunas):
|    |   BaciaCodigo |   SubBaciaCodigo |   RioCodigo | RioNome      |   EstadoCodigo | nmEstado   |   MunicipioCodigo | nmMunicipio        |   ResponsavelCodigo | ResponsavelSigla   |
|---:|--------------:|-----------------:|------------:|:-------------|---------------:|:-----------|------------------:|:-------------------|--------------------:|:-------------------|
|  0 |             3 |               39 |    39742000 | RIO JACUÍPE  |             13 | ALAGOAS    |          13021000 | COLÔNIA LEOPOLDINA |                 104 | CPRH-PE            |
|  1 |             3 |               39 |    39742000 | RIO JACUÍPE  |             13 | ALAGOAS    |          13035000 | JACUÍPE            |                   1 | ANA                |
|  2 |             3 |               39 |    39742000 | RIO JACUÍPE  |             13 | ALAGOAS    |          13035000 | JACUÍPE            |                 121 | SEMARH-AL          |
|  3 |             3 |               39 |    39751500 | RIO MARAGOGI |             13 | ALAGOAS    |          13045000 | MARAGOGI           |                 121 | SEMARH-AL          |
|  4 |             3 |               39 |    39753500 | RIO MANGUABA |             13 | ALAGOAS    |          13073000 | PORTO CALVO        |                   1 | ANA                |


~~~~python

from webservice_hidro import retorna_inventario

# Seleção dos dados brutos de vazão da estação fluviométrica
# PENEDO - Código: 49740000 em Penedo/Alagoas para o ano de 2021
serie_historica = retorna_serie_historica(codEstacao=49740000, tiposDados=3,
                            dataInicio="01/01/2021", dataFim="31/12/2021",
                            nivelConsistencia=1)

print(serie_historica.head())

~~~~

Resultado (10 primeiras colunas):

|    |   EstacaoCodigo |   NivelConsistencia | DataHora            |   MediaDiaria |   MetodoObtencaoVazoes | Maxima   | Minima   | Media   | DiaMaxima   | DiaMinima   |
|---:|----------------:|--------------------:|:--------------------|--------------:|-----------------------:|:---------|:---------|:--------|:------------|:------------|
|  3 |        49740000 |                   1 | 2021-05-01 00:00:00 |             1 |                      1 |          |          |         |             |             |
|  2 |        49740000 |                   1 | 2021-06-01 00:00:00 |             1 |                      1 |          |          |         |             |             |
|  1 |        49740000 |                   1 | 2021-07-01 00:00:00 |             1 |                      1 |          |          |         |             |             |
|  0 |        49740000 |                   1 | 2021-08-01 00:00:00 |             1 |                      1 |          |          |         |             |             |