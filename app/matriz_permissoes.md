# Matriz de Permissões - Esuda Certificados

| Funcionalidade | Admin | Organizador | Participante |
|----------------|------:|------------:|-------------:|
| Criar usuário | Sim | Não | Não |
| Excluir usuário | Sim | Não | Não |
| Criar evento | Sim | Sim | Não |
| Excluir evento | Sim | Não | Não |
| Listar eventos | Sim | Sim | Sim |
| Inscrever-se em evento | Não | Não | Sim |
| Cancelar inscrição | Sim | Sim | Apenas própria |
| Listar inscritos | Sim | Sim | Não |
| Emitir certificado | Sim | Sim | Não |
| Consultar certificado | Sim | Sim | Próprio apenas |

**Legenda:**
- Sim: Permitido para o perfil
- Não: Negado para o perfil
- Apenas própria: Apenas o proprietário da inscrição

**Nota:** Esta matriz será utilizada na segunda unidade para implementação de JWT e controle de acesso baseado em perfil.
