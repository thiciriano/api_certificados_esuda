"""exemplos pra preencher no swagger sem digitar na mao"""

EXEMPLO_USUARIO = {
    "usuario_aluno": {
        "summary": "🎓 Aluno (Participante)",
        "description": "Preenche dados de um participante padrão para o MVP",
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

EXEMPLO_CATEGORIA = {
    "cat_workshop": {
        "summary": "🏷️ Categoria Workshop",
        "value": {
            "nome": "Workshop Prático",
            "descricao": "Eventos de curta duração com mão na massa"
        }
    }
}

EXEMPLO_EVENTO = {
    "evento_fastapi": {
        "summary": "📅 Evento FastAPI",
        "description": "Evento de teste com capacidade para 50 vagas",
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

EXEMPLO_INSCRICAO = {
    "inscricao_padrao": {
        "summary": "📝 Inscrição de Teste",
        "value": {
            "usuario_id": 1,
            "evento_id": 1
        }
    }
}

EXEMPLO_CERTIFICADO = {
    "emissao_padrao": {
        "summary": "📜 Emitir Certificado",
        "value": {
            "inscricao_id": 1
        }
    }
}
