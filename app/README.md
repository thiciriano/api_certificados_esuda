# Contexto do Problema

A instituição precisa de uma API para gerenciar eventos acadêmicos, inscrições, usuários e emissão de certificados, substituindo controles manuais por uma solução centralizada.

**Perguntas-chave:**
- **Qual problema o sistema resolve?** Substitui controles manuais (planilhas, papel) por uma solução digital centralizada para gerenciar eventos acadêmicos, inscrições e certificados.
- **Quem vai usar?** Administradores (gerenciarem usuários, eventos e inscrições), Organizadores (criarem e gerenciarem eventos) e Participantes (consultem eventos e realizem inscrições).
- **Qual o objetivo da API?** Fornecer endpoints RESTful para cadastro, consulta, atualização e exclusão de usuários, eventos, inscrições e certificados, com controle de acesso adequado.
- **Qual o escopo da primeira versão?** API para gerenciamento básico de usuários, categorias, eventos, inscrições e emissão de certificados para participantes inscritos. Controle de autorização será implementado na segunda unidade.

**Objetivos não-funcionais:**
- API responsiva e disponível
- Validação de dados em tempo real
- Documentação automática via Swagger/OpenAPI
- Banco de dados relacional com integridade referencial
