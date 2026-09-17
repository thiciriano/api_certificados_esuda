# Guia de perguntas da defesa — Esuda Certificados (Primeira Entrega)

> Documento de estudo do grupo (não vai junto com a entrega). Cada pergunta é algo que o professor provavelmente vai perguntar com base nas diretrizes da atividade, seguida de uma resposta pronta e de **como provar a resposta**:
>
> - **📂 No código:** arquivo + trecho pra abrir no editor e mostrar na hora;
> - **🌐 No Swagger:** passo a passo concreto (rota, payload e resultado esperado).
>
> Dica: antes da defesa, deixe abertos no editor os 4 arquivos que mais aparecem aqui: `app/api/v1/routers/usuarios.py`, `inscricoes.py`, `certificados.py` e `app/schemas/evento.py`, além do Swagger em `http://localhost:8000/docs`.

## Como usar

- Ler uma vez inteira antes da defesa e **executar cada validação do 🌐 de verdade** — resposta testada vale mais que resposta decorada;
- As respostas citam os números dos documentos (RN, US, status codes) — mostrar que sabemos onde cada coisa está escrita conta ponto;
- Se aparecer pergunta fora do guia, a estratégia é: responder curto e oferecer mostrar no código (`"posso mostrar onde isso está implementado"`).

---

## 1. Contexto do problema

**P: "Expliquem o problema que o sistema resolve."**

R: Hoje o controle de eventos acadêmicos da Esuda (palestras, workshops, cursos) é feito à mão — lista de presença em papel, planilha e certificado editado um por um. Isso gera erros de contagem de vagas, inscrição duplicada e demora pra emitir certificado. A nossa API centraliza isso: cadastro de eventos com controle de capacidade, inscrição com regras de validação e emissão de certificado com código único.

> **📂 No código:** o escopo aparece no próprio `app/main.py` (linhas 19-24) — `title="Esuda Certificados"` e a descrição "API para gerenciar eventos acadêmicos, inscrições e emissão de certificados". O contexto detalhado está em `docs/01-contexto-do-problema.md`.
>
> **🌐 No Swagger:** abrir `/docs` — no topo aparece o nome e a descrição do projeto, e os 5 grupos de rotas (Usuários, Eventos, Inscrições, Certificados, Categorias) já desenham o problema inteiro sem falar nada.

**P: "Por que API e não um sistema com telas?"**

R: Porque a proposta da disciplina é o backend. A API expõe as regras de negócio pra qualquer frente consumir depois (site, aplicativo, sistema da secretaria). O Swagger em `/docs` já serve de interface pra testar tudo sem construir tela.

> **📂 No código:** no projeto não existe nenhuma tela/template — só rotas. O `app/main.py` tem ~30 linhas: sobe a aplicação e liga as rotas, nada de front-end.
>
> **🌐 No Swagger:** clicar em "Try it out" em qualquer rota (ex.: `GET /api/v1/eventos`) e executar — a própria página do Swagger é a "interface" que testa o backend.

**P: "O que é o MVP de vocês?"**

R: O fluxo completo de certificação sem login: cadastrar usuário, criar categoria e evento, inscrever respeitando vagas, cancelar inscrição e emitir certificado com código único. O que ficou de fora e por quê está documentado no backlog (login, permissões e testes automatizados são da unidade 2).

> **📂 No código:** `docs/10-backlog.md` — a coluna "Entrega" marca o corte: US01 a US10 na entrega 1; US11 a US14 na 2.
>
> **🌐 No Swagger:** percorrer o roteiro da seção 9 deste guia — ele é o MVP rodando de ponta a ponta em 3 minutos.

---

## 2. Perfis de usuário e permissões

**P: "Quais são os perfis?"**

R: Três: **Admin** (coordenação/secretaria — gerencia tudo, único que exclui evento), **Organizador** (professor responsável — cria os próprios eventos, vê inscritos, emite certificado) e **Participante** (aluno — consulta evento, se inscreve e cancela a própria inscrição).

> **📂 No código:** `app/models/usuario.py` linha 16 — `papel = Column(String(20), ..., default="participante")` com o comentário "admin, organizador ou participante".
>
> **🌐 No Swagger:** `POST /api/v1/usuarios` criando um usuário com `"papel": "organizador"` (201) e outro **sem** mandar papel — a resposta mostra que ele nasceu `"participante"`.

**P: "Por que definiram perfil se ainda não existe login?"**

R: Porque o perfil influencia decisões desde já: o campo `papel` já nasce na tabela de usuários com valor padrão `participante`, e a matriz de permissões orientou o desenho das rotas. Se deixássemos pra pensar nisso na unidade 2, teríamos que mexer em banco e cadastro de uma vez.

> **📂 No código:** a coluna `papel` já está no model (`app/models/usuario.py`), no schema de criação (`app/schemas/usuario.py` linha 9) e na migration (`alembic/versions/...cria_tabelas_iniciais.py`).
>
> **🌐 No Swagger:** `GET /api/v1/usuarios` — a listagem mostra o `papel` salvo de cada usuário, provando que o dado pra autorização já existe no banco.

**P: "Quem pode excluir um evento? Por que o organizador não pode?"**

R: Só o admin (RN15). O organizador que quiser tirar o evento do ar usa o **cancelamento** (muda o status), que preserva o histórico. Exclusão apaga de vez — decisão que ficaria com a coordenação, seguindo a matriz de exemplo passada em aula.

