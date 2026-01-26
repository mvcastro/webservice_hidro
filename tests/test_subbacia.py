import unittest
from unittest.mock import Mock, patch

from webservice_hidro.webservice_access.subbacia import retorna_subbacia_por_codigo

# Helper XML for successful Subbacia response (Table tag)
SUBBACIA_XML_TABLE_SUCCESS = b"""
    <NewDataSet>
        <Table>
            <codBacia>1</codBacia>
            <nmBacia>10</nmBacia>
            <codSubBacia>101</codSubBacia>
            <nmSubBacia>Rio Branco</nmSubBacia>
        </Table>
    </NewDataSet>
"""


# Helper XML for error response (empty with Vazio field)
SUBBACIA_XML_ERROR = b"""
    <NewDataSet>
        <Table1>
            <Vazio>Nenhuma subbacia encontrada com o codigo informado</Vazio>
        </Table1>
    </NewDataSet>
"""

# Helper XML for empty response (no data found)
SUBBACIA_XML_EMPTY = b"""
    <NewDataSet>
    </NewDataSet>
"""


class TestSubbaciaWebService(unittest.TestCase):
    """
    Testes para a função retorna_subbacia_por_codigo do módulo subbacia.

    A função retorna_subbacia_por_codigo faz uma requisição HTTP para obter
    informações sobre uma subbacia específica através de um código.
    """

    @patch("webservice_hidro.webservice_access.subbacia.requests.get")
    def test_retorna_subbacia_table_success(self, mock_get: Mock):
        """
        Testa se a função retorna um objeto Subbacia com os dados corretos
        quando a API retorna uma resposta válida na tag Table.
        """
        # Arrange
        mock_get.return_value = Mock(content=SUBBACIA_XML_TABLE_SUCCESS)
        cod_subbacia = 101

        # Act
        result = retorna_subbacia_por_codigo(cod_subbacia)

        # Assert
        assert isinstance(result, dict)
        assert result["codBacia"] == "1"
        assert result["nmBacia"] == "10"
        assert result["codSubBacia"] == "101"
        assert result["nmSubBacia"] == "Rio Branco"
        mock_get.assert_called_once()

    @patch("webservice_hidro.webservice_access.subbacia.requests.get")
    def test_retorna_subbacia_error_vazio(self, mock_get: Mock):
        """
        Testa se a função lança uma exceção ValueError quando
        a API retorna uma resposta com erro (campo 'Vazio' presente).
        """
        # Arrange
        mock_get.return_value = Mock(content=SUBBACIA_XML_ERROR)
        cod_subbacia = 99999

        # Act & Assert
        with self.assertRaises(ValueError) as context:
            retorna_subbacia_por_codigo(cod_subbacia)

        assert "Nenhuma subbacia encontrada" in str(context.exception)

    @patch("webservice_hidro.webservice_access.subbacia.requests.get")
    def test_retorna_subbacia_error_empty_response(self, mock_get: Mock):
        """
        Testa se a função lança um erro quando a API retorna
        um XML vazio sem dados em Table ou Table1.
        """
        # Arrange
        mock_get.return_value = Mock(content=SUBBACIA_XML_EMPTY)
        cod_subbacia = 00000

        # Act & Assert
        with self.assertRaises((ValueError, TypeError)):
            retorna_subbacia_por_codigo(cod_subbacia)

    @patch("webservice_hidro.webservice_access.subbacia.requests.get")
    def test_retorna_subbacia_request_params_string(self, mock_get: Mock):
        """
        Testa se a função envia os parâmetros corretos na requisição HTTP
        quando o código é uma string.
        """
        # Arrange
        mock_get.return_value = Mock(content=SUBBACIA_XML_TABLE_SUCCESS)
        cod_subbacia = "101"

        # Act
        retorna_subbacia_por_codigo(cod_subbacia)

        # Assert
        mock_get.assert_called_once()
        args, kwargs = mock_get.call_args
        assert "telemetriaws1.ana.gov.br" in args[0]
        assert "HidroBaciaSubBacia" in args[0]
        assert kwargs["params"]["codSubBacia"] == cod_subbacia
        assert kwargs["params"]["codBacia"] == ""

    @patch("webservice_hidro.webservice_access.subbacia.requests.get")
    def test_retorna_subbacia_request_params_int(self, mock_get: Mock):
        """
        Testa se a função envia os parâmetros corretos na requisição HTTP
        quando o código é um inteiro.
        """
        # Arrange
        mock_get.return_value = Mock(content=SUBBACIA_XML_TABLE_SUCCESS)
        cod_subbacia = 101

        # Act
        retorna_subbacia_por_codigo(cod_subbacia)

        # Assert
        mock_get.assert_called_once()
        args, kwargs = mock_get.call_args
        assert "telemetriaws1.ana.gov.br" in args[0]
        assert "HidroBaciaSubBacia" in args[0]
        assert kwargs["params"]["codSubBacia"] == cod_subbacia
        assert kwargs["params"]["codBacia"] == ""

    @patch("webservice_hidro.webservice_access.subbacia.requests.get")
    def test_retorna_subbacia_multiple_tables(self, mock_get: Mock):
        """
        Testa o comportamento quando existem múltiplos elementos Table.
        A função deve retornar o último encontrado (sobrescrito pelos loops).
        """
        # Arrange
        multi_table_xml = b"""
            <NewDataSet>
                <Table>
                    <codBacia>1</codBacia>
                    <nmBacia>10</nmBacia>
                    <codSubBacia>101</codSubBacia>
                    <nmSubBacia>Rio Branco</nmSubBacia>
                </Table>
                <Table>
                    <codBacia>1</codBacia>
                    <nmBacia>10</nmBacia>
                    <codSubBacia>102</codSubBacia>
                    <nmSubBacia>Rio Acre</nmSubBacia>
                </Table>
            </NewDataSet>
        """
        mock_get.return_value = Mock(content=multi_table_xml)
        cod_subbacia = 101

        # Act
        result = retorna_subbacia_por_codigo(cod_subbacia)

        # Assert
        assert isinstance(result, dict)
        # O resultado deve ser o último elemento processado
        assert result["codSubBacia"] == "102"
        assert result["nmSubBacia"] == "Rio Acre"


if __name__ == "__main__":
    unittest.main()
