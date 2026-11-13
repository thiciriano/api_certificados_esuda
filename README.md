# Esuda Certificados

API REST para gerenciamento de **eventos acadêmicos, inscrições e emissão de certificados** da Faculdade ESUDA, evoluída da 1AV para a 2AV com autenticação JWT, autorização por perfil, testes automatizados e deploy em produção.

- **Problema de negócio:** a instituição controlava eventos e certificados em planilhas e papel, com risco de erro, duplicidade e dificuldade de consulta.
- **Objetivo:** centralizar cadastro de usuários, categorias, eventos, inscrições e certificados numa API segura, documentada e disponível 24h.
- **Perfis:** Administrador (tudo), Organizador (gerencia os eventos que criou), Participante (inscreve-se e acompanha o próprio certificado). A matriz completa está em [`app/matriz_permissoes.md`](app/matriz_permissoes.md).

## Tecnologias

| Camada | Ferramenta |
| ------ | ---------- |
| API | Python 3.12 + FastAPI |
| Banco | SQLite (local) / PostgreSQL (produção via Render) com SQLAlchemy |
| Auth | JWT (python-jose) + hash de senha bcrypt |
| Config | pydantic-settings + variáveis de ambiente (`.env`) |
| Testes | pytest + TestClient (httpx) |
| Deploy | Render (blueprint `render.yaml`) |

## Estrutura de diretórios

```
Esuda/
├── app/
│   ├── api/v1/
│   │   ├── api.py                  # junta as rotas sob /api/v1
│   │   └── routers/                # auth, usuarios, eventos, inscricoes, certificados, categorias
│   ├── core/
│   │   ├── config.py               # Settings (variáveis de ambiente)
│   │   ├── security.py             # hash bcrypt + criar/decodificar JWT
│   │   ├── deps.py                 # get_current_user, precisa_de_permissao
│   │   ├── permissions.py          # matriz PERFIS (o que cada papel pode)
│   │   └── swagger_presets.py      # exemplos de payload pro Swagger
│   ├── database/database.py        # engine, SessionLocal, get_db
│   ├── models/models.py            # tabelas (SQLAlchemy)
│   ├── schemas/schemas.py          # validação de entrada/saída (Pydantic)
│   ├── main.py                     # sobe a API (create_all sem drop_all)
│   └── matriz_permissoes.md / regras_negocios.md / criteria_aceite.md
├── tests/                          # suíte pytest (conftest + 5 arquivos)
├── docs/relatorio_evolucao_2av.md  # relatório de evolução 1AV → 2AV
├── run.py                          # python run.py [porta]
├── seed.py                         # popula o banco com dados de teste
├── render.yaml                     # blueprint do Render (deploy)
├── .env.example                    # modelo das variáveis de ambiente
└── requirements.txt
```

## Entidades e relacionamentos

- **Usuario** 1—N **Inscrição**; **Usuario** 1—N **Certificado**
- **Evento** N—1 **Categoria**; **Evento** 1—N **Inscrição**
- **Inscrição** 1—1 **Certificado** (uma inscrição gera no máximo um)
- **Evento.criado_por** → Usuario (define o dono do evento p/ autorização)

## Como rodar locally

```bash
# 1. dependências (use venv)
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

# 2. variáveis de ambiente
cp .env.example .env
# edite o .env: gere a chave com python -c "import secrets; print(secrets.token_hex(32))"

# 3. banco (as tabelas são criadas sozinhas no boot, sem drop_all)
python -c "from app.main import app"   # ou simplesmente suba a API

# 4. sobe a API
python run.py            # http://localhost:8000  (docs em /docs)

# 5. (opcional) popula dados de teste — pede a senha do admin na hora
python seed.py
```

O banco local é o arquivo `esuda_certificados.db` (criado automaticamente, não versionado).

## Testes

```bash
pytest           # roda tudo (47 testes)
pytest tests/test_auth.py -v   # só um arquivo, verboso
```

O `tests/conftest.py` aponta o `DATABASE_URL` para um banco isolado em `/tmp/opencode/` — os testes **não** tocam no banco local nem no de produção.

## Endpoints principais (prefixo `/api/v1`)

| Método | Rota | Auth | Descrição |
| ------ | ---- | ---- | --------- |
| POST | `/auth/login` | – | Login (OAuth2 form: username = e-mail) → `{access_token, token_type}` |
| POST | `/usuarios` | – | Auto-cadastro (participante/organizador); admin cria qualquer papel |
| GET | `/usuarios/me` | Bearer | Usuário autenticado pelo token |
| GET/PUT/DELETE | `/usuarios/{id}` | Bearer | Gestão de usuários (admin; PUT próprio cadastro também) |
| GET | `/eventos` | – | Lista eventos (consulta aberta) |
| POST/PUT/DELETE | `/eventos` | Bearer | CRUD conforme matriz (exclusão só admin) |
| POST | `/inscricoes` | Bearer | Inscreve o **próprio** usuário (token define o dono) |
| GET/PUT/DELETE | `/inscricoes/{id}` | Bearer | Listagem e cancelamento conforme dono/vínculo |
| POST/GET/PUT/DELETE | `/certificados` | Bearer | Emissão e gestão conforme matriz |
| GET/POST/PUT/DELETE | `/categorias` | Bearer* | *GET aberto; escrita é organizador/admin |

Lista completa com códigos e exemplos: **[Swagger](https://esuda-certificados.onrender.com/docs)** (também local em `/docs`).

## Perfis e permissões

Três papéis (`app/core/permissions.py`): `admin`, `organizador`, `participante`. Regras de dono: participante só mexe nas próprias inscrições/certificados; organizador só mexe nos eventos que criou (`criado_por`) e no que está vinculado a eles; admin mexe em tudo. Quem não tem o perfil recebe `403`; sem token ou token expirado, `401`; recurso inexistente, `404`. Detalhe tabela a tabela em [`app/matriz_permissoes.md`](app/matriz_permissoes.md).

## Principais regras de negócio

R1–R10 documentadas na 1AV e revisadas + R11–R16 novas da 2AV (certificado terminal, categoria com vínculo, sem promoção a admin, etc.) — todas com endpoint e status em [`app/regras_negocios.md`](app/regras_negocios.md).

## Ambiente publicado

- **API:** https://esuda-certificados.onrender.com
- **Swagger:** https://esuda-certificados.onrender.com/docs
- **Banco:** Postgres persistente no Render (criado pelo `render.yaml`); `DATABASE_URL`, `JWT_SECRET_KEY` etc. são variáveis de ambiente do serviço — nenhum segredo versionado.
- O boot roda `create_all()` (sem `drop_all`), então os dados sobrevivem a redeploy/restart.

## Integrantes e responsabilidades

| Integrante | Responsabilidade |
| ---------- | ---------------- |
| Thiago Henrique | _(preencher)_ |
| Victor Oliveira | _(preencher)_ |
| _(outro integrante)_ | _(preencher)_ |

## Evolução 1AV → 2AV

O relatório completo (revisão do MVP, correções, refatorações e rastreabilidade) está em [`docs/relatorio_evolucao_2av.md`](docs/relatorio_evolucao_2av.md). Contexto original do problema em [`app/README.md`](app/README.md).