> **📂 No código:** `app/api/v1/routers/eventos.py` linha 101 — comentário nosso: "a partir da segunda entrega só o admin vai poder chegar nessa rota (jwt)". E o cancelamento por status está no `PUT /eventos/{id}` (linhas 76-80).
>
> **🌐 No Swagger:** mostrar `PUT /api/v1/eventos/{id}` com `{"status": "cancelado"}` → 200 (o "tirar do ar" do organizador) e, no lugar de provar o bloqueio (que ainda não existe), explicar que hoje o DELETE responde pra qualquer um e é exatamente isso que o JWT vai fechar na unidade 2.

**P: "Como a matriz vai virar código na unidade 2?"**

R: O token JWT vai trazer o papel do usuário; uma dependência do FastAPI pega esse papel e compara com a matriz antes de executar a rota. Se não puder, retorna **403**. As rotas em si não mudam — só recebem a dependência.

> **📂 No código:** `docs/08-matriz-de-permissoes.md` é o contrato do que será checado; o campo `papel` no banco é de onde o token vai nascer.
>
> **🌐 No Swagger:** abrir a matriz no documento e contrastar: hoje `DELETE /api/v1/eventos/{id}` executa sem token nenhum — na unidade 2 essa mesma chamada vai devolver 403 pra quem não for admin. Mostrar o "antes" já prepara a explicação do "depois".

---

## 3. Regras de negócio

**P: "Citem três regras de negócio."**

R: Boas opções (todas testadas de ponta a ponta):
1. **RN04** — um evento não pode ultrapassar a capacidade de inscritos ativos (retorna 400);
2. **RN03** — o mesmo usuário não pode ter duas inscrições ativas no mesmo evento (400);
3. **RN11/RN12** — certificado só é emitido para inscrição ativa e só existe um por inscrição (400).

> **📂 No código:** as três estão em sequência em `app/api/v1/routers/inscricoes.py` (linhas 33-48) e `certificados.py` (linhas 20-27) — dá pra ler o `if` de cada uma com o `raise HTTPException` do lado.
>
> **🌐 No Swagger:** as três provas estão passo a passo nas três perguntas seguintes.

**P: "Onde cada regra é validada: no schema ou na rota? Vocês decidiram como?"**

R: Foi um critério nosso: **schema** quando a regra vale pro campo isolado, sem olhar o banco (RN02 e-mail válido, RN05 capacidade maior que zero, RN06 data não pode ser passada — tudo 422). **Rota** quando a regra depende do estado do banco (duplicidade, lotação, status do evento — tudo 400). Essa separação é a mesma que explica a diferença entre 422 e 400.

> **📂 No código:** `app/schemas/evento.py` linhas 16-30 — os dois `@field_validator` (capacidade e data). Do outro lado, `inscricoes.py` linhas 25-48 — os `if`s que consultam o banco antes de salvar.
>
> **🌐 No Swagger:** `POST /api/v1/eventos` com `"capacidade": 0` → **422** e a resposta nem chega na rota (erro do schema, com a mensagem "a capacidade tem que ser maior que zero"). Já `POST /api/v1/inscricoes` duplicado → **400** (a requisição está perfeita; quem nega é a regra que olha o banco).

**P: "Qual a diferença entre 400 e 422 no projeto de vocês?"**

R: **422** é erro de validação de campo — formato, obrigatório, valor inválido (comportamento padrão do Pydantic no FastAPI). **400** é regra de negócio quebrada — a requisição está bem formada, mas o estado do banco não permite: já inscrito, evento lotado, certificado duplicado. Exemplo: capacidade 0 → 422; inscrever usuário que já está inscrito → 400.

> **📂 No código:** o 422 nasce em `app/schemas/evento.py` (`raise ValueError(...)` dentro do validator) e o 400 nasce em `app/api/v1/routers/inscricoes.py` (`raise HTTPException(status_code=400, ...)`).
>
> **🌐 No Swagger:** fazer os dois no mesmo evento: (1) `POST /eventos` com `"capacidade": 0` → 422; (2) evento criado com capacidade 2, inscrever o mesmo usuário 2 vezes → a 2ª volta 400 "Usuário já está inscrito nesse evento".

**P: "Por que cancelar inscrição não apaga o registro?"**

R: Histórico. O cancelamento só troca o status para `cancelada` — o registro continua pra auditoria e porque a inscrição faz parte do rastro do evento. A vaga volta pro evento porque a contagem de capacidade só soma inscrições ativas.

> **📂 No código:** `app/api/v1/routers/inscricoes.py` linhas 93-98 — `inscricao.status = "cancelada"`, `db.commit()`... e **nenhum** `db.delete` na função (comparar com o `deletar_usuario`, que tem).
>
> **🌐 No Swagger:** `PUT /api/v1/inscricoes/{id}/cancelar` → 200 com `"status": "cancelada"`; depois `GET /api/v1/inscricoes/usuario/{usuario_id}` — a inscrição continua na lista, só mudou o status.

**P: "Quando o participante cancela, a vaga volta? Mostrem."**

R: Volta, sim. A contagem no código é `db.query(Inscricao).filter(evento_id == ..., status == "ativa").count()` — cancelada não conta. No Swagger dá pra mostrar: lota o evento, cancela uma inscrição, e a próxima inscrição entra.

> **📂 No código:** `app/api/v1/routers/inscricoes.py` linhas 42-48 — o `.filter(Inscricao.status == "ativa")` dentro da contagem é a linha exata que faz a vaga voltar.
>
> **🌐 No Swagger:** criar evento com **capacidade 2** → inscrever usuário A e B (201 e 201) → `POST` inscrição do C → **400 lotado** → cancelar a do B → `POST` do C de novo → **201**. Essa sequência é a prova mais forte da API.

