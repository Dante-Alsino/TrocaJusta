# Entendendo o ORM do Django no Troca Justa

Um dos pilares arquiteturais mais robustos do Django é o seu **ORM (Object-Relational Mapping)**. 
Em vez de escrevermos comandos complexos e engessados em SQL (como `SELECT * FROM anuncios WHERE id = 1`), o ORM nos permite manipular tabelas do banco de dados relacional (PostgreSQL) usando apenas classes e métodos puramente em Python.

Isso traz segurança contra falhas de injeção de SQL (*SQL Injection*), além de facilitar a manutenção: se amanhã trocarmos o PostgreSQL pelo MySQL, não precisamos reescrever sequer uma linha das queries, pois o ORM faz a tradução por baixo dos panos.

---

## Mapeamento: Como as Classes Viram Tabelas

Na pasta `core/models.py`, você notará as estruturas lógicas do projeto. Cada classe Python herdada de `models.Model` equivale a uma tabela no Banco de Dados. E cada propriedade dessa classe é uma coluna.

### 1. `CustomUser` (A Tabela de Contas)
```python
class CustomUser(AbstractUser):
    telefone_contato = models.CharField('Telefone de Contato', max_length=20)
    cidade = models.CharField(max_length=20, choices=CidadeOpcoes.choices)
```
- **Abstração Avançada:** Em vez de criarmos uma tabela de usuários do zero, o Troca Justa herda o `AbstractUser` nativo do Django, ganhando de brinde a criptografia pesada de senhas, controle de admin e sessões ativas. Nós apenas expandimos esse núcleo adicionando colunas customizadas como `telefone_contato` e uma limitação restrita em `cidade` (com *Choices*, que obriga o banco a aceitar apenas opções de um menu pré-definido).

### 2. `Anuncio` (A Tabela Central)
```python
class Anuncio(models.Model):
    perfil = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    categoria = models.ForeignKey(Categoria, on_delete=models.RESTRICT)
    preco_solicitado = models.DecimalField(max_digits=10, decimal_places=2)
```
**Como isso é traduzido no banco de dados (SQL bruto):**
```sql
CREATE TABLE "core_anuncio" (
    "id" integer NOT NULL PRIMARY KEY AUTOINCREMENT,
    "preco_solicitado" numeric(10, 2) NOT NULL,
    "categoria_id" integer NOT NULL REFERENCES "core_categoria" ("id"),
    "perfil_id" integer NOT NULL REFERENCES "core_customuser" ("id")
);
```
- **Relacionamentos Inteligentes (Foreign Key):** Aqui o ORM brilha. A propriedade `perfil` conecta o anúncio ao criador dele. O ORM sabe que, se usarmos o comportamento `on_delete=models.CASCADE`, ao apagarmos um usuário do sistema, o banco de dados apagará todos os seus anúncios automaticamente.
- Já para a propriedade `categoria`, adotamos `on_delete=models.RESTRICT`. Isso é uma proteção a nível de banco: impede que o administrador acidentalmente exclua uma Categoria que possua anúncios ativos, barrando a ação para não deixar "produtos orfãos".
- **Garantia Decimal:** O `DecimalField` é vital. Nunca usamos float para dinheiro na programação por conta de falhas de precisão binária; o ORM assegura 10 dígitos e arredondamento impecável de 2 casas decimais.

### 3. `ImagemAnuncio` e Relacionamentos Reversos (`related_name`)
```python
class ImagemAnuncio(models.Model):
    anuncio = models.ForeignKey(Anuncio, related_name='imagens', ...)
```
- Perceba o atributo `related_name='imagens'`. Sem escrever nenhuma query complexa de `JOIN`, o ORM nos entrega a possibilidade de puxar todas as imagens com uma sintaxe elegante em qualquer momento do código (por exemplo, na view ou template, escrevemos `anuncio.imagens.all()` e a mágica acontece).

---

## Consultas Avançadas (Querysets) no Código

O poder do ORM fica evidente dentro da nossa Camada de Serviços (`ads/services.py`). Veja como operamos a busca global dos produtos da plataforma:

### Motor de Busca Inteligente
```python
from django.db.models import Q

def get_anuncios_ativos(query=None):
    # Retorna APENAS anúncios cujo status de publicação seja ATIVO
    anuncios = Anuncio.objects.filter(status_publicacao='ativo').order_by('-data_postagem')
    
    if query:
        # Busca complexa com a letra Q
        anuncios = anuncios.filter(
            Q(titulo_produto__icontains=query) | Q(descricao_detalhada__icontains=query)
        )
    return anuncios
```

**Como a query complexa acima é traduzida no banco de dados (SQL bruto):**
```sql
SELECT * FROM "core_anuncio" 
WHERE "status_publicacao" = 'ativo' 
  AND (UPPER("titulo_produto"::text) LIKE UPPER('%query%') 
       OR UPPER("descricao_detalhada"::text) LIKE UPPER('%query%'))
ORDER BY "data_postagem" DESC;
```

**Destrinchando o código:**
1. **`.filter()`**: Aplica cláusulas condicionais equivalentes ao `WHERE` no SQL.
2. **`.order_by('-data_postagem')`**: O sinal de menos (`-`) faz a ordenação inversa (Descending), trazendo sempre os anúncios mais frescos e recém-criados no topo da lista.
3. **O uso do `Q` (Buscas "Ou"):** O ORM usa o pipe `|` e a classe `Q` para criar uma condição alternativa de segurança e flexibilidade (Equivale a: *"Me dê os anúncios onde a palavra-chave procurada exista no Título OU exista na Descrição"*).
4. **O Sufixo `__icontains`**: É um modificador espetacular do Django. O sufixo `contains` pesquisa ocorrências dentro do texto (`LIKE %query%` no SQL). O `i` antes significa "Insensitive". Ou seja, o ORM manda o banco de dados ignorar letras maiúsculas e minúsculas ao procurar pela palavra.
