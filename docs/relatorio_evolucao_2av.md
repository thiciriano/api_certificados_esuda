# Relatório de Evolução — Esuda Certificados (1AV → 2AV)

## 1. Revisão e consolidação do MVP

| Item | Situação na 1AV | Ação na 2AV |
| ------------------ | ----------------------- | -------------------- |
| CRUD das entidades | Completo (sem auth) | Mantido e protegido por JWT + perfil |
| Persistência | SQLite local | SQLite local + Postgres no deploy (`DATABASE_URL`), `create_all` sem `drop_all` |
| Relacionamentos | Implementados | Mantidos; exclusões em cascata corrigidas (certificado → inscrição → evento) |
| Regras de negócio | R1–R4, R6, R8, R10 ok; R5, R7, R9 pendentes | R1–R16 todas implementadas (ver `app/regras_negocios.md`) |
| Validações | Dict `Body(...)` sem schema | Schemas Pydantic aplicados em todas as rotas (entrada e saída) |
| Documentação | Inicial, sem securityScheme | OpenAPI com tags, exemplos e botão Authorize (Bearer) |
| Segurança | Planejada | JWT + bcrypt + `.env` fora do repositório |
| Testes | Não implementados | 47 testes em 5 arquivos (mínimo exigido: 20) |

## 2. Bugs/correções encontrados na revisão da 1AV

1. **Prefixo `/api/v1` ausente** — o `seed.py` da 1AV chamava `http://localhost:8000/api/v1/...`, mas o `api_router` era incluído sem prefixo; todas as chamadas do seed davam 404. Corrigido em `app/api/v1/api.py`.
2. **Inscrição decrementava `capacidade` em vez de `vagas_disponiveis`** — o saldo de vagas nunca era exibido corretamente e a regra R6 não funcionava de verdade (`app/api/v1/routers/inscricoes.py`).
3. **Exclusão de evento/incrição deixava registros órfãos** — o DELETE de evento removia só o evento; agora remove certificados e inscrições vinculados antes (`app/api/v1/routers/eventos.py`).
4. **Exclusão de inscrição já cancelada devolvia vaga duas vezes** — agora só devolve se a inscrição estava `ativa`.
5. **E-mail duplicado dependia de loop manual** — trocado por query com filtro + tratamento de `IntegrityError` (corrida entre dois requests).

## 3. Três melhorias técnicas (refatoração obrigatória)

1. **Remoção de credenciais do código**: a 1AV tinha `JWT_SECRET_KEY` com valor fixo e o `database.py` com URL dura; agora tudo vem de `Settings` (`.env`), com `.env.example` versionado e `.gitignore` bloqueando o `.env`. O `config.py` também migrou do `validator` deprecated do Pydantic v1 para `field_validator`.
2. **Separação de responsabilidades nas rotas**: os endpoints da 1AV recebiam `dict = Body(...)` e faziam validação manual com `for` em todos os registros (`for u in db.query(Usuario).all()`). Agora existem schemas Pydantic na entrada e na saída (`response_model`), as validações viraram queries com filtro, e a autorização saiu das rotas para `app/core/deps.py` (`precisa_de_permissao`) + `app/core/permissions.py` (matriz `PERFIS`).
3. **Padronização das respostas e tratamento de erros**: todas as operações de escrita devolvem o envelope `{success, message, data}` com schemas tipados (`RespostaUsuario`, `RespostaEvento`, ...), senhas saem dos schemas de resposta, e cada rota valida existência (404), perfil (403) e regra de negócio (400) antes de gravar. O `InscriçãoOut` aninhava `UsuarioOut` que **expunha a senha** na 1AV — corrigido.

## 4. Autenticação e autorização implementadas