**P: "Por que evento com inscrição não pode ser excluído?"**

R: RN14 — preservar o histórico. Se o evento tem inscrição, excluir apagaria o rastro das pessoas que se inscreveram. A rota devolve 400 explicando. Usuário com inscrição e categoria com evento seguem a mesma lógica.

> **📂 No código:** a mesma ideia em três lugares: `eventos.py` linhas 93-99, `usuarios.py` linhas 76-82 e `categorias.py` linhas 52-55 — todas consultam a tabela filha antes do `db.delete`.
>
> **🌐 No Swagger:** tentar os três: `DELETE /eventos/{id}` com inscrição → 400 "Esse evento já tem inscrições..."; `DELETE /usuarios/{id}` com inscrição → 400; `DELETE /categorias/{id}` com evento ligado → 400 "Essa categoria tem eventos ligados a ela, não pode excluir".

**P: "Como o código do certificado é gerado? Pode repetir?"**

R: Usamos `uuid.uuid4().hex[:8].upper()` — um identificador universal convertido em 8 caracteres hexadecimais maiúsculos, tipo `A3F19C2B`. A chance de colisão é desprezível, e mesmo assim no banco a inscrição é `unique` em certificados, garantindo um certificado por inscrição.

> **📂 No código:** `app/api/v1/routers/certificados.py` linha 32 (geração com uuid4) e `app/models/certificado.py` linha 13 — `inscricao_id ... unique=True` com o comentário "1 inscricao = 1 certificado" (a garantia no nível do banco).
>
> **🌐 No Swagger:** emitir certificados para **duas inscrições diferentes** → cada resposta traz um `codigo` distinto (ex.: `A3F19C2B` e `7B04E1DC`). Tentar o mesmo para uma inscrição já certificada → 400 "Já existe um certificado emitido para essa inscrição".

**P: "A senha pode aparecer em alguma resposta?"**

R: Nunca (RN13). O schema de resposta `UsuarioResposta` não tem o campo senha — o FastAPI só serializa o que está declarado no `response_model`. Dá pra mostrar no Swagger: cria usuário e a resposta só tem id, nome, e-mail, papel e data de cadastro.

> **📂 No código:** dois pontos fortes: (1) `app/schemas/usuario.py` linhas 22-29 — `UsuarioResposta` **sem** campo senha, com o comentário "reparo que a senha não tem aqui em cima de propósito"; (2) `app/api/v1/routers/usuarios.py` linha 29 — a senha nem é salva pura: `senha=gerar_hash_senha(dados.senha)` (hash sha256, com comentário de que na unidade 2 vira bcrypt).
>
> **🌐 No Swagger:** `POST /api/v1/usuarios` mandando `"senha": "123456"` → na resposta 201 a senha não existe. Bônus: abrir o `esuda.db` com DB Browser e mostrar que a coluna senha guarda o hash, não o texto.

---

## 4. Modelo de dados, DER e dicionário

**P: "Quais são as entidades?"**

R: Cinco: **usuarios**, **categorias**, **eventos**, **inscricoes** e **certificados**.

> **📂 No código:** a pasta `app/models/` tem exatamente 5 arquivos, um por entidade — e a migration `alembic/versions/1e905a380dc1_cria_tabelas_iniciais.py` cria 5 `create_table`.
>
> **🌐 No Swagger:** a barra lateral do `/docs` mostra as 5 tags, e cada tag espelha uma entidade.

**P: "Expliquem o DER de vocês."**

R: Categoria 1:N eventos; usuário 1:N inscrições; evento 1:N inscrições; inscrição 1:0..1 certificado. A inscrição é a tabela que resolve o N:N entre usuário e evento — e ganhou vida própria com data e status.

> **📂 No código:** os relacionamentos estão nos models como `relationship(...)`: `app/models/inscricao.py` linhas 18-20 (usuario, evento e certificado com `uselist=False` — o 0..1 do DER!) e `app/models/usuario.py` linha 19. A imagem está em `docs/der.png`.
>
> **🌐 No Swagger:** percorrer o DER com dados: criar categoria → criar evento com essa `categoria_id` → inscrever 2 usuários → emitir 1 certificado. Cada rota percorrida é um relacionamento do diagrama acontecendo.

**P: "Por que inscrição é uma tabela e não só uma relação?"**

R: Porque o N:N entre usuário e evento tem **atributos**: a data em que se inscreveu e o status (ativa/cancelada). N:N com atributo vira entidade associativa. E ela é a base do certificado.

> **📂 No código:** `app/models/inscricao.py` — além das duas FK (linhas 13-14), tem `data_inscricao` e `status` (linhas 15-16): são os atributos que justificam a entidade.
>
> **🌐 No Swagger:** a resposta do `POST /api/v1/inscricoes` devolve exatamente esses atributos (`data_inscricao`, `"status": "ativa"`) — dados que uma "relação simples" não teria onde guardar.

**P: "Por que o certificado liga na inscrição e não direto no usuário?"**

R: Porque o certificado comprova participação **naquele evento específico** — e o par usuário+evento é exatamente a inscrição. Assim ganhamos de graça a regra de um certificado por participação (unique em `inscricao_id`).

