from typing import cast
import xml.etree.ElementTree as ET

import requests

from webservice_hidro.models import Rio


def retorna_rio_por_codigo(codRio: str | int) -> Rio:
    url_hidro_rio = "http://telemetriaws1.ana.gov.br/ServiceANA.asmx/HidroRio"
    resp = requests.get(url_hidro_rio, params={"codRio": codRio})
    data = resp.content
    root = ET.XML(data)

    rio = {}
    for estacao in root.iter("Table"):
        rio = {dado.tag: dado.text for dado in estacao}
        
    if not rio:
        for estacao in root.iter("Table1"):
            rio = {dado.tag: dado.text for dado in estacao}
        raise ValueError(rio.get("Vazio"))

    return Rio(**cast(Rio, rio))
