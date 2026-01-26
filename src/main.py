from webservice_hidro import retorna_rio_por_codigo, retorna_subbacia_por_codigo


rio = retorna_rio_por_codigo(47300000)
print(rio)
# rio = retorna_rio_por_codigo("12345")


subbacia = retorna_subbacia_por_codigo(64)
print(subbacia)
# subbacia = retorna_subbacia_por_codigo(0)