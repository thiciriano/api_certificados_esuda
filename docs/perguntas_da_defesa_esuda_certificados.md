# Guia de perguntas da defesa — Esuda Certificados (Primeira Entrega)

> Documento de estudo do grupo (não vai junto com a entrega). Cada pergunta é algo que o professor provavelmente vai perguntar com base nas diretrizes da atividade, seguida de uma resposta pronta — curta, do jeito que dá pra falar na hora.

## Como usar

- Ler uma vez inteira antes da defesa e, de preferência, testar no Swagger cada resposta que menciona comportamento;
- As respostas citam os números dos documentos (RN, US, status codes) — mostrar que sabemos onde cada coisa está escrita conta ponto;
- Se aparecer pergunta fora do guia, a estratégia é: responder curto e oferecer mostrar no código (`"posso mostrar onde isso está implementado"`).

---

## 1. Contexto do problema

**P: "Expliquem o problema que o sistema resolve."**

R: Hoje o controle de eventos acadêmicos da Esuda (palestras, workshops, cursos) é feito à mão — lista de presença em papel, planilha e certificado editado um por um. Isso gera erros de contagem de vagas, inscrição duplicada e demora pra emitir certificado. A nossa API centraliza isso: cadastro de eventos com controle de capacidade, inscrição com regras de validação e emissão de certificado com código único.

**P: "Por que API e não um sistema com telas?"**

R: Porque a proposta da disciplina é o backend. A API expõe as regras de negócio pra qualquer frente consumir depois (site, aplicativo, sistema da secretaria). O Swagger em `/docs` já serve de interface pra testar tudo sem construir tela.

**P: "O que é o MVP de vocês?"**

R: O fluxo completo de certificação sem login: cadastrar usuário, criar categoria e evento, inscrever respeitando vagas, cancelar inscrição e emitir certificado com código único. O que ficou de fora e por quê está documentado no backlog (login, permissões e testes automatizados são da unidade 2).

---

## 2. Perfis de usuário e permissões

**P: "Quais são os perfis?"**

R: Três: **Admin** (coordenação/secretaria — gerencia tudo, único que exclui evento), **Organizador** (professor responsável — cria os próprios eventos, vê inscritos, emite certificado) e **Participante** (aluno — consulta evento, se inscreve e cancela a própria inscrição).

**P: "Por que definiram perfil se ainda não existe login?"**

R: Porque o perfil influencia decisões desde já: o campo `papel` já nasce na tabela de usuários com valor padrão `participante`, e a matriz de permissões orientou o desenho das rotas. Se deixássemos pra pensar nisso na unidade 2, teríamos que mexer em banco e cadastro de uma vez.

**P: "Quem pode excluir um evento? Por que o organizador não pode?"**

R: Só o admin (RN15). O organizador que quiser tirar o evento do ar usa o **cancelamento** (muda o status), que preserva o histórico. Exclusão apaga de vez — decisão que ficaria com a coordenação, seguindo a matriz de exemplo passada em aula.

**P: "Como a matriz vai virar código na unidade 2?"**

R: O token JWT vai trazer o papel do usuário; uma dependência do FastAPI pega esse papel e compara com a matriz antes de executar a rota. Se não puder, retorna **403**. As rotas em si não mudam — só recebem a dependência.

---

## 3. Regras de negócio

**P: "Citem três regras de negócio."**

R: Boas opções (todas testadas de ponta a ponta):
1. **RN04** — um evento não pode ultrapassar a capacidade de inscritos ativos (retorna 400);
2. **RN03** — o mesmo usuário não pode ter duas inscrições ativas no mesmo evento (400);
3. **RN11/RN12** — certificado só é emitido para inscrição ativa e só existe um por inscrição (400).

**P: "Onde cada regra é validada: no schema ou na rota? Vocês decidiram como?"**

R: Foi um critério nosso: **schema** quando a regra vale pro campo isolado, sem olhar o banco (RN02 e-mail válido, RN05 capacidade maior que zero, RN06 data não pode ser passada — tudo 422). **Rota** quando a regra depende do estado do banco (duplicidade, lotação, status do evento — tudo 400). Essa separação é a mesma que explica a diferença entre 422 e 400.

**P: "Qual a diferença entre 400 e 422 no projeto de vocês?"**

R: **422** é erro de validação de campo — formato, obrigatório, valor inválido (comportamento padrão do Pydantic no FastAPI). **400** é regra de negócio quebrada — a requisição está bem formada, mas o estado do banco não permite: já inscrito, evento lotado, certificado duplicado. Exemplo: capacidade 0 → 422; inscrever usuário que já está inscrito → 400.

**P: "Por que cancelar inscrição não apaga o registro?"**

