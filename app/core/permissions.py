"""o que cada papel pode fazer (matriz de permissoes da 2AV)"""


PERFIS = {
    "admin": {
        "pode_criar_evento": True,
        "pode_editar_evento": True,
        "pode_excluir_evento": True,
        "pode_gerenciar_categoria": True,
        "pode_emitir_certificado": True,
        "pode_excluir_certificado": True,
        "pode_excluir_inscricao": True,
        "pode_gerenciar_usuarios": True,
    },
    "organizador": {
        "pode_criar_evento": True,
        "pode_editar_evento": True,
        "pode_excluir_evento": False,
        "pode_gerenciar_categoria": True,
        "pode_emitir_certificado": True,
        "pode_excluir_certificado": False,
        "pode_excluir_inscricao": False,
        "pode_gerenciar_usuarios": False,
    },
    "participante": {
        "pode_criar_evento": False,
        "pode_editar_evento": False,
        "pode_excluir_evento": False,
        "pode_gerenciar_categoria": False,
        "pode_emitir_certificado": False,
        "pode_excluir_certificado": False,
        "pode_excluir_inscricao": False,
        "pode_gerenciar_usuarios": False,
    },
}


def eh_dono_ou_admin(usuario, dono_id: int) -> bool:
    """admin mexe em tudo, o resto so no que e dele"""
    return usuario.papel == "admin" or usuario.id == dono_id
