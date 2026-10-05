# Esuda Certificados

> **Projeto acadêmico de backend** — trabalho da disciplina de Desenvolvimento Back End (primeira entrega). Tem fins exclusivamente acadêmicos; não é um produto em produção.

API REST para gerenciamento de eventos acadêmicos, inscrições e emissão de certificados da instituição.

## Tecnologias

| Camada | Biblioteca |
|--------|-----------|
| Framework | FastAPI |
| Banco / ORM | SQLAlchemy 2.x + SQLite |
| Validação | Pydantic 2.x |
| Autenticação | python-jose (JWT) — prepared, ainda não ligada |
| Servidor | Uvicorn |

## Requisitos

- **Python 3.12**
- Nada além disso: o SQLite já vem com o Python e as tabelas são criadas sozinhas no start (não há migrations para rodar).

## Instalação

```bash
# 1. criar o ambiente virtual
python -m venv .venv

# 2. ativar
# linux/mac:
source .venv/bin/activate
# windows powershell:
.venv\Scripts\Activate.ps1

# 3. instalar as dependências
pip install -r requirements.txt
```

## Como rodar

```bash
# sobe na porta 8000 com reload automático
python run.py

# ou, em outra porta
python run.py 8080

# alternativa direta pelo uvicorn
uvicorn app.main:app --reload
```

O banco `esuda_certificados.db` é criado automaticamente na pasta do projeto na primeira execução.

### Documentação interativa

| URL | O que é |
|-----|---------|
| http://localhost:8000/docs | Swagger UI (clique em **Try it out** para testar) |
| http://localhost:8000/redoc | ReDoc |
| http://localhost:8000/openapi.json | Esquema OpenAPI |
| http://localhost:8000/health | Health check |

Os endpoints de `POST` e `PUT` já vêm com **exemplos prontos** (`openapi_examples`): no Swagger, use o dropdown *Examples* no canto do campo de payload para preencher o JSON com 1 clique.

## Endpoints

São **22 endpoints** — 5 entidades com CRUD completo, mais 2 rotas de raiz.

