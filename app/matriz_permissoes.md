# Matriz de Permissões - Esuda Certificados (2AV)

| Funcionalidade | Endpoint | Admin | Organizador | Participante |
|----------------|----------|------:|------------:|-------------:|
| Cadastrar conta | `POST /api/v1/usuarios` | Sim (qualquer papel) | Sim (auto-cadastro) | Sim (auto-cadastro) |
| Login | `POST /api/v1/auth/login` | Sim | Sim | Sim |
| Ver usuário autenticado | `GET /api/v1/usuarios/me` | Sim | Sim | Sim |
| Listar usuários | `GET /api/v1/usuarios` | Sim | Não | Não |
| Atualizar usuário | `PUT /api/v1/usuarios/{id}` | Sim (qualquer) | Apenas o próprio (sem mudar papel) | Apenas o próprio (sem mudar papel) |
| Excluir usuário | `DELETE /api/v1/usuarios/{id}` | Sim | Não | Não |
| Listar eventos | `GET /api/v1/eventos` | Sim (aberto) | Sim (aberto) | Sim (aberto) |
| Ver evento | `GET /api/v1/eventos/{id}` | Sim (aberto) | Sim (aberto) | Sim (aberto) |
| Criar evento | `POST /api/v1/eventos` | Sim | Sim | Não |
| Editar evento | `PUT /api/v1/eventos/{id}` | Sim (qualquer) | Apenas os que criou | Não |
| Excluir evento | `DELETE /api/v1/eventos/{id}` | Sim | Não | Não |
| Inscrever-se | `POST /api/v1/inscricoes` | Não | Não | Sim (em si mesmo) |
| Listar inscrições | `GET /api/v1/inscricoes` | Sim (todas) | Conforme vínculo (eventos que criou) | Apenas as próprias |
| Cancelar/reativar inscrição | `PUT /api/v1/inscricoes/{id}` | Sim (qualquer) | Conforme vínculo (eventos que criou) | Apenas a própria |
| Excluir inscrição | `DELETE /api/v1/inscricoes/{id}` | Sim | Não | Não |
| Emitir certificado | `POST /api/v1/certificados` | Sim | Sim | Não |
| Listar certificados | `GET /api/v1/certificados` | Sim (todos) | Conforme vínculo (eventos que criou) | Apenas os próprios |
| Atualizar certificado | `PUT /api/v1/certificados/{id}` | Sim | Sim | Não |
| Excluir certificado | `DELETE /api/v1/certificados/{id}` | Sim | Não | Não |
| Criar/editar/excluir categoria | `POST/PUT/DELETE /api/v1/categorias` | Sim | Sim | Não |
| Listar categorias | `GET /api/v1/categorias` | Sim (aberto) | Sim (aberto) | Sim (aberto) |

**Legenda:**
- **Sim**: Permitido para o perfil
- **Não**: Retorno `403 Forbidden`
- **Apenas o próprio / Apenas as próprias**: Comparação entre o usuário do token (`sub`) e o dono do recurso, retorno `403` se não for o dono (e `404` se o recurso não existir)
- **Conforme vínculo**: Organizador acessa só recursos de eventos com `criado_por` igual ao próprio id
- **(aberto)**: Consulta pública, não exige token

**Comportamento:**
- Sem token ou token inválido/expirado → `401 Unauthorized`
- Logado sem o perfil da operação → `403 Forbidden`
- Recurso inexistente → `404 Not Found`

**Nota:** Os perfis e permissões estão implementados em `app/core/permissions.py` (PERFIS) e aplicados nas rotas por `app/core/deps.py` (`precisa_de_permissao`, `get_current_active_user`).
