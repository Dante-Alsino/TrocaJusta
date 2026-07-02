import pytest
from core.models import Anuncio, CustomUser, Categoria, Denuncia
from ads.services import (
    create_anuncio, registrar_denuncia, AccountNotVerifiedError, DuplicateReportError
)

@pytest.fixture
def categoria(db):
    return Categoria.objects.create(nome_categoria="Teste", icone_svg="<svg></svg>")

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

@pytest.mark.django_db
def test_create_anuncio_usuario_inativo(usuario_pendente, categoria):
    with pytest.raises(AccountNotVerifiedError):
        create_anuncio(usuario_pendente, "Teste", categoria.id, 10.0, "Teste")

@pytest.mark.django_db
def test_registrar_denuncia_duplicada(usuario_ativo, anuncio):
    # Primeira denúncia
    registrar_denuncia(anuncio, usuario_ativo, "fraude", "Teste")
    # Segunda denúncia deve falhar
    with pytest.raises(DuplicateReportError):
        registrar_denuncia(anuncio, usuario_ativo, "fraude", "Teste 2")

@pytest.mark.django_db
def test_create_anuncio_sucesso(usuario_ativo, categoria):
    anuncio = create_anuncio(usuario_ativo, "Anúncio Sucesso", categoria.id, 50.0, "Desc")
    assert Anuncio.objects.filter(id=anuncio.id).exists()
    assert anuncio.status_publicacao == Anuncio.StatusAnuncio.ATIVO
