# Apresentação Final — Esuda Certificados

Roteiro para apresentação e defesa técnica (10 a 12 minutos). Cada slide traz o conteúdo projetado e a fala sugerida.

---

## Slide 1 — Esuda Certificados

- API REST para eventos acadêmicos, inscrições e certificados da Faculdade ESUDA
- Entrega final: 1ª + 2ª + 3ª unidades consolidadas
- Thiago Neves

**Fala:** "Bom dia. Apresento a API Esuda Certificados, evoluída do MVP da primeira unidade até uma versão segura, testada e publicada. Ao longo da apresentação mostro a arquitetura, segurança, autorização, testes, deploy e uma demonstração funcional."

---

## Slide 2 — Problema e objetivo

- Antes: eventos e certificados controlados em planilhas e papel
- Riscos: duplicidade, erro humano, dificuldade de consulta e auditoria
- Objetivo: centralizar cadastro, inscrições e emissão em uma API segura e documentada
- Entidades: Usuário, Categoria, Evento, Inscrição e Certificado

**Fala:** "O problema de negócio era a falta de uma fonte única de verdade. A API passou a concentrar os cinco domínios com persistência real, validações e regras documentadas."

---

## Slide 3 — Evolução entre as entregas

| Entrega | Entregue |
| ------- | -------- |
| 1ª | DER, regras R1–R10, backlog, CRUDs iniciais, Swagger |
| 2ª | JWT, bcrypt, `/usuarios/me`, matriz de permissões, 47 testes, Render |
| 3ª | Handlers de erro, serviços de escopo e validação, 52 testes |
| Final | Publicação atualizada, evidências, apresentação e defesa |

**Fala:** "Não reconstruímos o sistema: evoluímos o MVP. A segunda entrega corrigiu cinco bugs da primeira, a terceira eliminou duplicações e padronizou erros, e a final fecha a publicação."

---

## Slide 4 — Arquitetura

- FastAPI + Pydantic v2 + SQLAlchemy 2.x
- Camadas: `api/v1/routers`, `core`, `services`, `models`, `schemas`, `database`
- `core`: config, segurança, dependências de JWT, matriz e erros
- `services`: escopo dos recursos e validações de unicidade
- Banco: SQLite local / PostgreSQL persistente em produção

**Fala:** "A separação de responsabilidades foi uma das melhorias: rotas cuidam do HTTP, schemas validam entrada e saída, models representam o banco, core concentra regras transversais e services agrupa consultas reutilizadas."

---

## Slide 5 — Autenticação e proteção das credenciais

- `POST /api/v1/auth/login` (OAuth2 password flow; `username` é o e-mail)
- Senha armazenada como hash bcrypt — nunca em texto puro
- JWT HS256 com `sub`, `papel` e `exp` (`ACCESS_TOKEN_EXPIRE_MINUTES`)
- Chave `JWT_SECRET_KEY` via variável de ambiente; `.env` fora do Git
- 401 para token ausente, inválido ou expirado

**Fala:** "O login valida a senha com bcrypt e devolve um token com expiração. As rotas protegidas decodificam o token, buscam o usuário pelo `sub` e rejeitam qualquer token inválido com 401."

---

## Slide 6 — Autorização e acesso aos recursos

- Três papéis: `admin`, `organizador`, `participante`
- Matriz em `app/matriz_permissoes.md` com endpoints protegidos
- `precisa_de_permissao` aplica as flags de `PERFIS`; 403 para perfil sem permissão
- `eh_dono_ou_admin` e `app/services/escopo.py` impedem acesso a recurso alheio
- Participante inscreve-se em si mesmo; organizador só edita eventos que criou

**Fala:** "Autorização é diferente de autenticação. Um usuário logado como participante recebe 403 ao tentar criar evento; um organizador não altera evento de outro organizador mesmo mudando o ID na URL."

---

## Slide 7 — Regras de negócio e qualidade

- R1–R16 implementadas e rastreadas em `app/regras_negocios.md`
- Exemplos: e-mail e título únicos, capacidade/vagas, inscrição duplicada, certificado só com inscrição ativa
- Três melhorias da 3ª entrega:
  1. envelope único de erro + handlers centrais
  2. serviço de escopo de recursos
  3. serviço de validações de unicidade

**Fala:** "As regras são validadas no back-end e demonstradas por testes. As três refatorações reduziram duplicação e deixaram o contrato de erro previsível para o cliente."

---

## Slide 8 — Testes automatizados

- 52 testes pytest em 6 arquivos (mínimo exigido: 15/20)
- Categorias: autenticação (9), autorização (11), CRUD (5), regras (12), validação (10), erros/OpenAPI (5)
- Banco isolado em `tests/conftest.py`; não toca em produção
- Resultado: **52 passed** — `docs/evidencias/pytest-v-3av.txt`

**Fala:** "Cada teste verifica comportamento, não apenas status 200. Por exemplo, o teste de capacidade cria um evento com uma vaga, inscreve um usuário e confirma que o segundo recebe 400."

