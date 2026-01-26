import unittest
from unittest.mock import Mock, patch

from webservice_hidro.webservice_access.rio import retorna_rio_por_codigo

# Helper XML for successful Rio response
RIO_XML_SUCCESS = b"""
    <NewDataSet>
        <Table>
            <BaciaCodigo>1</BaciaCodigo>
            <SubBaciaCodigo>10</SubBaciaCodigo>
            <Codigo>12345</Codigo>
            <Nome>Rio Amazonas</Nome>
        </Table>
    </NewDataSet>
"""

# Helper XML for error response
RIO_XML_ERROR = b"""
    <NewDataSet>
        <Table1>
            <Vazio>Nenhum rio encontrado com o codigo informado</Vazio>
        </Table1>
    </NewDataSet>
"""


class TestRioWebService(unittest.TestCase):
    """
    Testes para a função retorna_inventario do módulo rio.

    A função retorna_inventario faz uma requisição HTTP para obter informações
    sobre um rio específico através de um código de rio (codRio).
    """

    @patch("webservice_hidro.webservice_access.rio.requests.get")
    def test_retorna_rio_success(self, mock_get: Mock):
        """
        Testa se a função retorna um objeto Rio com os dados corretos
        quando a API retorna uma resposta válida.
        """
        # Arrange
        mock_get.return_value = Mock(content=RIO_XML_SUCCESS)
        cod_rio = "12345"

        # Act
        result = retorna_rio_por_codigo(cod_rio)

        # Assert
        assert isinstance(result, dict)
        assert result["BaciaCodigo"] == "1"
        assert result["SubBaciaCodigo"] == "10"
        assert result["Codigo"] == "12345"
        assert result["Nome"] == "Rio Amazonas"
        mock_get.assert_called_once()

    @patch("webservice_hidro.webservice_access.rio.requests.get")
    def test_retorna_rio_error(self, mock_get: Mock):
        """
        Testa se a função lança uma exceção ValueError quando
        a API retorna uma resposta com erro (campo 'Vazio' presente).
        """
        # Arrange
        mock_get.return_value = Mock(content=RIO_XML_ERROR)
        cod_rio = "99999"

        # Act & Assert
        with self.assertRaises(ValueError) as context:
            retorna_rio_por_codigo(cod_rio)

        assert "Nenhum rio encontrado" in str(context.exception)

    @patch("webservice_hidro.webservice_access.rio.requests.get")
    def test_retorna_rio_request_params(self, mock_get: Mock):
        """
        Testa se a função envia os parâmetros corretos na requisição HTTP.
        """
        # Arrange
        mock_get.return_value = Mock(content=RIO_XML_SUCCESS)
        cod_rio = "12345"

        # Act
        retorna_rio_por_codigo(cod_rio)

        # Assert
        mock_get.assert_called_once()
        args, kwargs = mock_get.call_args
        assert "telemetriaws1.ana.gov.br" in args[0]
        assert "HidroRio" in args[0]
        assert kwargs["params"]["codRio"] == cod_rio


if __name__ == "__main__":
    unittest.main()
