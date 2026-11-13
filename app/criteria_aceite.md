# Critérios de Aceitação - Esuda Certificados (2AV)

## Cadastro de Usuário

- [x] Deve exigir nome, e-mail e senha
- [x] Não deve permitir e-mail duplicado no banco
- [x] A senha não deve ser retornada na resposta (hash only)
- [x] Deve retornar status 201 ao cadastrar com sucesso
- [x] Devolver erro 400 ao tentar cadastrar e-mail inválido (422 do schema EmailStr)
- [x] Devolver erro 400 ao tentar cadastrar com campos obrigatórios vazios (422 do schema)

## Criar Evento

- [x] Deve validar se categoria existe antes de criar evento (404)
- [x] Título do evento deve ser único (400)
- [x] Data do evento não pode ser passada (deve ser futura) (400)
- [x] Capacidade deve ser maior que zero (422)
- [x] Deve retornar status 201 ao criar com sucesso
- [x] Exigir perfil de administrador ou organizador (403)

## Inscrever-se em Evento

- [x] Usuário vem do token (não do body) — não inscreve terceiros
- [x] Evento deve existir (404) e estar ativo (400)
- [x] Evento deve ter vagas disponíveis (400)
- [x] Usuário não pode já estar inscrito no evento (400)
- [x] Deve decrementar `vagas_disponiveis` ao inscrever
- [x] Devolver status 201 ao sucesso
- [x] Participante só cancela a própria inscrição (403)

## Emitir Certificado

- [x] Inscrição deve existir no banco (404)
- [x] Inscrição deve estar ativa (400)
- [x] Certificado não pode já ter sido emitido para esta inscrição (400)
- [x] Deve gerar `codigo_certificacao` único (formato ESUDA-{inscricao_id}-{aleatorio})
- [x] Devolver status 201 ao sucesso
- [x] Somente organizador/admin pode emitir (403)

## Login/Autenticação (JWT)

- [x] Deve gerar token JWT com o id do usuário (`sub`) e papel
- [x] Token expira após ACCESS_TOKEN_EXPIRE_MINUTES
- [x] Token inválido ou expirado retorna 401
- [x] Rotas protegidas exigem Authorization Bearer
- [x] Senha incorreta retorna 401
- [x] Usuário inativo não autentica (403)
