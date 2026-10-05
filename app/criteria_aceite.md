# Critérios de Aceitação - Esuda Certificados

## Cadastro de Usuário

- [ ] Deve exigir nome, e-mail e senha
- [ ] Não deve permitir e-mail duplicado no banco
- [ ] A senha não deve ser retornada na resposta (hash only)
- [ ] Deve retornar status 201 ao cadasrar com sucesso
- [ ] Devolver erro 400 ao tentar cadastrar e-mail inválido
- [ ] Devolver erro 400 ao tentar cadastrar com campos obrigatórios vazios

## Criar Evento

- [ ] Deve validar se categoria existe antes de criar evento
- [ ] Título do evento deve ser único
- [ ] Data do evento não pode ser passada (deve ser futura)
- [ ] Capacidade deve ser maior que zero
- [ ] Devolver status 201 ao criar com sucesso
- [ ] Devolver erro 400 se capacidade inválida
- [ ] Devolver erro 404 se categoria não encontrada

## Inscrever-se em Evento

- [ ] Usuário deve existir no sistema
- [ ] Evento deve existir e estar ativo
- [ ] Evento deve ter vagas disponíveis
- [ ] Usuário não pode já estar inscrito no evento
- [ ] Deve decrementar vagas_disponíveis ao inserir inscrição
- [ ] Devolver status 201 ao sucesso
- [ ] Devolver erro 400 se sem vagas
- [ ] Devolver erro 404 se usuário/evento não encontrado

## Emitir Certificado

- [ ] Inscrição deve existir no banco
- [ ] Certificado não pode já ter sido emitido para esta inscrição
- [ ] Usuário do evento deve ser participante (não admin)
- [ ] Deve gerar código_certificacao unico (formato ESUDA-{id}-{inscricao_id})
- [ ] Devolver status 201 ao sucesso
- [ ] Devolver erro 404 se inscrição não encontrada
- [ ] Devolver erro 400 se certificado já emitido

## Login/Autenticação (JWT)

- [ ] Deve gerar token JWT com username e papel
- [ ] Token deve expirar após X minutos
- [ ] Token inválido deve retornar 401
- [ ] Rotas protegidas devem exigir token de autorização