> **📂 No código:** `app/models/certificado.py` linha 13 — FK pra `inscricoes.id` com `unique=True`. E `app/models/inscricao.py` linha 20 — `uselist=False` (a inscrição sabe que tem no máximo um certificado).
>
> **🌐 No Swagger:** tentar `POST /api/v1/certificados` duas vezes na mesma inscrição → a 2ª volta 400. Não existe caminho pra "certificar o usuário no evento" sem passar pela inscrição.

**P: "O que é chave estrangeira? Onde tem no projeto?"**

R: É a coluna que aponta para a chave primária de outra tabela, garantindo a integridade do relacionamento. No projeto: `eventos.categoria_id` → `categorias.id`; `inscricoes.usuario_id` e `inscricoes.evento_id`; `certificados.inscricao_id`. Tentar inscrever com `usuario_id` inexistente devolve 404.

> **📂 No código:** `app/models/inscricao.py` linhas 13-14 — `ForeignKey("usuarios.id")` e `ForeignKey("eventos.id")`; `app/models/evento.py` tem o `categoria_id` como FK.
>
> **🌐 No Swagger:** `POST /api/v1/inscricoes` com `"usuario_id": 9999` → 404 "Usuário não encontrado" (a rota confere antes de salvar) — e o banco também teria a FK como última defesa.

**P: "O que tem no dicionário de dados?"**

R: Uma tabela por entidade com: campo, tipo, obrigatório ou não, valor padrão, restrições (PK, FK, unique) e descrição em português. Ele é a tradução campo a campo do DER.

> **📂 No código:** `docs/06-dicionario-de-dados.md` — dá pra abrir lado a lado com o model correspondente e mostrar que bate campo a campo (ex.: `email String(120) unique` ↔ `app/models/usuario.py` linha 14).
>
> **🌐 No Swagger:** rolar o `/docs` até a parte de **Schemas** e abrir `UsuarioResposta` — a lista de campos é a mesma do dicionário, porque é o mesmo contrato.

---

## 5. Rotas, contratos e status codes

**P: "Quantas rotas têm? Como estão organizadas?"**

R: 22 rotas em 5 grupos (usuarios, eventos, inscricoes, certificados, categorias), todas sob o prefixo `/api/v1`. A lista é exatamente a que aparece no Swagger e no documento 07.

> **📂 No código:** `app/api/v1/api.py` é o agrupador que inclui os 5 routers; cada router declara o próprio prefixo (ex.: `APIRouter(prefix="/inscricoes", tags=["Inscrições"])` no topo de `inscricoes.py`).
>
> **🌐 No Swagger:** contar os endpoints do `/docs` — dá pra ver os 22 agrupados por tag, na mesma ordem da tabela do documento 07.

**P: "Por que o prefixo /api/v1?"**

R: Versionamento na URL. Se um dia a API mudar de forma incompatível, criamos `/api/v2` sem quebrar quem já consome a v1. É um padrão comum de API pública.

> **📂 No código:** `app/main.py` linha 26 — `app.include_router(api_router, prefix="/api/v1")`. O versionamento inteiro do projeto está nessa linha.
>
> **🌐 No Swagger:** apontar qualquer endpoint da listagem — todos começam com `/api/v1/...`.

**P: "Expliquem um contrato completo. Por exemplo, criar evento."**

R: `POST /api/v1/eventos` recebe JSON com titulo, descricao, data_evento, local, capacidade e categoria_id. Antes de executar, o Pydantic valida tipos e obrigatórios (RN07), e o schema rejeita capacidade ≤ 0 (RN05) e data passada (RN06) com 422. Se a `categoria_id` não existe, 400. No sucesso retorna **201** com o evento completo, incluindo id, status `ativo` e data_cadastro.

> **📂 No código:** entrada em `app/schemas/evento.py` (`EventoCriar`, com os validators) e execução em `app/api/v1/routers/eventos.py` linhas 13-33 (checagem de categoria + `Evento(...)` + `db.commit()` + retorno).
>
> **🌐 No Swagger:** a sequência que prova o contrato inteiro:
> 1. `POST /eventos` com o payload do doc 07 → **201** com `"status": "ativo"`;
> 2. repetir sem o `"local"` → **422** (campo obrigatório);
> 3. repetir com `"capacidade": 0` → **422**;
> 4. repetir com `"categoria_id": 999` → **400** "Categoria não existe".

**P: "Por que POST retorna 201 e DELETE 204?"**

R: 201 significa "Created" — nasceu um recurso novo e a resposta traz ele. 204 é "No Content" — deu certo e não há corpo pra devolver (nada mais justo que uma exclusão). Consultas e atualizações devolvem 200 com o objeto.

> **📂 No código:** está explícito na assinatura das rotas: `app/api/v1/routers/usuarios.py` linha 19 — `status_code=status.HTTP_201_CREATED` no POST; linha 70 — `status_code=status.HTTP_204_NO_CONTENT` no DELETE. Igual nos outros 4 routers.
>
> **🌐 No Swagger:** após executar, o código vem no topo da resposta: POST de usuário mostra "201", DELETE mostra "204" e a resposta aparece como "Response body: no content" (sem corpo mesmo).

**P: "Se eu mandar um e-mail inválido, o que acontece?"**

R: 422, e o corpo da resposta aponta o campo e o motivo — validação automática do `EmailStr` do Pydantic. Não precisamos escrever `if` nenhum pra isso.

> **📂 No código:** `app/schemas/usuario.py` linha 8 — `email: EmailStr`. Uma linha de declaração substitui a validação na mão.
>
> **🌐 No Swagger:** `POST /api/v1/usuarios` com `"email": "joao#email.com"` → **422**, e a resposta aponta `"loc": ["body", "email"]` com a mensagem de e-mail inválido.