R: Histórico. O cancelamento só troca o status para `cancelada` — o registro continua pra auditoria e porque a inscrição faz parte do rastro do evento. A vaga volta pro evento porque a contagem de capacidade só soma inscrições ativas.

**P: "Quando o participante cancela, a vaga volta? Mostrem."**

R: Volta, sim. A contagem no código é `db.query(Inscricao).filter(evento_id == ..., status == "ativa").count()` — cancelada não conta. No Swagger dá pra mostrar: lota o evento, cancela uma inscrição, e a próxima inscrição entra.

**P: "Por que evento com inscrição não pode ser excluído?"**

R: RN14 — preservar o histórico. Se o evento tem inscrição, excluir apagaria o rastro das pessoas que se inscreveram. A rota devolve 400 explicando. Usuário com inscrição e categoria com evento seguem a mesma lógica.

**P: "Como o código do certificado é gerado? Pode repetir?"**

R: Usamos `uuid.uuid4().hex[:8].upper()` — um identificador universal convertido em 8 caracteres hexadecimais maiúsculos, tipo `A3F19C2B`. A chance de colisão é desprezível, e mesmo assim no banco a inscrição é `unique` em certificados, garantindo um certificado por inscrição.

**P: "A senha pode aparecer em alguma resposta?"**

R: Nunca (RN13). O schema de resposta `UsuarioResposta` não tem o campo senha — o FastAPI só serializa o que está declarado no `response_model`. Dá pra mostrar no Swagger: cria usuário e a resposta só tem id, nome, e-mail, papel e data de cadastro.

---

## 4. Modelo de dados, DER e dicionário

**P: "Quais são as entidades?"**

R: Cinco: **usuarios**, **categorias**, **eventos**, **inscricoes** e **certificados**.

**P: "Expliquem o DER de vocês."**

R: Categoria 1:N eventos; usuário 1:N inscrições; evento 1:N inscrições; inscrição 1:0..1 certificado. A inscrição é a tabela que resolve o N:N entre usuário e evento — e ganhou vida própria com data e status.

**P: "Por que inscrição é uma tabela e não só uma relação?"**

R: Porque o N:N entre usuário e evento tem **atributos**: a data em que se inscreveu e o status (ativa/cancelada). N:N com atributo vira entidade associativa. E ela é a base do certificado.

**P: "Por que o certificado liga na inscrição e não direto no usuário?"**

R: Porque o certificado comprova participação **naquele evento específico** — e o par usuário+evento é exatamente a inscrição. Assim ganhamos de graça a regra de um certificado por participação (unique em `inscricao_id`).

**P: "O que é chave estrangeira? Onde tem no projeto?"**

R: É a coluna que aponta para a chave primária de outra tabela, garantindo a integridade do relacionamento. No projeto: `eventos.categoria_id` → `categorias.id`; `inscricoes.usuario_id` e `inscricoes.evento_id`; `certificados.inscricao_id`. Tentar inscrever com `usuario_id` inexistente devolve 404.

**P: "O que tem no dicionário de dados?"**

R: Uma tabela por entidade com: campo, tipo, obrigatório ou não, valor padrão, restrições (PK, FK, unique) e descrição em português. Ele é a tradução campo a campo do DER.

---

## 5. Rotas, contratos e status codes

**P: "Quantas rotas têm? Como estão organizadas?"**

R: 22 rotas em 5 grupos (usuarios, eventos, inscricoes, certificados, categorias), todas sob o prefixo `/api/v1`. A lista é exatamente a que aparece no Swagger e no documento 07.

**P: "Por que o prefixo /api/v1?"**

R: Versionamento na URL. Se um dia a API mudar de forma incompatível, criamos `/api/v2` sem quebrar quem já consome a v1. É um padrão comum de API pública.

**P: "Expliquem um contrato completo. Por exemplo, criar evento."**

R: `POST /api/v1/eventos` recebe JSON com titulo, descricao, data_evento, local, capacidade e categoria_id. Antes de executar, o Pydantic valida tipos e obrigatórios (RN07), e o schema rejeita capacidade ≤ 0 (RN05) e data passada (RN06) com 422. Se a `categoria_id` não existe, 400. No sucesso retorna **201** com o evento completo, incluindo id, status `ativo` e data_cadastro.

**P: "Por que POST retorna 201 e DELETE 204?"**

R: 201 significa "Created" — nasceu um recurso novo e a resposta traz ele. 204 é "No Content" — deu certo e não há corpo pra devolver (nada mais justo que uma exclusão). Consultas e atualizações devolvem 200 com o objeto.

**P: "Se eu mandar um e-mail inválido, o que acontece?"**