- `POST /api/v1/auth/login` (OAuth2 password flow) → devolve `{access_token, token_type}`.
- Senhas com **bcrypt** (`hash_senha`/`verificar_senha` em `app/core/security.py`).
- Token com `sub` = id do usuário e `papel`; validado por `get_current_user`/`get_current_active_user` (401 sem token, token inválido ou expirado; 403 para inativo).
- `GET /api/v1/usuarios/me` identifica o usuário autenticado.
- Matriz de permissões completa em `app/matriz_permissoes.md`, com comparação de dono do recurso (`eh_dono_ou_admin`) e vínculo de organizador (`criado_por`).
- Cadastro público não aceita papel `admin` (R14) e `PUT /usuarios/{id}` não deixa usuário comum alterar o próprio papel.

## 5. Testes automatizados (47 testes, todos passando)

| Arquivo | Categoria | Testes |
| ------- | --------- | ------ |
| `tests/test_auth.py` | Autenticação e JWT | 8 |
| `tests/test_permissions.py` | Autorização e controle de acesso | 11 |
| `tests/test_usuarios.py` | CRUD e operações principais | 5 |
| `tests/test_regras_negocio.py` | Regras de negócio (R1–R15) | 13 |
| `tests/test_validacoes.py` | Validação e tratamento de erros | 10 |

- Banco de teste isolado em `/tmp/opencode/esuda_pytest.db` (variável `DATABASE_URL` setada no `conftest.py` antes de importar a app) — não toca no banco local nem no de produção.
- Fixtures por perfil (`admin_headers`, `organizador_headers`, `participante_headers`) e `token_expirado_headers`.
- Execução: `pytest` (raiz do projeto). Resultado: **47 passed**.

## 6. Rastreabilidade requisitos × endpoints

| ID | Requisito ou regra | Endpoint relacionado | Status |
| ---- | ------------------------------------------ | ---------------------- | ------------ |
| RF01 | Cadastro de usuário | POST `/api/v1/usuarios` | Implementado |
| RF02 | Login e token JWT | POST `/api/v1/auth/login` | Implementado |
| RF03 | Usuário autenticado | GET `/api/v1/usuarios/me` | Implementado |
| RN01 | Impedir cadastro duplicado (e-mail) | POST `/api/v1/usuarios` | Implementado |
| RN02 | Restringir exclusão de evento por perfil | DELETE `/api/v1/eventos/{id}` | Implementado |
| RN03 | Alteração de evento apenas pelo dono/admin | PUT `/api/v1/eventos/{id}` | Implementado |
| RN04 | Inscrição duplicada | POST `/api/v1/inscricoes` | Implementado |
| RN05 | Data futura do evento | POST/PUT `/api/v1/eventos` | Implementado |
| RN06 | Vagas disponíveis | POST `/api/v1/inscricoes` | Implementado |
| RN07 | Cancelamento apenas da própria inscrição | PUT `/api/v1/inscricoes/{id}` | Implementado |
| RN08 | Certificado só para inscrição ativa | POST `/api/v1/certificados` | Implementado |
| RN09 | Título de evento único | POST/PUT `/api/v1/eventos` | Implementado |
| RN10 | Um certificado por inscrição | POST `/api/v1/certificados` | Implementado |
| RN11 | Categoria com eventos não exclui | DELETE `/api/v1/categorias/{id}` | Implementado |
| RN12 | Capacidade ≥ inscrições ativas | PUT `/api/v1/eventos/{id}` | Implementado |
| RN13 | Certificado cancelado é terminal | PUT `/api/v1/certificados/{id}` | Implementado |
| RN14 | Sem promoção a admin | POST/PUT `/api/v1/usuarios` | Implementado |
| RN15 | Evento inativo não aceita inscrição | POST `/api/v1/inscricoes` | Implementado |
| RN16 | Senha em hash, nunca em texto puro | POST `/api/v1/usuarios`, login | Implementado |

## 7. Deploy

- `render.yaml` na raiz: blueprint com serviço web + banco Postgres (variável `DATABASE_URL` injetada automaticamente).
- `JWT_SECRET_KEY` com valor gerado pelo Render (não versionado).
- Comando de start: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`.
- `create_all()` roda no boot (sem `drop_all`), então os dados persistem entre reinicializações.
