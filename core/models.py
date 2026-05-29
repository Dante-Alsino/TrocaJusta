from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator

class CustomUser(AbstractUser):
    class StatusConta(models.TextChoices):
        ATIVO = 'ativo', 'Ativo'
        SUSPENSO = 'suspenso', 'Suspenso'
        PENDENTE = 'pendente_verificacao', 'Pendente de Verificação'

    email = models.EmailField('Endereço de Email', unique=True)
    telefone_contato = models.CharField('Telefone de Contato', max_length=20)
    status_conta = models.CharField(
        'Status da Conta',
        max_length=20,
        choices=StatusConta.choices,
        default=StatusConta.PENDENTE
    )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'nome_completo', 'telefone_contato']
    
    # Campo extra para o nome real se não quiser usar o first_name e last_name nativos
    nome_completo = models.CharField('Nome Completo', max_length=100)

    def __str__(self):
        return self.email


class Categoria(models.Model):
    nome_categoria = models.CharField('Nome da Categoria', max_length=50, unique=True)
    slug_busca = models.SlugField('Slug de Busca', max_length=60, unique=True)

    class Meta:
        verbose_name = 'Categoria'
        verbose_name_plural = 'Categorias'

    def __str__(self):
        return self.nome_categoria


class Anuncio(models.Model):
    class StatusAnuncio(models.TextChoices):
        ATIVO = 'ativo', 'Ativo'
        PAUSADO = 'pausado', 'Pausado'
        VENDIDO = 'vendido', 'Vendido'
        BLOQUEADO = 'bloqueado_fraude', 'Bloqueado por Fraude'

    perfil = models.ForeignKey(
        CustomUser, 
        on_delete=models.CASCADE, 
        related_name='anuncios',
        verbose_name='Anunciante'
    )
    categoria = models.ForeignKey(
        Categoria, 
        on_delete=models.RESTRICT, 
        related_name='anuncios',
        verbose_name='Categoria'
    )
    titulo_produto = models.CharField('Título do Produto', max_length=100)
    descricao_detalhada = models.TextField('Descrição Detalhada')
    preco_solicitado = models.DecimalField(
        'Preço Solicitado', 
        max_digits=10, 
        decimal_places=2,
        validators=[MinValueValidator(0.00)]
    )
    status_publicacao = models.CharField(
        'Status da Publicação',
        max_length=20,
        choices=StatusAnuncio.choices,
        default=StatusAnuncio.ATIVO
    )
    data_postagem = models.DateTimeField('Data de Postagem', auto_now_add=True)

    class Meta:
        db_table = 'anuncios'
        verbose_name = 'Anúncio'
        verbose_name_plural = 'Anúncios'

    def __str__(self):
        return f"{self.titulo_produto} - {self.preco_solicitado}"


class ImagemAnuncio(models.Model):
    anuncio = models.ForeignKey(
        Anuncio, 
        on_delete=models.CASCADE, 
        related_name='imagens',
        verbose_name='Anúncio'
    )
    imagem = models.ImageField(upload_to='anuncios/imagens/', verbose_name='Imagem do Produto')
    data_upload = models.DateTimeField('Data de Upload', auto_now_add=True)

    class Meta:
        verbose_name = 'Imagem do Anúncio'
        verbose_name_plural = 'Imagens dos Anúncios'

    def __str__(self):
        return f"Imagem de {self.anuncio.titulo_produto}"


class Denuncia(models.Model):
    anuncio = models.ForeignKey(
        Anuncio, 
        on_delete=models.CASCADE, 
        related_name='denuncias',
        verbose_name='Anúncio Denunciado'
    )
    perfil_autor = models.ForeignKey(
        CustomUser, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='denuncias_feitas',
        verbose_name='Denunciante'
    )
    motivo_categoria = models.CharField('Motivo/Categoria', max_length=50)
    detalhes_denuncia = models.TextField('Detalhes da Denúncia')
    data_registro = models.DateTimeField('Data do Registro', auto_now_add=True)

    class Meta:
        verbose_name = 'Denúncia'
        verbose_name_plural = 'Denúncias'

    def __str__(self):
        return f"Denúncia do anúncio {self.anuncio.titulo_produto}"
