import pytest
from django.test import Client
from django.urls import reverse
from core.models import CustomUser, Categoria, Anuncio

@pytest.fixture
def client():
    return Client()

@pytest.fixture
def usuario_pendente(db):
    user = CustomUser.objects.create_user(
        email="pendente@test.com", username="pendente", password="123", status_conta="pendente", cidade="charqueadas"
    )
    return user

@pytest.fixture
def categoria(db):
    return Categoria.objects.create(nome_categoria="Teste", slug_busca="teste")

# Testa se a tentativa de criar um anúncio por inativos redireciona corretamente enviando a Flash Message de aviso
@pytest.mark.django_db
def test_ad_create_view_redireciona_inativo(client, usuario_pendente, categoria):
    client.force_login(usuario_pendente)
    url = reverse('ads:create')
    
    response = client.post(url, {
        'titulo_produto': 'Teste',
        'categoria': categoria.id,
        'preco_solicitado': 100,
        'descricao_detalhada': 'Teste inativo'
    })
    
    assert response.status_code == 302
    assert response.url == reverse('ads:my_ads')
    
    # Verifica a presença da message
    messages = list(response.wsgi_request._messages)
    assert len(messages) == 1
    assert "Sua conta precisa ser verificada" in str(messages[0])

# Valida se a vitrine principal (Catálogo Público) renderiza o template correto em HTTP 200
@pytest.mark.django_db
def test_ad_list_view_status(client):
    url = reverse('ads:list')
    response = client.get(url)
    
    assert response.status_code == 200
    assert 'ads/ad_list.html' in [t.name for t in response.templates]

# Garante que o painel de gerenciamento (Meus Anúncios) seja renderizado com status de sucesso (200)
@pytest.mark.django_db
def test_my_ads_view_status(client, usuario_pendente):
    client.force_login(usuario_pendente)
    url = reverse('ads:my_ads')
    response = client.get(url)
    assert response.status_code == 200
    assert 'ads/my_ads.html' in [t.name for t in response.templates]

# Avalia a rota de deleção via POST, checando se destrói a Model e redireciona de volta ao painel
@pytest.mark.django_db
def test_ad_delete_view(client, usuario_pendente, categoria):
    client.force_login(usuario_pendente)
    # Cria um anúncio manual via model direto para não estourar a regra de inativo no service
    anuncio = Anuncio.objects.create(
        perfil=usuario_pendente, categoria=categoria, titulo_produto="Teste Excluir", 
        descricao_detalhada="...", preco_solicitado=10, status_publicacao="ativo"
    )
    url = reverse('ads:delete', kwargs={'pk': anuncio.id})
    response = client.post(url)
    
    assert response.status_code == 302
    assert response.url == reverse('ads:my_ads')
    assert not Anuncio.objects.filter(id=anuncio.id).exists()
