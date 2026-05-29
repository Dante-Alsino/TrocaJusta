import os
import django
from django.utils.text import slugify

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'trocajusta.settings')
django.setup()

from core.models import Categoria

categorias = [
    'Eletrônicos e Celulares', 
    'Veículos e Peças', 
    'Imóveis', 
    'Serviços e Vagas', 
    'Casa e Móveis', 
    'Moda e Beleza', 
    'Esportes e Lazer', 
    'Outros'
]

for nome in categorias:
    Categoria.objects.get_or_create(
        nome_categoria=nome, 
        defaults={'slug_busca': slugify(nome)}
    )

print("Categorias criadas com sucesso!")