**P: "Por que vocês não usam envelope tipo {success: true, data: ...}?"**

R: Foi uma decisão consciente, está justificada no documento 07: o `{"detail": "..."}` já é o comportamento nativo do HTTPException do FastAPI, o Swagger mostra exatamente o que cada rota devolve, e o status HTTP já diz se deu certo — envelope duplicaria essa informação. Preferimos um padrão simples, documentado e consistente.

> **📂 No código:** qualquer router mostra o padrão: erros com `raise HTTPException(..., detail="...")` e sucessos devolvendo o objeto do `response_model` direto (ex.: `return nova_inscricao` em `inscricoes.py` linha 57). A justificativa está em `docs/07` seção 7.4.
>
> **🌐 No Swagger:** provocar um erro (`GET /api/v1/usuarios/9999` → `{"detail": "Usuário não encontrado"}`) e um sucesso (`GET /api/v1/usuarios` → o objeto direto, sem envelope) — os dois formatos são esses mesmos em todas as 22 rotas.

**P: "Como funciona a paginação?"**

R: Nas listagens, por query params `skip` e `limit` (padrão 0 e 100), aplicados com `.offset()` e `.limit()` do SQLAlchemy. Ex.: `GET /api/v1/usuarios?skip=0&limit=10`.

> **📂 No código:** `app/api/v1/routers/usuarios.py` linhas 38-40 — `skip: int = 0, limit: int = 100` na assinatura e `.offset(skip).limit(limit)` na consulta. Repetido nas listagens de eventos, inscrições e certificados.
>
> **🌐 No Swagger:** cadastrar 3 usuários e chamar `GET /api/v1/usuarios?limit=2` → só 2 voltam; `GET /api/v1/usuarios?skip=2` → pula os 2 primeiros. Os parâmetros aparecem prontos no próprio Swagger.

**P: "O PUT aceita campos opcionais. Isso não devia ser PATCH?"**

R: Na prática nosso PUT faz atualização parcial — só altera o que vier no corpo. Semânticamente o PATCH seria o verbo mais exato para isso; mantivemos PUT por simplicidade e padronização em todas as entidades, e é uma melhoria fácil de discutir na unidade 2.

> **📂 No código:** `app/schemas/usuario.py` linhas 16-19 — `UsuarioAtualizar` com todos os campos `| None = None`; e `usuarios.py` linhas 57-63 — os `if dados.nome: ...` com o comentário "só altera o que foi mandado no json".
>
> **🌐 No Swagger:** `PUT /api/v1/usuarios/{id}` mandando **só** `{"nome": "João da Silva"}` → 200; depois `GET /api/v1/usuarios/{id}` confirma que e-mail e papel ficaram exatamente como estavam.

---

## 6. Estrutura do projeto e stack

**P: "Por que FastAPI e não Django ou Flask?"**

R: Três motivos: o **Swagger nasce pronto** sem configurar nada (foi essencial pra nossa entrega), a **validação integrada com Pydantic** resolveu metade das nossas regras, e a curva de aprendizado é menor. Django traria um pacote grande (admin, templates) que não usaríamos; Flask exigiria montar validação e documentação na mão.

> **📂 No código:** a prova é o tamanho do `main.py` (~30 linhas incluindo o `/docs`) e o quanto os schemas fazem sozinhos (`app/schemas/evento.py` — 2 validators cobrem RN05 e RN06).
>
> **🌐 No Swagger:** abrir `/docs` e dizer: "essa documentação completa nós não escrevemos uma linha pra ela — o FastAPI gerou dos nossos schemas e routers".

**P: "O que é um ORM?"**

R: Mapeamento objeto-relacional: as tabelas viram classes Python e as linhas viram objetos. Escrevemos `db.query(Evento).filter(...)` em vez de SQL em string. Vantagens: código mais legível, proteção contra SQL injection nos filtros, e facilidade de trocar de banco.

> **📂 No código:** `app/models/` inteiro (as classes = tabelas) e qualquer router (`db.query(...).filter(...)`). Vale citar `app/database/conexao.py` linha 1 — `create_engine` é quem conecta.
>
> **🌐 No Swagger:** conceitual, mas com apoio: executar `GET /api/v1/eventos?status_filtro=ativo` e abrir `eventos.py` linha 40 pra mostrar o `consulta.filter(Evento.status == status_filtro)` — o filtro da query param virou método Python, não string SQL.

**P: "Qual a diferença entre model e schema? Vocês precisam dos dois?"**

R: Precisamos. O **model** (SQLAlchemy) representa a tabela do banco. O **schema** (Pydantic) valida e formata o que entra e sai da API. São propositalmente diferentes: a senha existe no model `Usuario` mas não existe no schema de resposta — é assim que garantimos a RN13 (senha nunca volta).

> **📂 No código:** abrir lado a lado `app/models/usuario.py` (linha 15 — tem `senha`) e `app/schemas/usuario.py` (linhas 22-29 — `UsuarioResposta` sem senha, com o comentário "de propósito").
>
> **🌐 No Swagger:** `POST /api/v1/usuarios` mandando senha → resposta 201 sem senha. O dado passou pelos dois mundos: o model guardou, o schema escondeu.

**P: "Descrevam o caminho de uma requisição."**

