from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.html import format_html
from django.urls import reverse, path
from django.shortcuts import redirect
from .models import CustomUser, Categoria, Anuncio, ImagemAnuncio, Denuncia

@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    list_display = ('email', 'nome_completo', 'telefone_contato', 'cidade', 'status_conta', 'is_staff')
    list_filter = ('status_conta', 'cidade', 'is_staff', 'is_superuser', 'is_active')
    search_fields = ('email', 'nome_completo', 'telefone_contato', 'endereco_completo')
    ordering = ('email',)
    
    fieldsets = UserAdmin.fieldsets + (
        ('Informações Adicionais e Localidade', {'fields': ('nome_completo', 'telefone_contato', 'cidade', 'endereco_completo', 'status_conta')}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Informações Adicionais e Localidade', {'fields': ('nome_completo', 'telefone_contato', 'cidade', 'endereco_completo', 'status_conta')}),
    )

@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ('nome_categoria', 'slug_busca')
    prepopulated_fields = {'slug_busca': ('nome_categoria',)}

class ImagemAnuncioInline(admin.TabularInline):
    model = ImagemAnuncio
    extra = 1

@admin.register(Anuncio)
class AnuncioAdmin(admin.ModelAdmin):
    list_display = ('titulo_produto', 'perfil', 'preco_solicitado', 'categoria', 'status_publicacao', 'data_postagem')
    list_filter = ('status_publicacao', 'categoria', 'data_postagem')
    search_fields = ('titulo_produto', 'descricao_detalhada', 'perfil__email')
    inlines = [ImagemAnuncioInline]

@admin.register(Denuncia)
class DenunciaAdmin(admin.ModelAdmin):
    list_display = ('anuncio', 'ver_anuncio_link', 'vendedor_denunciado', 'perfil_autor', 'motivo_categoria', 'data_registro', 'acao_suspender')
    list_filter = ('motivo_categoria', 'data_registro')
    search_fields = ('anuncio__titulo_produto', 'perfil_autor__email', 'anuncio__perfil__email')
    readonly_fields = ('data_registro', 'acao_suspender', 'ver_anuncio_link', 'vendedor_denunciado')

    fieldsets = (
        ('Informações da Denúncia', {
            'fields': ('anuncio', 'ver_anuncio_link', 'vendedor_denunciado', 'perfil_autor', 'motivo_categoria', 'detalhes_denuncia', 'data_registro')
        }),
        ('Ações de Moderação', {
            'fields': ('acao_suspender',)
        }),
    )

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('<int:denuncia_id>/suspender/', self.admin_site.admin_view(self.suspender_anuncio), name='suspender-anuncio'),
        ]
        return custom_urls + urls

    def acao_suspender(self, obj):
        if obj.anuncio.status_publicacao == 'bloqueado_fraude':
            return format_html('<span style="color: gray; font-weight: bold;">Bloqueado</span>')
        url = reverse('admin:suspender-anuncio', args=[obj.pk])
        return format_html('<a class="button" style="background-color: #b91c1c; color: white; padding: 4px 8px; border-radius: 4px; text-decoration: none;" href="{}">Bloquear Anúncio</a>', url)
    acao_suspender.short_description = 'Moderação'

    def suspender_anuncio(self, request, denuncia_id):
        from django.contrib import messages
        denuncia = self.get_object(request, denuncia_id)
        if denuncia:
            anuncio = denuncia.anuncio
            if anuncio.status_publicacao != 'bloqueado_fraude':
                anuncio.status_publicacao = 'bloqueado_fraude'
                anuncio.save()
                self.message_user(request, f'O anúncio "{anuncio.titulo_produto}" foi bloqueado com sucesso.', level=messages.SUCCESS)
            else:
                self.message_user(request, 'O anúncio já estava bloqueado.', level=messages.WARNING)
        return redirect('admin:core_denuncia_changelist')

    def vendedor_denunciado(self, obj):
        return obj.anuncio.perfil.email
    vendedor_denunciado.short_description = 'Denunciado'

    def ver_anuncio_link(self, obj):
        url = reverse('ads:detail', args=[obj.anuncio.pk])
        return format_html('<a href="{}" target="_blank">Ver Anúncio</a>', url)
    ver_anuncio_link.short_description = 'Link'
