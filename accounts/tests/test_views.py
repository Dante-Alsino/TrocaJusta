import pytest
from django.test import Client
from django.urls import reverse
from django.contrib.auth import get_user_model

User = get_user_model()

@pytest.fixture
def client():
    return Client()

@pytest.mark.django_db
def test_register_view_get(client):
    """Testa se a página de registro carrega corretamente."""
    url = reverse('register')
    response = client.get(url)
    assert response.status_code == 200
    assert 'accounts/register.html' in [t.name for t in response.templates]

@pytest.mark.django_db
def test_profile_view_bloqueado(client):
    """Garante que a página de perfil é restrita a usuários logados (@login_required)."""
    url = reverse('profile')
    response = client.get(url)
    assert response.status_code == 302
    assert '/login/' in response.url
