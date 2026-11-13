# Regras de Negócio do Sistema Esuda Certificados

## Regras da Primeira Unidade (revisadas na 2AV)

| ID | Regra de Negócio | Descrição | Endpoint | Status 2AV |
|----|------------------|-----------|----------|------------|
| R1 | E-mail único | Não pode existir dois usuários com o mesmo e-mail | `POST /api/v1/usuarios` | ✅ Implementada |
| R2 | Título único de evento | Não pode existir dois eventos com o mesmo título | `POST/PUT /api/v1/eventos` | ✅ Implementada |
| R3 | Capacidade máxima | Inscrição não deixa o evento passar da capacidade | `POST /api/v1/inscricoes` | ✅ Implementada (corrige: decrementava `capacidade` em vez de `vagas_disponiveis`) |
| R4 | Inscrição duplicada | Usuário não pode se inscrever duas vezes no mesmo evento | `POST /api/v1/inscricoes` | ✅ Implementada |
| R5 | Data do evento | Não é permitido cadastrar evento com data passada | `POST/PUT /api/v1/eventos` | ✅ Implementada (era pendente na 1AV) |
| R6 | Vagas disponíveis | Inscrição só possível se `vagas_disponiveis > 0` | `POST /api/v1/inscricoes` | ✅ Implementada |
| R7 | Cancelamento próprio | Participante só pode cancelar sua própria inscrição | `PUT /api/v1/inscricoes/{id}` | ✅ Implementada (era pendente na 1AV; agora compara o dono com o token) |
| R8 | Emissão de certificado | Certificado só pode ser emitido para inscrição **ativa** | `POST /api/v1/certificados` | ✅ Implementada (agora valida o status da inscrição) |
| R9 | Admin exclusão | Apenas admin pode excluir eventos | `DELETE /api/v1/eventos/{id}` | ✅ Implementada (era pendente na 1AV; agora é enforced no back-end) |
| R10 | Único certificado | Cada inscrição gera no máximo um certificado | `POST /api/v1/certificados` | ✅ Implementada |

## Regras novas da Segunda Unidade

| ID | Regra de Negócio | Descrição | Endpoint | Status |
|----|------------------|-----------|----------|--------|
| R11 | Categoria com eventos | Categoria com evento vinculado não pode ser excluída | `DELETE /api/v1/categorias/{id}` | ✅ Implementada |
| R12 | Capacidade vs inscritos | Capacidade não pode ficar menor que o nº de inscrições ativas | `PUT /api/v1/eventos/{id}` | ✅ Implementada |
| R13 | Certificado terminal | Certificado cancelado não volta de status | `PUT /api/v1/certificados/{id}` | ✅ Implementada |
| R14 | Sem promoção de papel | Só admin cria/edita usuários com papel admin | `POST/PUT /api/v1/usuarios` | ✅ Implementada |
| R15 | Evento inativo | Evento cancelado/finalizado não aceita inscrição | `POST /api/v1/inscricoes` | ✅ Implementada |
| R16 | Senha em hash | Senhas são guardadas com bcrypt, nunca em texto puro; nenhuma resposta devolve senha/hash | `POST /api/v1/usuarios`, `POST /api/v1/auth/login` | ✅ Implementada |
