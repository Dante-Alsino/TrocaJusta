# Testes Automatizados no Troca Justa

## 1. Testes Unitários (Camada de Serviços)
Os testes unitários têm o objetivo de isolar e validar a regra de negócio "crua", sem se preocupar com a tela ou interface.

Esses testes operam estritamente sobre os arquivos `services.py`. 
Como o sistema utiliza a arquitetura baseada em serviços, os testes focam em garantir que as funções essenciais operem sem falhas:

### Funcionalidades Avaliadas:
- **Barreiras de Segurança (Exceções Customizadas):** O sistema impede usuários não verificados de criar anúncios (`AccountNotVerifiedError`) e impede denúncias duplicadas via *flood* (`DuplicateReportError`).

- **Motor de Busca (Queries Isoladas):** O sistema utiliza dados falsos (`Fixtures`) no banco de testes provisório e verifica se o motor de busca consegue ocultar itens irrelevantes baseando-se em palavras-chave (`query`) e em filtragens exclusivas de Categorias.
- **Lógicas Utilitárias:** Validação do núcleo responsável por "limpar" telefones (Regex) para o formato exigido pela API do WhatsApp, convertendo strings sujas em URLs codificadas e prontas para uso.

---

## 2. Testes Funcionais (Camada de Views / Navegação)
Enquanto os testes unitários avaliam o "motor" da aplicação, os Testes Funcionais avaliam o "carro andando". Se usa o utilitário `Client` do Django para simular requisições de um navegador comum.

### Funcionalidades Avaliadas:
- **Disponibilidade (Endpoints HTTP):** O `Client` realiza requisições `GET` em telas vitais (como o Catálogo e o painel "Meus Anúncios") validando se o servidor as processa sem estourar Erros 500. Espera-se códigos HTTP `200 OK`.

- **Proteção de Rotas:** O ambiente simula acessos como usuário anônimo (deslogado) nas páginas restritas (como Perfil e "Meus Anúncios"). O teste assegura que as rotas estão devidamente fechadas com redirecionamentos (HTTP `302 Found` para a tela de Login).

- **Simulação de Fluxo de Exclusão:** Um teste complexo onde o Client "finge" estar logado, realiza um método POST com dados fictícios para deletar uma postagem e checa se o redirecionamento foi concluído e se o item sumiu do Banco de Dados.

---

## Como Executar a Suíte de Testes

O ambiente Django roda dentro de um container Docker isolado. Sendo assim, o Pytest precisa ser executado dentro daquele container, que é onde estão instaladas as bibliotecas do projeto e onde ocorre a comunicação com o PostgreSQL.

**Passo a passo:**
1. Certifique-se de que os containers do projeto estão de pé:
   ```bash
   docker-compose up -d
   ```
2. Para rodar a malha de testes padrão e obter uma visualização rápida do progresso (pontinhos verdes):
   ```bash
   docker-compose exec web pytest
   ```
3. (Opcional) Para rodar o teste com log aprofundado (listando minuciosamente o nome de cada teste aprovado):
   ```bash
   docker-compose exec web pytest -v
   ```

A execução irá ignorar o banco de dados principal de produção, criar um banco de testes temporário "vazio", popular dados com os Fixtures, executar os 15 cenários de stress, aprovar e destruir o banco em aproximadamente 3 a 5 segundos.