R: 422, e o corpo da resposta aponta o campo e o motivo — validação automática do `EmailStr` do Pydantic. Não precisamos escrever `if` nenhum pra isso.

**P: "Por que vocês não usam envelope tipo {success: true, data: ...}?"**

R: Foi uma decisão consciente, está justificada no documento 07: o `{"detail": "..."}` já é o comportamento nativo do HTTPException do FastAPI, o Swagger mostra exatamente o que cada rota devolve, e o status HTTP já diz se deu certo — envelope duplicaria essa informação. Preferimos um padrão simples, documentado e consistente.

**P: "Como funciona a paginação?"**

R: Nas listagens, por query params `skip` e `limit` (padrão 0 e 100), aplicados com `.offset()` e `.limit()` do SQLAlchemy. Ex.: `GET /api/v1/usuarios?skip=0&limit=10`.

**P: "O PUT aceita campos opcionais. Isso não devia ser PATCH?"**

R: Na prática nosso PUT faz atualização parcial — só altera o que vier no corpo. Semânticamente o PATCH seria o verbo mais exato para isso; mantivemos PUT por simplicidade e padronização em todas as entidades, e é uma melhoria fácil de discutir na unidade 2.

---

## 6. Estrutura do projeto e stack

**P: "Por que FastAPI e não Django ou Flask?"**

R: Três motivos: o **Swagger nasce pronto** sem configurar nada (foi essencial pra nossa entrega), a **validação integrada com Pydantic** resolveu metade das nossas regras, e a curva de aprendizado é menor. Django traria um pacote grande (admin, templates) que não usaríamos; Flask exigiria montar validação e documentação na mão.

**P: "O que é um ORM?"**

R: Mapeamento objeto-relacional: as tabelas viram classes Python e as linhas viram objetos. Escrevemos `db.query(Evento).filter(...)` em vez de SQL em string. Vantagens: código mais legível, proteção contra SQL injection nos filtros, e facilidade de trocar de banco.

**P: "Qual a diferença entre model e schema? Vocês precisam dos dois?"**

R: Precisamos. O **model** (SQLAlchemy) representa a tabela do banco. O **schema** (Pydantic) valida e formata o que entra e sai da API. São propositalmente diferentes: a senha existe no model `Usuario` mas não existe no schema de resposta — é assim que garantimos a RN13 (senha nunca volta).

**P: "Descrevam o caminho de uma requisição."**

R: A requisição entra pelo `main.py`, que montou tudo em `/api/v1` através do `api.py` (agrupador dos routers). Chega no router da entidade, o corpo passa pela validação do schema, o router aplica as regras de negócio consultando o banco pelos models, e a resposta sai no formato do `response_model`.

**P: "O que é esse Depends(pegar_sessao)?"**

R: Injeção de dependência do FastAPI. Para cada requisição ele cria uma sessão de banco e a fecha no final, sem a gente repetir try/finally em toda rota. Está no `database/conexao.py`.

**P: "Onde ficam as configurações?"**

R: Em `app/core/config.py`, com pydantic-settings lendo variáveis de ambiente do `.env` (nome do projeto, `DATABASE_URL`). Config não fica espalhada no código.

---

## 7. Banco de dados e migrations

**P: "Por que SQLite?"**

R: É a fase de desenvolvimento e demonstração: não precisa instalar servidor de banco, o arquivo `esuda.db` é criado sozinho, e qualquer pessoa do grupo (e o professor) roda igual. Para produção planejamos PostgreSQL.

**P: "Quanto custa trocar para PostgreSQL?"**

R: Só mudar a `DATABASE_URL` no `.env` para `postgresql://usuario:senha@localhost/esuda`. O código não muda, porque tudo passa pelo SQLAlchemy e pelo Alembic — foi por isso que escolhemos ORM.

**P: "O que é migration? Por que não criar as tabelas na mão?"**

R: Migration é o versionamento do schema do banco: cada mudança vira um arquivo com `upgrade` e `downgrade`. Motivos: o banco evolui de forma controlada, qualquer pessoa sobe o banco no estado certo com um comando (`alembic upgrade head`), e o histórico fica versionado junto do código. Nunca alteramos tabela "no dedo".

**P: "Como geraram a migration inicial?"**

R: Com autogenerate: `alembic revision --autogenerate -m "cria tabelas iniciais"` — o Alembic compara os models com o banco e gera as operações. Depois aplicamos com `alembic upgrade head`. O arquivo está em `alembic/versions/`.

**P: "Como rodar o projeto do zero?"**

R: Três passos:
```bash
pip install -r requirements.txt
alembic upgrade head
uvicorn app.main:app --reload
```
E abrir `http://localhost:8000/docs`. O banco `esuda.db` é criado no primeiro comando de migração.

