from django.shortcuts import get_object_or_404
from core.models import Anuncio, ImagemAnuncio, Denuncia

class AccountNotVerifiedError(Exception):
    """Exceção levantada quando um usuário não verificado tenta criar um anúncio."""
    pass

class DuplicateReportError(Exception):
    """Exceção levantada quando um usuário tenta denunciar um anúncio mais de uma vez."""
    pass

def get_anuncios_ativos():
    """Retorna o queryset de anúncios ativos para exibição no catálogo público."""
    return Anuncio.objects.filter(status_publicacao=Anuncio.StatusAnuncio.ATIVO).order_by('-data_postagem')

def get_anuncios_do_usuario(usuario):
    """Retorna os anúncios pertencentes a um usuário logado específico."""
    return Anuncio.objects.filter(perfil=usuario).order_by('-data_postagem')

def get_anuncio_por_id(anuncio_id):
    """Busca e retorna um anúncio específico pelo ID, levantando 404 se não existir."""
    return get_object_or_404(Anuncio, pk=anuncio_id)

def create_anuncio(usuario, titulo, categoria_id, preco, descricao, imagem=None):
    """
    Regra de Negócio: Cria um novo anúncio no banco de dados.
    Valida obrigatoriamente o status da conta do usuário antes de permitir a postagem.
    """
    if usuario.status_conta != 'ativo':
        raise AccountNotVerifiedError("Sua conta precisa ser verificada pelo Administrador para que você possa publicar anúncios.")
    
    anuncio = Anuncio.objects.create(
        perfil=usuario,
        categoria_id=categoria_id,
        titulo_produto=titulo,
        descricao_detalhada=descricao,
        preco_solicitado=preco,
        status_publicacao=Anuncio.StatusAnuncio.ATIVO
    )
    
    if imagem:
        ImagemAnuncio.objects.create(anuncio=anuncio, imagem=imagem)
        
    return anuncio

def delete_anuncio(anuncio_id, usuario):
    """
    Regra de Negócio: Deleta um anúncio permanentemente.
    Garante segurança ao exigir que o anúncio pertença estritamente ao usuário solicitante.
    """
    anuncio = get_object_or_404(Anuncio, pk=anuncio_id, perfil=usuario)
    anuncio.delete()

def verificar_denuncia_existente(anuncio, usuario):
    """Retorna True se o usuário já possuir uma denúncia registrada para aquele anúncio."""
    if not usuario.is_authenticated:
        return False
    return Denuncia.objects.filter(anuncio=anuncio, perfil_autor=usuario).exists()

def registrar_denuncia(anuncio, usuario, motivo, detalhes):
    """
    Regra de Negócio: Efetua o registro da denúncia.
    Valida a barreira anti-spam para impedir duplicidade de denúncias.
    """
    if verificar_denuncia_existente(anuncio, usuario):
        raise DuplicateReportError("Você já denunciou este anúncio anteriormente.")
        
    denuncia = Denuncia.objects.create(
        anuncio=anuncio,
        perfil_autor=usuario,
        motivo_categoria=motivo,
        detalhes_denuncia=detalhes
    )
    return denuncia
