from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from core.models import Anuncio, Categoria

def ad_list(request):
    # Lista todos os anúncios ativos
    anuncios = Anuncio.objects.filter(status_publicacao=Anuncio.StatusAnuncio.ATIVO).order_by('-data_postagem')
    return render(request, 'ads/ad_list.html', {'anuncios': anuncios})

def ad_detail(request, pk):
    # Detalha um anúncio específico
    anuncio = get_object_or_404(Anuncio, pk=pk)
    return render(request, 'ads/ad_detail.html', {'anuncio': anuncio})

@login_required
def ad_create(request):
    if request.user.status_conta != 'ativo':
        from django.contrib import messages
        messages.warning(request, 'Sua conta precisa ser verificada pelo Administrador para que você possa publicar anúncios.')
        return redirect('ads:my_ads')
        
    if request.method == 'POST':
        titulo = request.POST.get('titulo_produto')
        categoria_id = request.POST.get('categoria')
        preco = request.POST.get('preco_solicitado')
        descricao = request.POST.get('descricao_detalhada')
        imagem = request.FILES.get('imagem')
        
        from core.models import ImagemAnuncio
        
        # Salva o Anúncio vinculando ao usuário logado
        anuncio = Anuncio.objects.create(
            perfil=request.user,
            categoria_id=categoria_id,
            titulo_produto=titulo,
            descricao_detalhada=descricao,
            preco_solicitado=preco,
            status_publicacao=Anuncio.StatusAnuncio.ATIVO
        )
        
        # Salva a imagem, se foi enviada
        if imagem:
            ImagemAnuncio.objects.create(anuncio=anuncio, imagem=imagem)
            
        return redirect('ads:list')
        
    categorias = Categoria.objects.all()
    return render(request, 'ads/ad_create.html', {'categorias': categorias})

@login_required
def my_ads(request):
    # Lista os anúncios criados pelo usuário logado
    anuncios = Anuncio.objects.filter(perfil=request.user).order_by('-data_postagem')
    return render(request, 'ads/my_ads.html', {'anuncios': anuncios})

@login_required
def ad_delete(request, pk):
    # Permite a exclusão de um anúncio apenas pelo dono
    anuncio = get_object_or_404(Anuncio, pk=pk, perfil=request.user)
    if request.method == 'POST':
        anuncio.delete()
    return redirect('ads:my_ads')
