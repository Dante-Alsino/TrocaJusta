from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from core.models import Categoria
from . import services

def ad_list(request):
    """View Magra: Roteia o request para buscar todos os anúncios ativos, aplicando filtros de busca."""
    query = request.GET.get('q')
    categoria_id = request.GET.get('categoria')
    
    anuncios = services.get_anuncios_ativos(query=query, categoria_id=categoria_id)
    categorias = Categoria.objects.all()
    
    return render(request, 'ads/ad_list.html', {
        'anuncios': anuncios,
        'categorias': categorias,
        'query': query,
        'categoria_id': categoria_id
    })

def ad_detail(request, pk):
    """View Magra: Busca o detalhe, status de denúncia e gera o link do WhatsApp."""
    anuncio = services.get_anuncio_por_id(pk)
    ja_denunciou = services.verificar_denuncia_existente(anuncio, request.user)
    
    whatsapp_link = ""
    if anuncio.perfil.telefone_contato:
        whatsapp_link = services.gerar_link_whatsapp(anuncio.perfil.telefone_contato, anuncio.titulo_produto)
        
    return render(request, 'ads/ad_detail.html', {
        'anuncio': anuncio, 
        'ja_denunciou': ja_denunciou,
        'whatsapp_link': whatsapp_link
    })

@login_required
def ad_create(request):
    """View Magra: Coleta dados do formulário e tenta salvar através da Camada de Serviços."""
    if request.method == 'POST':
        titulo = request.POST.get('titulo_produto')
        categoria_id = request.POST.get('categoria')
        preco = request.POST.get('preco_solicitado')
        descricao = request.POST.get('descricao_detalhada')
        imagem = request.FILES.get('imagem')
        
        try:
            services.create_anuncio(
                usuario=request.user, 
                titulo=titulo, 
                categoria_id=categoria_id, 
                preco=preco, 
                descricao=descricao, 
                imagem=imagem
            )
            return redirect('ads:list')
        except services.AccountNotVerifiedError as e:
            messages.warning(request, str(e))
            return redirect('ads:my_ads')
        
    categorias = Categoria.objects.all()
    return render(request, 'ads/ad_create.html', {'categorias': categorias})

@login_required
def my_ads(request):
    """View Magra: Busca anúncios restritos ao dono logado."""
    anuncios = services.get_anuncios_do_usuario(request.user)
    return render(request, 'ads/my_ads.html', {'anuncios': anuncios})

@login_required
def ad_delete(request, pk):
    """View Magra: Delega o comando POST de exclusão para o serviço."""
    if request.method == 'POST':
        services.delete_anuncio(pk, request.user)
    return redirect('ads:my_ads')

@login_required
def ad_report(request, pk):
    """View Magra: Tenta registrar a denúncia via serviço e reage em caso de exceção (Spam)."""
    anuncio = services.get_anuncio_por_id(pk)
    
    if request.method == 'POST':
        motivo = request.POST.get('motivo_categoria')
        detalhes = request.POST.get('detalhes_denuncia')
        
        try:
            services.registrar_denuncia(
                anuncio=anuncio, 
                usuario=request.user, 
                motivo=motivo, 
                detalhes=detalhes
            )
            messages.success(request, 'Sua denúncia foi registrada e será analisada com prioridade pela nossa equipe.')
        except services.DuplicateReportError as e:
            messages.info(request, str(e))
            
    return redirect('ads:detail', pk=pk)
