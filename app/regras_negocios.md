# Regras de Negócio do Sistema Esuda Certificados

| ID | Regra de Negócio | Descrição | Status |
|----|------------------|-----------|--------|
| R1 | E-mail único | Não pode existir dois usuários com o mesmo e-mail | ✅ Implementada |
| R2 | Título único de evento | Não pode existir dois eventos com o mesmo título | ✅ Implementada |
| R3 | Capacidade máxima | Evento não pode ter vagas além da capacidade definida | ✅ Implementada |
| R4 | Inscrição duplicada | Usuário não pode se inscrever duas vezes no mesmo evento | ✅ Implementada |
| R5 | Data do evento | Não é permitido cadastrar evento com data passada | ⚠️ Pendente validação |
| R6 | Vagas disponíveis | Inscrição só possível se vagas_disponíveis > 0 | ✅ Implementada |
| R7 | Cancelamento próprio | Participante só pode cancelar sua própria inscrição | ⚠️ Pendente implementação |
| R8 | Emissão de certificado | Certificado só pode ser emitido para inscrito no evento | ✅ Implementada |
| R9 | Admin exclusão | Apenas admin pode excluir eventos | ⚠️ Pendente matriz de permissões |
| R10 | Único certificado | Cada inscrição gera no máximo um certificado | ⚠️ Pendente documentação |