R: A requisição entra pelo `main.py`, que montou tudo em `/api/v1` através do `api.py` (agrupador dos routers). Chega no router da entidade, o corpo passa pela validação do schema, o router aplica as regras de negócio consultando o banco pelos models, e a resposta sai no formato do `response_model`.

> **📂 No código:** seguir o caminho com os arquivos abertos nesta ordem: `main.py` (linha 26) → `api.py` → `routers/inscricoes.py` (linha 16) → `schemas/inscricao.py` → `models/inscricao.py` → retorno na linha 57.
>
> **🌐 No Swagger:** executar o `POST /api/v1/inscricoes` e narrar o caminho em voz alta com o código aberto — essa é a resposta que mais impressiona quando demonstrada ao vivo.

**P: "O que é esse Depends(pegar_sessao)?"**

R: Injeção de dependência do FastAPI. Para cada requisição ele cria uma sessão de banco e a fecha no final, sem a gente repetir try/finally em toda rota. Está no `database/conexao.py`.

> **📂 No código:** `app/database/conexao.py` linhas 22-28 — a função com `yield sessao` e `finally: sessao.close()`. Nos routers, o parâmetro `db: Session = Depends(pegar_sessao)` (aparece em todas as 22 rotas).
>
> **🌐 No Swagger:** conceitual — cada execução de rota abre e fecha sua sessão; é por isso que dá pra fazer dezenas de chamadas seguidas no Swagger sem "travar" conexão.

**P: "Onde ficam as configurações?"**

R: Em `app/core/config.py`, com pydantic-settings lendo variáveis de ambiente do `.env` (nome do projeto, `DATABASE_URL`). Config não fica espalhada no código.

> **📂 No código:** `app/core/config.py` inteiro (11 linhas!) — `SettingsConfigDict(env_file=".env")` na linha 10; e o consumo em `conexao.py` linha 6 (`configuracoes.database_url`).
>
> **🌐 No Swagger:** conceitual — sem `.env` algum, a API usa o padrão `sqlite:///./esuda.db` (por isso roda em qualquer máquina só com os 3 comandos).

---

## 7. Banco de dados e migrations

**P: "Por que SQLite?"**

R: É a fase de desenvolvimento e demonstração: não precisa instalar servidor de banco, o arquivo `esuda.db` é criado sozinho, e qualquer pessoa do grupo (e o professor) roda igual. Para produção planejamos PostgreSQL.

> **📂 No código:** `app/core/config.py` linha 8 — o padrão `database_url: str = "sqlite:///./esuda.db"`; e `conexao.py` linhas 9-13 — o `check_same_thread=False` (necessário porque o SQLite não gosta de várias threads, e o FastAPI atende requisições em threads).
>
> **🌐 No Swagger:** depois de subir a API e fazer qualquer cadastro, mostrar o arquivo `esuda.db` na raiz do projeto (dá até pra abrir com DB Browser e ver as 5 tabelas criadas pela migration).

**P: "Quanto custa trocar para PostgreSQL?"**

R: Só mudar a `DATABASE_URL` no `.env` para `postgresql://usuario:senha@localhost/esuda`. O código não muda, porque tudo passa pelo SQLAlchemy e pelo Alembic — foi por isso que escolhemos ORM.

> **📂 No código:** dois pontos: `config.py` linha 6 (comentário "da pra mudar qualquer uma dessas criando um arquivo .env") e `conexao.py` linhas 9-15 — o `if` já trata os dois caminhos (sqlite com `connect_args`, demais bancos direto).
>
> **🌐 No Swagger:** conceitual — nenhum endpoint muda de assinatura; a prova de arquitetura é que nenhuma rota conhece o banco, só a sessão.

**P: "O que é migration? Por que não criar as tabelas na mão?"**

R: Migration é o versionamento do schema do banco: cada mudança vira um arquivo com `upgrade` e `downgrade`. Motivos: o banco evolui de forma controlada, qualquer pessoa sobe o banco no estado certo com um comando (`alembic upgrade head`), e o histórico fica versionado junto do código. Nunca alteramos tabela "no dedo".

> **📂 No código:** `alembic/versions/1e905a380dc1_cria_tabelas_iniciais.py` — dentro tem `def upgrade()` (cria as 5 tabelas) e `def downgrade()` (derruba), e o `alembic/env.py` importa os models pra o autogenerate conhecê-los.
>
> **🌐 No Swagger:** conceitual, mas com terminal: `alembic current` mostra a versão aplicada do banco — prova de que o schema é versionado, não manual.

**P: "Como geraram a migration inicial?"**

R: Com autogenerate: `alembic revision --autogenerate -m "cria tabelas iniciais"` — o Alembic compara os models com o banco e gera as operações. Depois aplicamos com `alembic upgrade head`. O arquivo está em `alembic/versions/`.

> **📂 No código:** comparar o conteúdo do arquivo gerado (`ops.create_table(...)`) com os models — as colunas são um espelho (`app/models/usuario.py` ↔ bloco `create_table('usuarios', ...)` na migration).
>
> **🌐 No Swagger:** não se aplica — é terminal. Ter os comandos prontos no README e, se o professor pedir, rodar `alembic revision --autogenerate -m "teste"` numa base limpa pra ver ele gerar.

**P: "Como rodar o projeto do zero?"**

R: Três passos:
```bash
pip install -r requirements.txt
alembic upgrade head
uvicorn app.main:app --reload
```
E abrir `http://localhost:8000/docs`. O banco `esuda.db` é criado no primeiro comando de migração.

