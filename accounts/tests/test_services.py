import pytest
from unittest.mock import MagicMock, patch
from accounts.services import efetuar_registro_usuario

# Verifica se a função 'login' do Django é acionada assim que um novo perfil é registrado no serviço
def test_efetuar_registro_usuario():
    """Garante que ao registrar o usuário, a função login seja invocada automaticamente."""
    mock_form = MagicMock()
    mock_user = MagicMock()
    mock_form.save.return_value = mock_user
    mock_request = MagicMock()
    
    with patch('accounts.services.login') as mock_login:
        user_returned = efetuar_registro_usuario(mock_request, mock_form)
        
        mock_form.save.assert_called_once()
        mock_login.assert_called_once_with(mock_request, mock_user)
        assert user_returned == mock_user
