"""o que cada papel pode fazer"""
PERFIS = {
    "admin": {
        "pode_excluir_evento": True,
        "pode_criar_evento": True,
        "pode_emitir_certificado": True,
        "pode_gerenciar_usuarios": True,
    },
    "organizador": {
        "pode_excluir_evento": False,
        "pode_criar_evento": True,
        "pode_emitir_certificado": True,
        "pode_gerenciar_usuarios": False,
    },
    "participante": {
        "pode_excluir_evento": False,
        "pode_criar_evento": False,
        "pode_emitir_certificado": False,
        "pode_gerenciar_usuarios": False,
    },
}
