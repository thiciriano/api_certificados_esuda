"""exemplos pra preencher no swagger sem digitar na mao"""

EXEMPLO_USUARIO = {
    "usuario_aluno": {
        "summary": "🎓 Aluno (Participante)",
        "description": "Preenche dados de um participante padrão",
        "value": {
            "nome": "Thiago Henrique",
            "email": "thiago@esuda.edu.br",
            "senha": "senhaSegura123",
            "papel": "participante"
        }
    },
    "usuario_prof": {
        "summary": "👨‍🏫 Professor (Organizador)",
        "description": "Preenche dados para perfil organizador",
        "value": {
            "nome": "Victor Oliveira",
            "email": "victor@esuda.edu.br",
            "senha": "senhaSegura123",
            "papel": "organizador"
        }
    }
}

EXEMPLO_USUARIO_UPDATE = {
    "atualizar_nome": {
        "summary": "✏️ Atualizar nome",
        "description": "Manda so o campo que quer mudar",
        "value": {"nome": "Thiago H. Henrique"}
    },
    "atualizar_senha": {
        "summary": "🔑 Trocar senha",
        "description": "Senha nova (mínimo 6 caracteres)",
        "value": {"senha": "novaSenhaSegura123"}
    }
}

EXEMPLO_CATEGORIA = {
    "cat_workshop": {
        "summary": "🏷️ Categoria Workshop",
        "value": {
            "nome": "Workshop Prático",
            "descricao": "Eventos de curta duração com mão na massa"
        }
    }
}

EXEMPLO_CATEGORIA_UPDATE = {
    "atualizar_categoria": {
        "summary": "✏️ Categoria atualizada",
        "description": "Atualiza nome e/ou descricao da categoria",
        "value": {"nome": "Workshop Advanced", "descricao": "Workshop avançado"}
    }
}

EXEMPLO_EVENTO = {
    "evento_fastapi": {
        "summary": "📅 Evento FastAPI",
        "description": "Evento com capacidade para 50 vagas (a data precisa ser futura)",
        "value": {
            "titulo": "Workshop de FastAPI no Backend",
            "descricao": "Aprenda a criar APIs modernas em Python",
            "data_evento": "2026-11-20",
            "local": "Laboratório 3 - Faculdade ESUDA",
            "capacidade": 50,
            "categoria_id": 1
        }
    }
}

EXEMPLO_EVENTO_UPDATE = {
    "atualizar_evento": {
        "summary": "✏️ Evento atualizado",
        "description": "Atualiza título e/ou capacidade do evento",
        "value": {"titulo": "Workshop de FastAPI - Edição 2", "capacidade": 60}
    }
}

EXEMPLO_INSCRICAO = {
    "inscricao_padrao": {
        "summary": "📝 Inscrição no evento",
        "description": "O usuário vem do token, só manda o evento",
        "value": {"evento_id": 1}
    }
}

EXEMPLO_INSCRICAO_STATUS = {
    "cancelar": {
        "summary": "❌ Cancelar inscrição",
        "description": "Cancela a inscrição e devolve a vaga pro evento",
        "value": {"status": "cancelada"}
    },
    "reativar": {
        "summary": "✅ Reativar inscrição",
        "description": "Reativa a inscrição (tira a vaga de volta)",
        "value": {"status": "ativa"}
    }
}

EXEMPLO_CERTIFICADO = {
    "emissao_padrao": {
        "summary": "📜 Emitir certificado",
        "description": "A inscrição precisa existir e estar ativa",
        "value": {"inscricao_id": 1}
    }
}

EXEMPLO_CERTIFICADO_STATUS = {
    "emitir": {
        "summary": "✅ Certificado emitido",
        "description": "Atualiza status para emitido",
        "value": {"status": "emitido"}
    },
    "cancelar": {
        "summary": "❌ Certificado cancelado",
        "description": "Cancela o certificado (não volta de status depois)",
        "value": {"status": "cancelado"}
    }
}
