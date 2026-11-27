# Relatório Final — Esuda Certificados

Entrega final consolidada da API REST de eventos acadêmicos, inscrições e certificados da Faculdade ESUDA (Primeira, Segunda e Terceira Unidades).

**Integrante:** Thiago Neves  
**Repositório:** <https://github.com/thiciriano/api_certificados_esuda>  
**API pública:** <https://api-certificados-esuda.onrender.com>  
**Swagger publicado:** <https://api-certificados-esuda.onrender.com/docs>  
**Versão entregue:** `v2.0.0` (`main` @ `8495bd3`)

---

## 1. Links e artefatos da entrega

| Item | Local |
| ---- | ----- |
| Código-fonte completo | GitHub, branch `main` (PR #1 mesclado) |
| Histórico de commits | `git log` — desde `b923b98` (1AV) até `8495bd3` (final) |
| Tags | `v1.0.0` (2AV), `v1.1.0` (3AV), `v2.0.0` (final) |
| README técnico | [`README.md`](../README.md) |
| API publicada | <https://api-certificados-esuda.onrender.com> · `/health` responde 200 |
| Swagger publicado | <https://api-certificados-esuda.onrender.com/docs> |
| Matriz de permissões | [`app/matriz_permissoes.md`](../app/matriz_permissoes.md) |
| Relatório 1AV → 2AV | [`docs/relatorio_evolucao_2av.md`](relatorio_evolucao_2av.md) |
| Relatório da 3ª entrega | [`docs/relatorio_terceira_entrega.md`](relatorio_terceira_entrega.md) |
| Regras de negócio R1–R16 | [`app/regras_negocios.md`](../app/regras_negocios.md) |
| Apresentação/defesa | [Markdown](apresentacao_final.md) · [PPTX](apresentacao/apresentacao_final.pptx) · [PDF](apresentacao/apresentacao_final.pdf) |

---

## 2. Requisitos atendidos

| Requisito final | Situação | Evidência |
| ---------------- | -------- | --------- |
| Todos os CRUDs com persistência real | Atendido | 5 entidades (usuários, eventos, inscrições, certificados, categorias) com SQLAlchemy; SQLite local e Postgres no Render |
| Relacionamentos e regras de negócio | Atendido | R1–R16 em `app/regras_negocios.md`; `tests/test_regras_negocio.py` |
| JWT + senha segura + expiração | Atendido | `app/core/security.py` (bcrypt + HS256 com `exp`); `tests/test_auth.py` |
| Matriz de permissões integral | Atendido | `PERFIS` em `app/core/permissions.py`, dependências em `deps.py`, 19 operações protegidas; `tests/test_permissions.py` |
| Testes automatizados | Atendido | **52 testes passando** em 6 arquivos — `docs/evidencias/pytest-v-3av.txt` |
| Melhorias de arquitetura/qualidade | Atendido | 3 refatorações com commits dedicados (seção 4) |
| Swagger/OpenAPI completo e atualizado | Atendido | `/docs`, `OAuth2PasswordBearer`, `RespostaErro` — `docs/evidencias/swagger-3av.txt` |
| README técnico completo | Atendido | Instalação, execução, tecnologias, estrutura, endpoints, testes, deploy e evidências |
| Código no GitHub com histórico e versão | Atendido | PR #1 mesclado, tags `v1.0.0`/`v1.1.0`/`v2.0.0` |
| API publicada com HTTPS | Atendido | <https://api-certificados-esuda.onrender.com> |
| Registros persistidos no ambiente publicado | Atendido | Postgres persistente (`render.yaml`); `create_all()` sem `drop_all()` |
| Demonstração de login, autorização, CRUD, regras e testes | Atendido | `docs/evidencias/api-publica.txt` e evidências locais |
| Decisões técnicas e dificuldades | Atendido | Seção 6 e slide 12 da apresentação |
| Apresentação e defesa técnica | Atendido | Markdown + PPTX + PDF em `docs/apresentacao*` |

---

## 3. Evolução resumida (1AV → final)

| Etapa | Principais entregas | Commit/tag de referência |
| ----- | ------------------- | ------------------------ |
| 1ª unidade | DER, regras R1–R10, backlog, CRUDs iniciais, Swagger | `b923b98` |
| 2ª unidade | Correção do prefixo `/api/v1`, `vagas_disponiveis`, cascata, JWT, bcrypt, `/usuarios/me`, matriz de permissões, R11–R16, 47 testes, Render | `v1.0.0` |
| 3ª unidade | Handlers centralizados de erro, `app/services/escopo.py`, `app/services/validacoes.py`, 52 testes | `v1.1.0` |
| Entrega final | Merge do PR #1 em `main`, URL pública correta, relatório, apresentação e evidências de produção | `v2.0.0` |

O detalhamento com rastreabilidade de cada regra e os cinco bugs corrigidos entre a 1ª e a 2ª entrega está em [`docs/relatorio_evolucao_2av.md`](relatorio_evolucao_2av.md).

---

## 4. Melhorias de arquitetura e qualidade

1. **Tratamento centralizado de erros** (`d827059`) — `app/core/errors.py` com handlers para `HTTPException`, `RequestValidationError` e exceções inesperadas. Envelope único `{success, error, message, detail}` e schema `RespostaErro` em todas as rotas v1.
2. **Serviço de escopo dos recursos** (`68a1058`) — `app/services/escopo.py` concentra as regras de dono/vínculo antes repetidas nos routers de inscrições e certificados.
3. **Validações de unicidade centralizadas** (`d86bcce`) — `app/services/validacoes.py` unifica e-mail, título de evento e nome de categoria, com parâmetro opcional de `id` para atualizações.

Estrutura final: `api/v1/routers` (HTTP), `schemas` (Pydantic), `models` (SQLAlchemy), `core` (config, segurança, dependências, permissões e erros), `services` (regras reutilizáveis) e `database` (engine/sessão).

---

## 5. Evidências funcionais

| Evidência | Arquivo |
| --------- | ------- |
| Suíte completa (`pytest -v`, 52 passed) | [`docs/evidencias/pytest-v-3av.txt`](evidencias/pytest-v-3av.txt) |
| OpenAPI final (auth, schemas de erro) | [`docs/evidencias/swagger-3av.txt`](evidencias/swagger-3av.txt) |
| Requisições locais de acesso permitido/negado | [`docs/evidencias/requisicoes-acesso.txt`](evidencias/requisicoes-acesso.txt) |
| Demonstração na API publicada | [`docs/evidencias/api-publica.txt`](evidencias/api-publica.txt) |

A demonstração pública cobre: `GET /health`, `GET /docs`, `GET /openapi.json`, login JWT, `GET /api/v1/usuarios/me` com e sem token, `403` para participante em `POST /api/v1/eventos`, `400` em e-mail duplicado, `422` em senha curta e consultas públicas de eventos/categorias. Tokens são truncados no log para não expor credenciais.

---

## 6. Decisões técnicas

- **FastAPI + Pydantic v2:** validação declarativa e OpenAPI gerado a partir do código, evitando divergência entre documentação e implementação.
- **JWT stateless (HS256):** o token carrega `sub`, `papel` e `exp`; a chave vem de `JWT_SECRET_KEY`, sem sessão no servidor.
- **bcrypt para senhas:** hash com salt, nunca exposto nos schemas de saída.
- **Autorização em duas camadas:** flags de `PERFIS` por papel (`precisa_de_permissao`) e checagem de dono/vínculo (`eh_dono_ou_admin`, `app/services/escopo.py`).
- **Postgres gerenciado no Render:** `DATABASE_URL` injetada por variável de ambiente, `pool_pre_ping`, `create_all()` no boot sem `drop_all()` para preservar dados entre deploys.
- **Camada de serviços extraída:** consultas de escopo e unicidade reutilizadas por múltiplos routers.
- **Evidências versionadas:** saídas de pytest, OpenAPI e requisições reais no repositório, com segredos removidos.

---

## 7. Dificuldades enfrentadas

- **URL pública antiga fora do ar:** `https://esuda-certificados.onrender.com` respondia 404 com `x-render-routing: no-server`. A URL correta, informada pelo contratante, é `https://api-certificados-esuda.onrender.com`.
- **Deploy desatualizado:** mesmo com a URL correta no ar, o `/openapi.json` público mostrava `version 1.0.0`, rotas sem `/api/v1` e nenhum `securitySchemes`. A causa era o `main` parado na 1AV: as alterações estavam em `feat/auth-jwt` com PR #1 aberto. A mesclagem do PR e o push de `main` dispararam a publicação da versão final.
- **Concorrência no push:** o PR foi mesclado no GitHub enquanto o merge local era preparado; o push foi rejeitado (`fetch first`). Resolvido com `fetch`, `rebase origin/main` e novo push.
- **Ambiente de execução:** o Python do sistema não tinha as dependências instaladas; elas foram instaladas em um diretório isolado (`/tmp/opencode/pylib`) para rodar os 52 testes e gerar o OpenAPI sem afetar o projeto.
- **Ferramentas de apresentação ausentes:** não havia LibreOffice/pandoc; PPTX e PDF foram gerados com `python-pptx` e `reportlab` a partir do único roteiro Markdown versionado.
- **Aviso do `TestClient`:** a versão atual de Starlette recomenda `httpx2`; o aviso é registrado nas evidências e não afeta os resultados.

---

## 8. Como executar e validar

```bash
pip install -r requirements.txt
cp .env.example .env          # ajustar DATABASE_URL/JWT_SECRET_KEY se necessário
python seed.py                # dados de exemplo (opcional)
uvicorn app.main:app --reload
pytest -v                     # 52 testes
```

Swagger local: <http://localhost:8000/docs> · Health: <http://localhost:8000/health>.
