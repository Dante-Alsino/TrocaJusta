from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, Categoria, Anuncio, ImagemAnuncio, Denuncia

@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    list_display = ('email', 'nome_completo', 'telefone_contato', 'status_conta', 'is_staff')
    list_filter = ('status_conta', 'is_staff', 'is_superuser', 'is_active')
    search_fields = ('email', 'nome_completo', 'telefone_contato')
    ordering = ('email',)
    
    fieldsets = UserAdmin.fieldsets + (
        ('Informações Adicionais', {'fields': ('nome_completo', 'telefone_contato', 'status_conta')}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Informações Adicionais', {'fields': ('nome_completo', 'telefone_contato', 'status_conta')}),
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
    list_display = ('anuncio', 'perfil_autor', 'motivo_categoria', 'data_registro')
    list_filter = ('motivo_categoria', 'data_registro')
    search_fields = ('anuncio__titulo_produto', 'perfil_autor__email')