> **📂 No código:** os comandos estão no `README.md` e o `requirements.txt` tem as versões fixadas (fastapi 0.129.0, sqlalchemy 2.0.52, alembic 1.20.0...).
>
> **🌐 No Swagger:** essa pergunta É a demonstração — rodar os 3 comandos na frente, abrir `/docs`, chamar `GET /` ("Esuda Certificados rodando!") e partir pro roteiro da seção 9.

---

## 8. Backlog e critérios de aceitação

**P: "O que é o backlog de vocês?"**

R: A lista priorizada de histórias de usuário do produto — 14 USs, cada uma com prioridade e a unidade em que será feita. Na primeira entrega entram as 10 primeiras (CRUD + regras); login, autorização e testes ficam na segunda.

> **📂 No código:** `docs/10-backlog.md` — a tabela com ID, história, prioridade e entrega; a nota no fim explica o critério do corte.
>
> **🌐 No Swagger:** ligar US ↔ rota na hora: US07 (inscrever) é o `POST /api/v1/inscricoes`, US10 (certificado) é o `POST /api/v1/certificados` — o backlog não é papel, ele vira endpoint.

**P: "O que é uma história de usuário?"**

R: Um requisito escrito no formato "Como [papel], quero [ação], para [valor]" — por exemplo: "Como participante, quero me inscrever em um evento respeitando as vagas". Esse formato mantém o foco no valor pra pessoa usuária, não na tarefa técnica.

> **📂 No código:** `docs/10-backlog.md` US07 — e o "Como participante" da história bate com o `papel` que o banco já guarda (`app/models/usuario.py` linha 16).
>
> **🌐 No Swagger:** executar a US07 inteira: criar usuário com papel `participante`, criar evento, `POST /inscricoes` — e citar que os erros 400/422 são o "respeitando as vagas" da história.

**P: "O que é um critério de aceitação? Dê um exemplo do projeto."**

R: É a condição objetiva pra considerar a história pronta. Exemplo (US07, inscrição): só funciona com usuário e evento existentes (404); duplicada retorna 400; evento lotado 400; evento cancelado 400; evento que já aconteceu 400; sucesso retorna 201 com status `ativa`. Cada critério virou um teste manual no Swagger antes de fechar a entrega.

> **📂 No código:** `docs/11-criterios-de-aceitacao.md` (seção "Inscrição em evento") ↔ `app/api/v1/routers/inscricoes.py` linhas 17-48 — **cada linha de critério tem um `if` correspondente no código**, na mesma ordem.
>
> **🌐 No Swagger:** rodar os 6 critérios da US07 em sequência (é o roteiro da seção 9, passos 6-10) — esse é o melhor momento de dizer "esses critérios eram o nosso roteiro de teste".

**P: "Como vocês testaram?"**

R: Testes de mão de ponta a ponta pelo Swagger, usando os critérios de aceitação como roteiro — passamos por todos os caminhos de erro de cada rota. Testes automatizados com Pytest estão no backlog (US14) para a unidade 2, como combinado em aula.

> **📂 No código:** `docs/11-criterios-de-aceitacao.md` é o roteiro completo; `docs/09-arquitetura-e-stack.md` deixa escrito que Pytest é da unidade 2 (transparência, não omissão).
>
> **🌐 No Swagger:** oferecer demonstrar qualquer critério na hora — "pode escolher uma regra da RN01 a RN15 que eu mostro o teste" (a resposta deles quase sempre cai nas provas da seção 3).

---

## 9. Roteiro de demonstração ao vivo (3 minutos)

Se pedirem para demonstrar, esse fluxo mostra as regras mais fortes na ordem certa. Apoio no código: manter abertos `inscricoes.py` e `certificados.py` — quase todo passo tem um `if` pra apontar.

1. `GET /` — mensagem de que a API está de pé;
2. `POST /api/v1/categorias` — 201;
3. `POST /api/v1/eventos` com **capacidade 2** — 201;
4. `POST /api/v1/eventos` com **data passada** — 422 (validação);
5. `POST /api/v1/usuarios` — 201 (reparar: senha não volta);
6. Inscrever 2 usuários no evento — 201 e 201 (lota);
7. Inscrever um 3º — **400 capacidade**;
8. Inscrever um já inscrito — **400 duplicidade**;
9. `PUT /api/v1/inscricoes/{id}/cancelar` — 200 status `cancelada`;
10. Inscrever o 3º de novo — **201 (vaga liberada pelo cancelamento!)**;
11. `POST /api/v1/certificados` na inscrição ativa — 201 com código;
12. Tentar certificado de novo — **400 duplicado**;
13. `DELETE /api/v1/eventos/{id}` — **400** (tem inscrição, histórico preservado).

> **📂 No código (mapa dos passos):** 4 → `schemas/evento.py` linhas 24-30 · 5 → `schemas/usuario.py` linhas 22-29 · 7 e 8 → `inscricoes.py` linhas 33-48 · 9 → `inscricoes.py` linhas 93-98 · 11 e 12 → `certificados.py` linhas 20-33 · 13 → `eventos.py` linhas 93-99.
>
> **🌐 No Swagger:** é isso mesmo que está descrito acima — ensaiar uma vez com calma antes da defesa pra não errar a ordem dos ids (anotar numa folha: id do evento, dos 3 usuários, das inscrições).

Frase de fechamento: *"Tudo que devolveu 400 ou 422 é regra de negócio nossa respondendo certinho — o sistema não deixa o banco ficar inconsistente."*

---

## 10. Perguntas conceituais rápidas (cola de 1 linha)

