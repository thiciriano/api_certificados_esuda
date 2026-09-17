# Esuda Certificados

> **Projeto acadêmico de backend** — desenvolvido como trabalho da disciplina (primeira entrega) para fins de estudo e avaliação. Não é um produto em produção.

API REST para gerenciar eventos acadêmicos, inscrições e emissão de certificados da instituição.

## O que já funciona

- CRUD de usuários, categorias e eventos;
- Inscrição em evento com todas as regras de negócio (vaga, duplicidade, data, status);
- Cancelamento de inscrição;
- Emissão de certificado com código único;
- Migration inicial com o Alembic;
- Documentação automática no Swagger.

O login com JWT e a autorização por perfil ficam para a segunda entrega.

## Tecnologias

Python 3.10+, FastAPI, SQLAlchemy, Alembic, Pydantic e SQLite no desenvolvimento (configurado para trocar por PostgreSQL pelo .env).

## Como rodar

Requisitos: Python 3.10+.

```bash
# 1. criar o ambiente virtual (no projeto já existe um em .venv)
python -m venv .venv

# 2. ativar
# linux/mac:
source .venv/bin/activate
# windows:
.venv\Scripts\activate

# 3. instalar as dependências
pip install -r requirements.txt

# 4. criar as tabelas (migration inicial)
alembic upgrade head

# 5. subir o servidor
uvicorn app.main:app --reload
```

Pronto. Abra http://localhost:8000/docs para ver o Swagger e testar as rotas.

## Estrutura de pastas

```
app/
├── api/v1/routers/   # rotas por entidade
├── core/             # configurações
├── database/         # conexão com o banco
├── models/           # tabelas (SQLAlchemy)
├── schemas/          # validação (Pydantic)
└── main.py           # app principal
```

## Documentação da entrega

Toda a documentação está na pasta `docs/`:

1. [Contexto do problema](docs/01-contexto-do-problema.md)
2. [Requisitos](docs/02-requisitos.md)
3. [Perfis de usuário](docs/03-perfis-de-usuario.md)
4. [Regras de negócio](docs/04-regras-de-negocio.md)
5. [Modelo de dados (DER)](docs/05-modelo-de-dados.md)
6. [Dicionário de dados](docs/06-dicionario-de-dados.md)
7. [Rotas, contratos e status codes](docs/07-rotas-e-contratos.md)
8. [Matriz de permissões](docs/08-matriz-de-permissoes.md)
9. [Arquitetura e stack](docs/09-arquitetura-e-stack.md)
10. [Backlog](docs/10-backlog.md)
11. [Critérios de aceitação](docs/11-criterios-de-aceitacao.md)

## Observações

- O banco de desenvolvimento é SQLite (arquivo `esuda.db`, ignorado pelo git). Para trocar, crie um `.env` na raiz com `DATABASE_URL=postgresql://usuario:senha@localhost/esuda` e ajuste o `sqlalchemy.url` no `alembic.ini`;
- Este repositório tem fins exclusivamente acadêmicos.
