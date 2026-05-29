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
    # Logica placeholder para criação via formulário html
    if request.method == 'POST':
        # Aqui virá a lógica do form futuramente
        pass
    categorias = Categoria.objects.all()
    return render(request, 'ads/ad_create.html', {'categorias': categorias})