| Pergunta | Resposta curta | Como validar na hora |
|----------|----------------|----------------------|
| O que é REST? | Estilo de arquitetura para APIs HTTP: recursos em URLs e verbos GET/POST/PUT/DELETE com significado | 📂 abrir qualquer router e mostrar os 4 verbos; 🌐 listar os endpoints no `/docs` |
| O que é um endpoint? | Uma rota da API — o par método + caminho (ex.: POST /api/v1/usuarios) | 🌐 clicar num endpoint do Swagger e ler "POST /api/v1/usuarios" |
| O que é JSON? | Formato textual de chave/valor para trocar dados entre sistemas | 🌐 mostrar o corpo de qualquer resposta no "Response body" |
| Classes de status code? | 2xx sucesso, 3xx redirecionamento, 4xx erro do cliente, 5xx erro do servidor | 🌐 citar os que já vimos na demo: 200/201/204/400/404/422 |
| O que é Swagger/OpenAPI? | OpenAPI é a especificação da API; Swagger é a interface que a lê — nosso `/docs` | 📂 nada no projeto gera isso à mão; 🌐 a aba "Schemas" do `/docs` mostra a especificação |
| PK vs FK? | Chave primária identifica o registro na própria tabela; estrangeira aponta para a PK de outra | 📂 `app/models/inscricao.py` linhas 12-14 — `id` (PK) e os dois `ForeignKey` |
| Índice unique? | Restrição do banco que impede valor repetido na coluna | 📂 `models/usuario.py` linha 14 (`email ... unique=True`) e `models/certificado.py` linha 13 |
| O que é o .env? | Arquivo de variáveis de ambiente fora do código (config e segredos), lido pelo pydantic-settings | 📂 `app/core/config.py` linha 10 — `env_file=".env"` |
| O que é o uvicorn? | O servidor que executa a aplicação FastAPI (servidor ASGI) | 🖥️ o comando de execução `uvicorn app.main:app --reload` |
| 401 vs 403? | 401 não autenticado; 403 autenticado mas sem permissão (entram na unidade 2) | 📂 `docs/07` tabela 7.3 e matriz do doc 08 |
| O que é ORM? | Biblioteca que mapeia tabelas em classes Python (nosso caso, SQLAlchemy) | 📂 contraste: `models/evento.py` (classe) ↔ `db.query(Evento)` no router |

---

## 11. Se puxarem para a unidade 2 (respostas curtas prontas)

**P: "Como vai ser o login?"**

R: Rota de login recebendo e-mail e senha; confere o hash com passlib (bcrypt) e devolve um token JWT assinado. As rotas protegidas passam a exigir o header `Authorization: Bearer <token>`; sem ele, 401.

> **📂 No código:** já deixamos a semente pronta: `app/api/v1/routers/usuarios.py` linhas 14-16 — a função `gerar_hash_senha` com o comentário "na segunda entrega isso vira bcrypt com jwt". Hoje a senha já é salva como hash (sha256).
>
> **🌐 No Swagger:** mostrar que hoje `POST /api/v1/usuarios` salva hash e não devolve senha (base do login seguro); o `{"detail": ...}` de erro já é o mesmo formato que responderá o 401 futuro.

**P: "E o bloqueio por papel?"**

R: Uma dependência do FastAPI decodifica o token, pega o `papel` e compara com a matriz de permissões (documento 08) antes de executar a rota. Sem permissão, 403. O campo já está salvo no banco desde a primeira entrega — foi por isso que definimos os perfis agora.

> **📂 No código:** a matriz do `docs/08-matriz-de-permissoes.md` e o `papel` no model (`app/models/usuario.py` linha 16). Vale citar o comentário de `eventos.py` linha 101 como o ponto onde a dependência vai entrar.
>
> **🌐 No Swagger:** criar hoje um usuário com `"papel": "admin"` e outro `participante` — os dados da autorização futura já estão lá; falta só o token pra lê-los.

**P: "O que mais muda no código?"**

R: Nada que quebre o que existe: separar regras em `services` e acesso a dados em `repositories` (como comentado em aula), pasta `tests` com Pytest cobrindo os critérios de aceitação, e a consulta de certificado por código (US11).

> **📂 No código:** `docs/09-arquitetura-e-stack.md` seção 9.1 já diz que services/repositories/tests são o próximo passo; `docs/10-backlog.md` US11-US14 lista exatamente o que entra.
>
> **🌐 No Swagger:** US11 terá rota própria (`GET /certificados/codigo/{codigo}` por exemplo); hoje dá pra mostrar o `GET /api/v1/certificados/{id}` que já existe e devolve o código — a base tá pronta.

---

## 12. Dicas para a hora da defesa

- **Responder curto e mostrar**: uma frase de resposta + o bloco 📂/🌐 deste guia vale mais que discurso longo;
- **Não sabe? Admita e ancore**: "isso está no backlog da unidade 2, é a US14" — demonstra domínio do planejamento;
- **Nunca inventar** funcionalidade que não existe no código — professor vai pedir pra mostrar;
- **Deixar pronto**: terminal com os 3 comandos de execução, o Swagger aberto numa aba e no editor os arquivos campeões de citação (`usuarios.py`, `inscricoes.py`, `certificados.py`, `schemas/evento.py`);
- **Ensaiar o roteiro da seção 9** uma vez inteira (anotar os ids numa folha durante a demo);
- **Decorar os números do projeto**: 5 entidades, 22 rotas, 15 regras de negócio, 14 histórias de usuário, 3 perfis.