> ⚠️ **As rotas estão na raiz, sem o prefixo `/api/v1`.** Use `/usuarios`, e **não** `/api/v1/usuarios`. Veja [Problemas conhecidos](#problemas-conhecidos).

| Entidade | Endpoints |
|----------|-----------|
| Usuários | `POST /usuarios` · `GET /usuarios` · `PUT /usuarios/{id}` · `DELETE /usuarios/{id}` |
| Categorias | `POST /categorias` · `GET /categorias` · `PUT /categorias/{id}` · `DELETE /categorias/{id}` |
| Eventos | `POST /eventos` · `GET /eventos` · `PUT /eventos/{id}` · `DELETE /eventos/{id}` |
| Inscrições | `POST /inscricoes` · `GET /inscricoes` · `PUT /inscricoes/{id}` · `DELETE /inscricoes/{id}` |
| Certificados | `POST /certificados` · `GET /certificados` · `PUT /certificados/{id}` · `DELETE /certificados/{id}` |
| Raiz | `GET /` · `GET /health` |

`DELETE` responde **204** e não devolve corpo.

## Fluxo completo (a ordem importa)

As entidades têm chaves estrangeiras, então crie sempre nesta ordem:

```bash
B=http://localhost:8000

# 1. categoria (o evento exige uma categoria válida)
curl -X POST $B/categorias -H 'Content-Type: application/json' \
  -d '{"nome":"Workshop","descricao":"Eventos Praticos"}'

# 2. usuário
curl -X POST $B/usuarios -H 'Content-Type: application/json' \
  -d '{"nome":"Thiago","email":"thiago@esuda.edu.br","senha":"123","papel":"participante"}'

# 3. evento (categoria_id precisa existir)
curl -X POST $B/eventos -H 'Content-Type: application/json' \
  -d '{"titulo":"Apresentacao MVP","descricao":"Defesa de ADS","data_evento":"2026-11-10","local":"Auditorio","capacidade":30,"categoria_id":1}'

# 4. inscrição (consome uma vaga)
curl -X POST $B/inscricoes -H 'Content-Type: application/json' \
  -d '{"usuario_id":1,"evento_id":1}'

# 5. certificado
curl -X POST $B/certificados -H 'Content-Type: application/json' \
  -d '{"inscricao_id":1}'
```

Respostas de criação usam o envelope `{"success": true, "message": "...", "data": {...}}`. Erros usam `{"detail": "..."}`.

## Regras de negócio

Implementadas e verificadas na API:

| Regra | Onde | Comportamento |
|-------|------|---------------|
| E-mail único | `usuarios.py` | `400` se o e-mail já existir |
| Nome de categoria único | `categorias.py` | `400` se já existir |
| Título de evento único | `eventos.py` | `400` se já existir |
| Categoria precisa existir | `eventos.py` | `404` se `categoria_id` não existir |
| Inscrição duplicada | `inscricoes.py` | `400` se o usuário já estiver inscrito no evento |
| Sem vagas | `inscricoes.py` | `400` se não houver vaga |
| Cancelamento devolve vaga | `inscricoes.py` | `PUT` com `status: "cancelada"` devolve 1 vaga |
| Exclusão em cascata | `inscricoes.py` | Apagar inscrição apaga o certificado junto |
| Certificado único por inscrição | `certificados.py` | `400` se já foi emitido |
| Código de certificação | `certificados.py` | Gerado no formato `ESUDA-{id}-{inscricao_id}` |

Ainda **não** implementadas (previstas para a segunda entrega): autenticação JWT, controle de acesso por perfil, validação de data passada e validação de senha mínima.

## Estrutura do projeto

```
.
├── run.py                  # sobe o servidor
├── seed.py                 # script de dados de teste (ver limitações)
├── requirements.txt
├── esuda_certificados.db   # banco SQLite (gerado automaticamente)
└── app/
    ├── main.py             # app FastAPI; cria as tabelas no start
    ├── api/v1/
    │   ├── api.py          # registra as rotas de cada entidade
    │   └── routers/        # categorias, certificados, eventos,
    │                       # inscricoes, usuarios
    ├── core/
    │   ├── config.py       # settings via pydantic-settings / .env
    │   ├── security.py     # criação e leitura de token JWT
    │   ├── deps.py         # dependências de autenticação
    │   ├── permissions.py  # o que cada papel pode fazer
    │   └── swagger_presets.py
    ├── database/
    │   └── database.py     # engine, SessionLocal, Base, get_db
    ├── models/
    │   └── models.py       # tabelas SQLAlchemy
    ├── schemas/
    │   └── schemas.py      # schemas Pydantic
    ├── backlog.md
    ├── regras_negocios.md
    ├── matriz_permissoes.md
    └── criteria_aceite.md
```

## Scripts auxiliares

### `seed.py`

Popula o banco chamando a API por HTTP, para não digitar tudo no Swagger:

```bash
# em um terminal, com a API no ar:
python run.py

# em outro terminal:
python seed.py
```

⚠️ **O `seed.py` está quebrado na versão atual** — ele aponta para `/api/v1`, que não existe (veja abaixo), e não checa o status das respostas, então imprime `✅` mesmo quando nada é criado. Para popular o banco hoje, use o [fluxo em curl](#fluxo-completo-a-ordem-importa) acima ou os exemplos do Swagger.

Para zerar o banco e começar do zero:

```bash
rm esuda_certificados.db   # linux/mac
del esuda_certificados.db  # windows
python run.py              # recria as tabelas vazias
```

## Configuração

O `app/core/config.py` lê um arquivo `.env` opcional na raiz (não versionado):

```bash
PROJECT_NAME=Esuda Certificados
JWT_SECRET_KEY=troque-esta-chave
ACCESS_TOKEN_EXPIRE_MINUTES=1440
```

Mas atenção: **a URL do banco não vem do `.env`.** Ela está fixa em `app/database/database.py` (`sqlite:///./esuda_certificados.db`). As variáveis `POSTGRES_*` do `config.py` existem, mas ainda não são usadas — a troca para PostgreSQL fica para a segunda entrega.

## Problemas conhecidos

Encontrados ao testar a API localmente. Nenhum bloqueia a demonstração, mas os dois primeiros quebram o `seed.py`:

1. **Falta o prefixo `/api/v1`.** Em `app/api/v1/api.py` o router é criado sem prefixo (`APIRouter()`), então as rotas ficam em `/usuarios` em vez de `/api/v1/usuarios`. Correção sugerida:
   ```python
   api_router = APIRouter(prefix=settings.API_V1_STR)
   ```

2. **`seed.py` não valida as respostas.** Como aponta para `/api/v1`, todas as requisições retornam `404` — mas o script imprime `✅` mesmo assim, criando a ilusão de que o banco foi populado.

3. **`vagas_disponiveis` nunca é usada.** A coluna existe em `models.py`, mas a inscrição em `inscricoes.py` decrementa `capacidade`. Resultado: `capacidade` vai diminuindo (o valor original se perde) e `vagas_disponiveis` fica travada no valor inicial.

4. **Deprecation do Pydantic.** `config.py` usa `@validator` e `class Config` (estilo v1), o que gera avisos de depreciação no console e vai quebrar no Pydantic 3. Migrar para `@field_validator` e `SettingsConfigDict`.

5. **JWT pronto, mas sem rota de login.** `security.py`, `deps.py` e `permissions.py` existem e funcionam, porém nenhuma rota `/login` foi criada e os routers não exigem token — ou seja, **todas as rotas estão públicas**.

6. **Senhas em texto puro** no banco, sem hash, e o campo `papel` é texto livre (sem validação).

7. **`echo=True` no engine** (`app/database/database.py`): todo SQL é impresso no terminal. Comentar se poluir o console.


## Referência rápida

```bash
python -m venv .venv && source .venv/bin/activate   # preparar ambiente
pip install -r requirements.txt                     # instalar
python run.py                                       # subir em :8000
python run.py 8080                                  # subir em :8080
curl localhost:8000/health                          # testar
python seed.py                                      # popular (com API no ar)
```
