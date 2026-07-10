# 🛒 Troca Justa Charqueadas


## 🚀 Como Rodar o Projeto

Certifique-se de que o **Docker Desktop** esteja aberto e em execução.

### 1. Subir os Containers
Abra o terminal na pasta raiz do projeto (`c:\Users\dante\Desktop\Tcc`) e execute:
```bash
docker compose up
```
*(Use `docker compose up --build` apenas na primeira vez ou caso adicione novas dependências no `requirements.txt`).*

> 💡 **Dica:** Para subir em segundo plano e **liberar o terminal atual** sem precisar abrir outra janela para rodar os comandos seguintes, use:
> ```bash
> docker compose up -d
> ```

### 2. Criar as Tabelas no Banco de Dados (Migrações)
Com os containers rodando, abra uma **nova janela de terminal** na raiz do projeto e execute:
```bash
docker compose exec web python manage.py migrate
```

### 3. Criar a Conta de Administrador (Superuser)
Para ter acesso ao painel administrativo do Django, crie seu superusuário rodando:
```bash
docker compose exec web python manage.py createsuperuser
```
> **Nota:** Como o projeto usa o e-mail como autenticação principal, o prompt do terminal solicitará nesta ordem: **E-mail**, **Username**, **Nome completo**, **Telefone** e **Senha**.

### 4. Links de Acesso
Após seguir os passos acima, acesse o projeto através dos links abaixo:
* 💻 **Interface do Sistema:** [http://localhost:8000](http://localhost:8000)
* ⚙️ **Painel do Administrador:** [http://localhost:8000/admin](http://localhost:8000/admin)

### 5. Executando os Testes Automatizados (Pytest)
A plataforma possui uma suíte de testes com separação arquitetural (Unitários vs Funcionais). Garanta que os containers estão rodando e execute os comandos abaixo em uma nova aba do terminal:

**Testes Unitários (Apenas lógica e regras de negócio):**
```bash
docker compose exec web pytest -m unit -v
```

**Testes Funcionais (Simulação de fluxos de navegação e telas):**
```bash
docker compose exec web pytest -m functional -v
```

**Rodar todos os testes (Suíte Completa):**
```bash
docker compose exec web pytest -v
```
*(Nota: Se houver problemas de módulos ausentes, rode `docker compose up --build -d` para garantir que o pytest foi instalado dentro do container).*

---

## 🛠️ Comandos Úteis (Docker)

* **Parar os containers:**  
  ```bash
  docker compose down
  ```
* **Zerar o banco de dados e recomeçar do zero:**  
  *(Atenção: isso apagará todos os dados cadastrados no banco)*
  ```bash
  docker compose down -v
  ```
* **Criar novas migrações** *(rode sempre que alterar algo em `models.py`)*:  
  ```bash
  docker compose exec web python manage.py makemigrations
  ```
* **Aplicar migrações novas** *(rode após criar novas migrações)*:  
  ```bash
  docker compose exec web python manage.py migrate
  ```

---
