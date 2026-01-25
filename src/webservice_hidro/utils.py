from typing import Any
import pandas as pd

from webservice_hidro.models import Inventario


def as_dataframe(dados: dict[str, Any] | Inventario) -> pd.DataFrame:
    return pd.DataFrame(dados)