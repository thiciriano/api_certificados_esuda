# Relatório — Terceira Entrega (consolidação, testes e deploy)

## 1. Continuidade e requisitos atendidos

A terceira entrega preserva integralmente a 1ª e a 2ª entregas: CRUDs, persistência, regras R1–R16, autenticação JWT, bcrypt, papéis (`admin`, `organizador`, `participante`), matriz de permissões e acesso por dono/vínculo. O trabalho desta etapa foi consolidar qualidade, ampliar a suíte e fechar as configurações de publicação.

| Requisito da 3ª entrega | Situação |
| ----------------------- | -------- |
| Funcionalidades anteriores mantidas | Sim — 52 testes passando, incluindo os 47 da 2ª entrega |
| Pelo menos 15 testes (positivos e negativos) | Sim — 52 testes em 6 arquivos |
| Regras de negócio da 1ª unidade validadas | Sim — R1–R16 em `tests/test_regras_negocio.py` e rastreabilidade no relatório da 2AV |
| Pelo menos 3 melhorias/refatorações | Sim — seção 2 (commits `d827059`, `68a1058`, `d86bcce`) |
| Organização com responsabilidades separadas | Sim — nova camada `app/services/` para escopo e validações |
| Erros e status codes padronizados | Sim — handlers centrais + envelope `RespostaErro` |
| Swagger/OpenAPI atualizado | Sim — esquemas de erro em todas as rotas v1, ver evidência abaixo |
| README técnico | Sim — instalação, execução, estrutura, endpoints, testes e evidências |
| Histórico no GitHub | Sim — commits descritivos, PR #1 e tags `v1.0.0` / `v1.1.0` |
| Configurações de deploy | Sim — `render.yaml`, `.env.example`, Postgres persistente, `create_all()` sem `drop_all()` |

## 2. Três melhorias realizadas (demonstração)

### Melhoria 1 — Tratamento centralizado de erros e status codes

**Antes:** cada rota lançava `HTTPException` com textos e formatos próprios; erros de validação e erros 500 seguiam apenas o default do FastAPI, sem um contrato único de resposta.

**Depois:** `app/core/errors.py` registra handlers para `HTTPException` (incluindo 404 de rota inexistente), `RequestValidationError` e exceções não tratadas, devolvendo sempre:

```json
{ "success": false, "error": "forbidden", "message": "Sem permissão para esta operação", "detail": "..." }
```

`app/api/v1/api.py` aplica `RESPOSTAS_ERRO` a todas as rotas v1 e `RespostaErro` ganhou o campo `detail`, mantendo compatibilidade com os clientes que já liam esse campo. O campo `WWW-Authenticate` dos erros 401 é preservado.

```bash
$ git show --stat d827059
 app/api/v1/api.py      |  3 +-
 app/core/errors.py     | 84 ++++++++++++++++++++++++++++++++++++++++++++++++++
 app/main.py            |  4 ++++
 app/schemas/schemas.py |  3 ++
 4 files changed, 93 insertions(+), 1 deletion(-)
```

Evidências: `tests/test_erros.py` (401, 403, 422, 404 e contrato OpenAPI) e [`evidencias/swagger-3av.txt`](evidencias/swagger-3av.txt).

### Melhoria 2 — Serviço de escopo dos recursos

**Antes:** `inscricoes.py` e `certificados.py` repetiam queries para descobrir eventos criados pelo organizador, inscrições vinculadas e certificados visíveis; a regra de "alterar só o que é seu" estava espalhada em `if`s dentro das rotas.

**Depois:** `app/services/escopo.py` concentra `ids_eventos_criados`, `ids_inscricoes_em_eventos`, `evento_e_do_usuario`, `inscricoes_visiveis`, `certificados_visiveis` e `pode_alterar_inscricao`. Os routers apenas chamam o serviço, mantendo as mensagens 403 anteriores.

```bash
$ git show --stat 68a1058
 app/api/v1/routers/certificados.py | 28 ++---------------
 app/api/v1/routers/inscricoes.py   | 35 +++++----------------
 app/services/__init__.py           |  1 +
 app/services/escopo.py             | 63 ++++++++++++++++++++++++++++++++++++++
 4 files changed, 75 insertions(+), 52 deletions(-)
```

Evidência: testes de autorização (`test_organizador_nao_consegue_cancelar_inscricao_de_outro_evento`, `test_participante_so_ve_as_proprias_inscricoes`) continuam passando após a extração.

### Melhoria 3 — Validações de unicidade em um único serviço

**Antes:** a checagem de e-mail, título de evento e nome de categoria era copiada em seis pontos (criação e atualização de três entidades).

