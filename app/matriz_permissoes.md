# Matriz de Permissões - Esuda Certificados (2AV)

A coluna **Token** indica quais endpoints exigem `Authorization: Bearer <JWT>`. A coluna **Verificação aplicada** mostra onde a regra é executada no back-end (`app/core/deps.py`, `app/core/permissions.py` ou na rota).

| Funcionalidade | Endpoint | Token | Admin | Organizador | Participante | Verificação aplicada |
|----------------|----------|:-----:|------:|------------:|-------------:|----------------------|
| Cadastrar conta | `POST /api/v1/usuarios` | Opcional | Sim (qualquer papel) | Sim (auto-cadastro) | Sim (auto-cadastro) | `get_user_optional`: papel `admin` só se o token já for admin (R14) |
| Login | `POST /api/v1/auth/login` | Público | Sim | Sim | Sim | bcrypt + JWT com expiração |
| Ver usuário autenticado | `GET /api/v1/usuarios/me` | **Bearer** | Sim | Sim | Sim | `get_current_active_user` (401 sem token válido) |
| Listar usuários | `GET /api/v1/usuarios` | **Bearer** | Sim | Não | Não | `precisa_de_permissao("pode_gerenciar_usuarios")` |
| Atualizar usuário | `PUT /api/v1/usuarios/{id}` | **Bearer** | Sim (qualquer) | Apenas o próprio (sem mudar papel) | Apenas o próprio (sem mudar papel) | `eh_dono_ou_admin` + papel só muda com `admin` |
| Excluir usuário | `DELETE /api/v1/usuarios/{id}` | **Bearer** | Sim | Não | Não | `precisa_de_permissao("pode_gerenciar_usuarios")` |
| Listar eventos | `GET /api/v1/eventos` | Público | Sim | Sim | Sim | Consulta aberta |
| Ver evento | `GET /api/v1/eventos/{id}` | Público | Sim | Sim | Sim | Consulta aberta (404 se não existir) |
| Criar evento | `POST /api/v1/eventos` | **Bearer** | Sim | Sim | Não | `precisa_de_permissao("pode_criar_evento")` |
| Editar evento | `PUT /api/v1/eventos/{id}` | **Bearer** | Sim (qualquer) | Apenas os que criou | Não | `pode_editar_evento` + `eh_dono_ou_admin(criado_por)` |
| Excluir evento | `DELETE /api/v1/eventos/{id}` | **Bearer** | Sim | Não | Não | `precisa_de_permissao("pode_excluir_evento")` |
| Inscrever-se | `POST /api/v1/inscricoes` | **Bearer** | Não | Não | Sim (em si mesmo) | `get_current_active_user` + papel `participante`; `usuario_id` vem do token |
| Listar inscrições | `GET /api/v1/inscricoes` | **Bearer** | Sim (todas) | Conforme vínculo (eventos que criou) | Apenas as próprias | Filtro por `criado_por` / `usuario_id` do token |
| Cancelar/reativar inscrição | `PUT /api/v1/inscricoes/{id}` | **Bearer** | Sim (qualquer) | Conforme vínculo (eventos que criou) | Apenas a própria | `eh_dono_ou_admin` ou `_evento_do_organizador` |
| Excluir inscrição | `DELETE /api/v1/inscricoes/{id}` | **Bearer** | Sim | Não | Não | `precisa_de_permissao("pode_excluir_inscricao")` |
| Emitir certificado | `POST /api/v1/certificados` | **Bearer** | Sim | Sim | Não | `precisa_de_permissao("pode_emitir_certificado")` + inscrição ativa |
| Listar certificados | `GET /api/v1/certificados` | **Bearer** | Sim (todos) | Conforme vínculo (eventos que criou) | Apenas os próprios | Filtro por `criado_por` / `usuario_id` do token |
| Atualizar certificado | `PUT /api/v1/certificados/{id}` | **Bearer** | Sim | Sim | Não | `precisa_de_permissao("pode_emitir_certificado")` + regra de status terminal |
| Excluir certificado | `DELETE /api/v1/certificados/{id}` | **Bearer** | Sim | Não | Não | `precisa_de_permissao("pode_excluir_certificado")` |
| Criar/editar/excluir categoria | `POST/PUT/DELETE /api/v1/categorias` | **Bearer** | Sim | Sim | Não | `precisa_de_permissao("pode_gerenciar_categoria")` |
| Listar categorias | `GET /api/v1/categorias` | Público | Sim | Sim | Sim | Consulta aberta |

**Legenda:**
- **Sim**: permitido para o perfil.
- **Não**: retorno `403 Forbidden` (usuário autenticado sem permissão).
- **Bearer**: endpoint protegido por JWT; sem token ou com token inválido/expirado retorna `401 Unauthorized`.
- **Opcional**: a rota funciona sem token, mas o token (quando enviado) é usado na decisão de permissão.
- **Público**: consulta aberta, não exige token.
- **Apenas o próprio / Apenas as próprias**: comparação entre o `sub` do token e o dono do recurso; `403` se não for o dono (e `404` se o recurso não existir).
- **Conforme vínculo**: organizador acessa só recursos de eventos com `criado_por` igual ao próprio id.

**Endpoints protegidos (resumo por verificação):**

| Verificação (`PERFIS` / dependência) | Endpoints protegidos |
|--------------------------------------|----------------------|
| `pode_gerenciar_usuarios` | `GET /usuarios`, `DELETE /usuarios/{id}` |
| `pode_criar_evento` | `POST /eventos` |
| `pode_editar_evento` + dono | `PUT /eventos/{id}` |
| `pode_excluir_evento` | `DELETE /eventos/{id}` |
| `pode_excluir_inscricao` | `DELETE /inscricoes/{id}` |
| `pode_emitir_certificado` | `POST /certificados`, `PUT /certificados/{id}` |
| `pode_excluir_certificado` | `DELETE /certificados/{id}` |
| `pode_gerenciar_categoria` | `POST/PUT/DELETE /categorias` |
| `get_current_active_user` (qualquer perfil ativo) | `GET /usuarios/me`, `GET/POST/PUT /inscricoes`, `GET /certificados` |
| `eh_dono_ou_admin` / vínculo `criado_por` | `PUT /usuarios/{id}`, `PUT /eventos/{id}`, `PUT /inscricoes/{id}`, listagens filtradas |

**Comportamento de erro:**
- Sem token, token inválido ou expirado → `401 Unauthorized`.
- Logado sem a permissão da operação (ou tentando acessar recurso de outro usuário) → `403 Forbidden`.
- Recurso inexistente → `404 Not Found`.

**Implementação e evidências:**
- Perfis e flags: `app/core/permissions.py` (`PERFIS`, `eh_dono_ou_admin`).
- Dependências: `app/core/deps.py` (`get_current_user`, `get_current_active_user`, `precisa_de_permissao`).
- Requisições reais demonstrando acessos permitidos e negados: `docs/evidencias/requisicoes-acesso.txt`.
