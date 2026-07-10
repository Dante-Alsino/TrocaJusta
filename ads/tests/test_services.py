import pytest
from core.models import Anuncio, CustomUser, Categoria, Denuncia
from django.http import Http404
from ads.services import (
    create_anuncio, registrar_denuncia, AccountNotVerifiedError, DuplicateReportError,
    get_anuncios_ativos, gerar_link_whatsapp, delete_anuncio
)

@pytest.fixture
def categoria(db):
    return Categoria.objects.create(nome_categoria="Teste", slug_busca="teste")

@pytest.fixture
def usuario_ativo(db):
    return CustomUser.objects.create(
        email="ativo@test.com", username="ativo", status_conta="ativo", cidade="charqueadas"
    )

@pytest.fixture
def usuario_pendente(db):
    return CustomUser.objects.create(
        email="pendente@test.com", username="pendente", status_conta="pendente", cidade="charqueadas"
    )

@pytest.fixture
def anuncio(db, usuario_ativo, categoria):
    return Anuncio.objects.create(
        perfil=usuario_ativo, categoria=categoria, titulo_produto="Anúncio Teste", 
        descricao_detalhada="Teste", preco_solicitado=10.0, status_publicacao="ativo"
    )

# Garante que anúncios não podem ser criados por contas com status inativo/pendente
@pytest.mark.unit
@pytest.mark.django_db
def test_create_anuncio_usuario_inativo(usuario_pendente, categoria):
    with pytest.raises(AccountNotVerifiedError):
        create_anuncio(usuario_pendente, "Teste", categoria.id, 10.0, "Teste")

# Comprova o funcionamento do filtro anti-spam impedindo que a mesma denúncia seja feita duas vezes
@pytest.mark.unit
@pytest.mark.django_db
def test_registrar_denuncia_duplicada(usuario_ativo, anuncio):
    # Primeira denúncia
    registrar_denuncia(anuncio, usuario_ativo, "fraude", "Teste")
    # Segunda denúncia deve falhar
    with pytest.raises(DuplicateReportError):
        registrar_denuncia(anuncio, usuario_ativo, "fraude", "Teste 2")

# Simula o caminho feliz de um anúncio sendo gravado no banco de dados com status 'ATIVO'
@pytest.mark.unit
@pytest.mark.django_db
def test_create_anuncio_sucesso(usuario_ativo, categoria):
    anuncio = create_anuncio(usuario_ativo, "Anúncio Sucesso", categoria.id, 50.0, "Desc")
    assert Anuncio.objects.filter(id=anuncio.id).exists()
    assert anuncio.status_publicacao == Anuncio.StatusAnuncio.ATIVO

# Avalia o motor de busca (query text), garantindo que termos de pesquisa retornem resultados corretos e ignorem outros
@pytest.mark.unit
@pytest.mark.django_db
def test_get_anuncios_ativos_filtro_busca(usuario_ativo, categoria):
    anuncio1 = create_anuncio(usuario_ativo, "Bicicleta Caloi", categoria.id, 100.0, "Ótima bike")
    anuncio2 = create_anuncio(usuario_ativo, "Skate", categoria.id, 50.0, "Shape maple")
    
    resultados = get_anuncios_ativos(query="caloi")
    assert resultados.count() == 1
    assert resultados.first() == anuncio1

# Avalia o filtro por categorias do catálogo, comprovando que apenas produtos da categoria alvo são listados
@pytest.mark.unit
@pytest.mark.django_db
def test_get_anuncios_ativos_filtro_categoria(usuario_ativo, categoria, db):
    cat2 = Categoria.objects.create(nome_categoria="Outra", slug_busca="outra")
    anuncio1 = create_anuncio(usuario_ativo, "Anúncio A", categoria.id, 10.0, "A")
    anuncio2 = create_anuncio(usuario_ativo, "Anúncio B", cat2.id, 10.0, "B")
    
    resultados = get_anuncios_ativos(categoria_id=cat2.id)
    assert resultados.count() == 1
    assert resultados.first() == anuncio2

# Comprova a eficácia das expressões regulares (Regex) na limpeza de telefones sujos para links do WhatsApp
@pytest.mark.unit
def test_gerar_link_whatsapp():
    telefone = "(51) 98888-7777"
    titulo = "Bicicleta Caloi"
    link = gerar_link_whatsapp(telefone, titulo)
    
    assert link.startswith("https://wa.me/5551988887777")
    assert "text=Ol%C3%A1%21%20Vi%20seu%20an%C3%BAncio%20%27Bicicleta%20Caloi%27" in link

# Assegura que um usuário pode excluir seu próprio anúncio sem problemas
@pytest.mark.unit
@pytest.mark.django_db
def test_delete_anuncio_sucesso(usuario_ativo, anuncio):
    anuncio_id = anuncio.id
    delete_anuncio(anuncio_id, usuario_ativo)
    assert not Anuncio.objects.filter(id=anuncio_id).exists()

# Assegura a integridade do sistema levantando um Erro 404 caso alguém tente deletar o anúncio de terceiros
@pytest.mark.unit
@pytest.mark.django_db
def test_delete_anuncio_falha_usuario_errado(usuario_ativo, usuario_pendente, anuncio):
    with pytest.raises(Http404):
        # Usuário pendente tenta deletar o anúncio do usuário ativo, o que deve levantar 404 Not Found
        delete_anuncio(anuncio.id, usuario_pendente)
