import xml.etree.ElementTree as ET
from typing import cast

import requests

from webservice_hidro.models import Subbacia


def retorna_subbacia_por_codigo(codSubBacia: str | int) -> Subbacia:
    url_hidro_subbacia = (
        "http://telemetriaws1.ana.gov.br/ServiceANA.asmx/HidroBaciaSubBacia"
    )
    resp = requests.get(url_hidro_subbacia, params={"codBacia": "", "codSubBacia": codSubBacia})
    data = resp.content
    root = ET.XML(data)

    subbacia = {}
    for estacao in root.iter("Table"):
        subbacia = {dado.tag: dado.text for dado in estacao}

    if not subbacia:
        for estacao in root.iter("Table1"):
            subbacia = {dado.tag: dado.text for dado in estacao}
        raise ValueError(subbacia.get("Vazio"))

    return Subbacia(**cast(Subbacia, subbacia))