**Depois:** `app/services/validacoes.py` expõe `email_ja_cadastrado`, `titulo_evento_ja_usado` e `categoria_ja_existe`, todos com parâmetro opcional `id` para ignorar o próprio registro no `PUT`. Status, mensagens e regras R1/R2/R7 permaneceram idênticos.

```bash
$ git show --stat d86bcce
 app/api/v1/routers/categorias.py | 13 ++++---------
 app/api/v1/routers/eventos.py    | 14 ++++----------
 app/api/v1/routers/usuarios.py   | 13 ++++---------
 app/services/validacoes.py       | 33 +++++++++++++++++++++++++++++++++
 4 files changed, 45 insertions(+), 28 deletions(-)
```

Evidência: `test_r1_email_duplicado_e_bloqueado`, `test_r2_titulo_de_evento_duplicado_e_bloqueado`, `test_crud_de_categoria` e `test_crud_completo_de_usuario`.

## 3. Status codes e envelopes

| Situação | Status | Corpo |
| -------- | ------ | ----- |
| Sem token / token inválido ou expirado | `401` | envelope com `error: unauthorized` e header `WWW-Authenticate` |
| Autenticado sem permissão ou acessando recurso alheio | `403` | envelope com `error: forbidden` |
| Regra de negócio violada (duplicidade, sem vaga, etc.) | `400` | envelope com `error: bad_request` |
| Recurso inexistente | `404` | envelope com `error: not_found` |
| Payload inválido | `422` | envelope com `error: validation_error` e `detail` em lista |
| Erro não previsto | `500` | envelope com `error: internal_error` (detalhe registrado no log) |
| Sucesso | `200/201/204` | envelope `{success, message, data}` quando há corpo |

O campo `detail` continua presente em todos os erros para não quebrar clientes já existentes.

## 4. Testes automatizados

```bash
pytest -v
# 52 passed, 1 warning in 59.01s
```

| Arquivo | Testes | Foco |
| ------- | ------ | ---- |
| `tests/test_auth.py` | 9 | login, token ausente/inválido/expirado, bcrypt, senha nunca exposta |
| `tests/test_permissions.py` | 11 | papéis, 401 × 403, dono do recurso, sem promoção a admin |
| `tests/test_usuarios.py` | 5 | CRUD de usuários, eventos, inscrições, certificados e categorias |
| `tests/test_regras_negocio.py` | 12 | R1–R15 (capacidade, duplicidade, estados terminais) |
| `tests/test_validacoes.py` | 10 | 422 e 404 |
| `tests/test_erros.py` | 5 | envelope de erro e contrato do OpenAPI (novo na 3AV) |

Saída integral: [`evidencias/pytest-v-3av.txt`](evidencias/pytest-v-3av.txt). O banco de teste continua isolado via `tests/conftest.py`; a suíte não toca no banco local nem no de produção.

## 5. Swagger/OpenAPI

O documento gerado em `/openapi.json` agora contém:

- título `Esuda Certificados`, versão `2.0.0`, tags por domínio;
- `OAuth2PasswordBearer` com `tokenUrl: api/v1/auth/login` (botão **Authorize**);
- 19 operações protegidas por JWT;
- respostas 400/401/403/404/422/500 com `$ref` para `RespostaErro` em todas as rotas v1.

Evidência completa: [`evidencias/swagger-3av.txt`](evidencias/swagger-3av.txt).

## 6. Ambiente, deploy e segurança

- `requirements.txt`: FastAPI, Uvicorn, SQLAlchemy, psycopg2-binary, python-jose, bcrypt, Pydantic, pytest/httpx.
- `.env.example`: `DATABASE_URL`, `JWT_SECRET_KEY`, `JWT_ALGORITHM`, `ACCESS_TOKEN_EXPIRE_MINUTES`, `DB_ECHO`, `BACKEND_CORS_ORIGINS` — sem credenciais reais.
- `render.yaml`: serviço web + Postgres persistente; `DATABASE_URL` e `JWT_SECRET_KEY` injetados pelo Render.
- `app/main.py`: `create_all()` no boot, **sem** `drop_all()`, preservando dados entre reinicializações.
- Nenhum `.env` ou arquivo `.db` é versionado (`.gitignore`).

## 7. Evidências e versionamento

- GitHub: <https://github.com/thiciriano/api_certificados_esuda> · branch `feat/auth-jwt` · PR #1.
- Tags: `v1.0.0` (entrega 2) e `v1.1.0` (entrega 3).
- Histórico desta entrega: `d827059`, `68a1058`, `d86bcce`, `4a4aed7`, `b7d5924` e os commits de documentação seguintes.
- Evidências: [`pytest-v-3av.txt`](evidencias/pytest-v-3av.txt), [`swagger-3av.txt`](evidencias/swagger-3av.txt), além das requisições e do pytest da entrega 2 em `evidencias/`.