---

## 8. Backlog e critérios de aceitação

**P: "O que é o backlog de vocês?"**

R: A lista priorizada de histórias de usuário do produto — 14 USs, cada uma com prioridade e a unidade em que será feita. Na primeira entrega entram as 10 primeiras (CRUD + regras); login, autorização e testes ficam na segunda.

**P: "O que é uma história de usuário?"**

R: Um requisito escrito no formato "Como [papel], quero [ação], para [valor]" — por exemplo: "Como participante, quero me inscrever em um evento respeitando as vagas". Esse formato mantém o foco no valor pra pessoa usuária, não na tarefa técnica.

**P: "O que é um critério de aceitação? Dê um exemplo do projeto."**

R: É a condição objetiva pra considerar a história pronta. Exemplo (US07, inscrição): só funciona com usuário e evento existentes (404); duplicada retorna 400; evento lotado 400; evento cancelado 400; evento que já aconteceu 400; sucesso retorna 201 com status `ativa`. Cada critério virou um teste manual no Swagger antes de fechar a entrega.

**P: "Como vocês testaram?"**

R: Testes de mão de ponta a ponta pelo Swagger, usando os critérios de aceitação como roteiro — passamos por todos os caminhos de erro de cada rota. Testes automatizados com Pytest estão no backlog (US14) para a unidade 2, como combinado em aula.

---

## 9. Roteiro de demonstração ao vivo (3 minutos)

Se pedirem para demonstrar, esse fluxo mostra as regras mais fortes na ordem certa:

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

Frase de fechamento: *"Tudo que devolveu 400 ou 422 é regra de negócio nossa respondendo certinho — o sistema não deixa o banco ficar inconsistente."*

---

## 10. Perguntas conceituais rápidas (cola de 1 linha)

| Pergunta | Resposta curta |
|----------|----------------|
| O que é REST? | Estilo de arquitetura para APIs HTTP: recursos em URLs e verbos GET/POST/PUT/DELETE com significado |
| O que é um endpoint? | Uma rota da API — o par método + caminho (ex.: POST /api/v1/usuarios) |
| O que é JSON? | Formato textual de chave/valor para trocar dados entre sistemas |
| Classes de status code? | 2xx sucesso, 3xx redirecionamento, 4xx erro do cliente, 5xx erro do servidor |
| O que é Swagger/OpenAPI? | OpenAPI é a especificação da API; Swagger é a interface que a lê — nosso `/docs` |
| PK vs FK? | Chave primária identifica o registro na própria tabela; estrangeira aponta para a PK de outra |
| Índice unique? | Restrição do banco que impede valor repetido na coluna (nosso `email`) |
| O que é o .env? | Arquivo de variáveis de ambiente fora do código (config e segredos), lido pelo pydantic-settings |
| O que é o uvicorn? | O servidor que executa a aplicação FastAPI (servidor ASGI) |
| 401 vs 403? | 401 não autenticado; 403 autenticado mas sem permissão (entram na unidade 2) |
| O que é ORM? | Biblioteca que mapeia tabelas em classes Python (nosso caso, SQLAlchemy) |

---

## 11. Se puxarem para a unidade 2 (respostas curtas prontas)

**P: "Como vai ser o login?"**

R: Rota de login recebendo e-mail e senha; confere o hash com passlib (bcrypt) e devolve um token JWT assinado. As rotas protegidas passam a exigir o header `Authorization: Bearer <token>`; sem ele, 401.

**P: "E o bloqueio por papel?"**

R: Uma dependência do FastAPI decodifica o token, pega o `papel` e compara com a matriz de permissões (documento 08) antes de executar a rota. Sem permissão, 403. O campo já está salvo no banco desde a primeira entrega — foi por isso que definimos os perfis agora.

**P: "O que mais muda no código?"**

R: Nada que quebre o que existe: separar regras em `services` e acesso a dados em `repositories` (como comentado em aula), pasta `tests` com Pytest cobrindo os critérios de aceitação, e a consulta de certificado por código (US11).

---

## 12. Dicas para a hora da defesa

- **Responder curto e mostrar**: uma frase de resposta + "posso mostrar no Swagger/código" vale mais que discurso longo;
- **Não sabe? Admita e ancore**: "isso está no backlog da unidade 2, é a US14" — demonstra domínio do planejamento;
- **Nunca inventar** funcionalidade que não existe no código — professor vai pedir pra mostrar;
- **Deixar pronto**: terminal com os 3 comandos de execução e o Swagger aberto numa aba;
- **Decorar os números do projeto**: 5 entidades, 22 rotas, 15 regras de negócio, 14 histórias de usuário, 3 perfis.
