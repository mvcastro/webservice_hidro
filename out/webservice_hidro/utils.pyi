import pandas as pd
from typing import Any
from webservice_hidro.models import Inventario as Inventario

def as_dataframe(dados: dict[str, Any] | Inventario) -> pd.DataFrame: ...