---

## Slide 9 — Swagger e documentação

- `/docs` com tags por domínio e botão Authorize
- `OAuth2PasswordBearer` com `tokenUrl: api/v1/auth/login`
- 19 operações protegidas; schemas de entrada/saída e `RespostaErro` no OpenAPI
- README com instalação, execução, estrutura, endpoints, testes e links de evidência

**Fala:** "O Swagger é gerado a partir do código, então não diverge da implementação. O envelope de erro aparece documentado com 400, 401, 403, 404, 422 e 500."

---

## Slide 10 — Deploy e persistência

- URL pública: https://api-certificados-esuda.onrender.com
- Swagger: https://api-certificados-esuda.onrender.com/docs
- `render.yaml`: serviço web + Postgres persistente
- `DATABASE_URL` e `JWT_SECRET_KEY` configurados no Render
- Boot usa `create_all()` sem `drop_all()` — dados sobrevivem a restart

**Fala:** "A configuração sensível ficou fora do repositório. O banco é persistente e a criação de tabelas não apaga registros existentes."

---

## Slide 11 — Demonstração funcional

1. `GET /health` e `GET /docs` no ambiente publicado
2. `POST /api/v1/auth/login` → JWT
3. `GET /api/v1/usuarios/me` com token → 200; sem token → 401
4. Participante em `POST /api/v1/eventos` → 403
5. Cadastro duplicado → 400; senha curta → 422
6. Consulta a eventos/categorias → 200

**Fala:** "A demonstração cobre login, autorização, CRUD de leitura/escrita e regras de negócio diretamente na URL publicada. O log completo está em `docs/evidencias/api-publica.txt`."

---

## Slide 12 — Decisões, dificuldades e encerramento

- Decisões: FastAPI + Pydantic, JWT stateless, papéis em código + matriz documentada, Postgres gerenciado
- Dificuldades: URL antiga sem serviço associado, deploy desatualizado em `main`, diferenças entre SQLite local e Postgres, depreciação do `TestClient`
- Lições: versionar evidências, validar deploy com `openapi.json` e integrar PR antes de publicar

**Fala:** "A dificuldade mais importante foi perceber que a URL antiga estava no ar, mas servia a versão antiga. Validamos isso pelo `openapi.json` e corrigimos mesclando o PR em `main`. Estou à disposição para perguntas."

---

# Defesa técnica — perguntas e respostas

**Como o sistema identifica o usuário autenticado?**
O token JWT contém `sub` com o id do usuário. `get_current_user` decodifica e valida assinatura/expiração, consulta o usuário no banco e injeta o objeto na rota.

**O que acontece quando o token expira?**
`decode_access_token` captura `JWTError` e a dependência devolve 401 com `WWW-Authenticate: Bearer`. Há teste específico com token gerado com `expires_delta` negativo.

**Como uma rota verifica se o usuário possui permissão?**
Pela dependência `precisa_de_permissao("pode_criar_evento")`, que consulta `PERFIS[papel]`. Sem permissão, retorna 403; sem token, a própria dependência de autenticação retorna 401.

**Como impedir que um usuário altere dados de outro?**
`eh_dono_ou_admin` compara o id do token com o dono do recurso; para eventos e inscrições, `app/services/escopo.py` usa `criado_por` e o vínculo com o evento. Mudar o id na URL não burla a regra.

**Qual a diferença entre autenticação e autorização?**
Autenticação responde "quem é você" (credenciais → JWT); autorização responde "você pode fazer isso" (perfil e dono do recurso).

**Como as credenciais são protegidas?**
Senha com bcrypt, nunca retornada nos schemas; chave JWT em variável de ambiente; `.env` e `.db` ignorados pelo Git; `.env.example` sem segredos reais.

**Como o sistema se conecta ao banco de produção?**
`DATABASE_URL` injetada pelo Render em `Settings`; SQLAlchemy cria o engine com `pool_pre_ping`. Em produção é Postgres persistente.

**O que acontece se o servidor for reiniciado?**
`create_all()` roda no boot e cria tabelas ausentes, sem `drop_all()`. Como o banco é persistente, os registros permanecem.

**Quais melhorias foram feitas em relação à primeira unidade?**
Correção do prefixo `/api/v1`, cálculo de `vagas_disponiveis`, exclusão em cascata, e-mail duplicado, schemas Pydantic, handlers de erro, serviços de escopo/validação e 52 testes.

**Como os testes garantem as regras de negócio?**
Cada regra tem ao menos um teste com cenário positivo e negativo — por exemplo, capacidade, duplicidade, cancelamento devolvendo vaga e certificado terminal.

**Por que o deploy estava servindo a versão antiga?**
O Render acompanhava `main`, que estava parado na 1AV; as alterações estavam em `feat/auth-jwt` com PR aberto. A mesclagem do PR atualizou `main` e disparou o deploy da versão final.
