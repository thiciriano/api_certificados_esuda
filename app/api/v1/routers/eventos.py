"""rotas de eventos"""

from datetime import date

from fastapi import APIRouter, Body, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.deps import get_current_active_user, precisa_de_permissao
from app.core.permissions import eh_dono_ou_admin
from app.core.swagger_presets import EXEMPLO_EVENTO, EXEMPLO_EVENTO_UPDATE
from app.database.database import get_db
from app.models.models import Certificado, Categoria, Evento, Inscrição, Usuario
from app.schemas.schemas import EventoCreate, EventoOut, EventoUpdate, RespostaEvento


router = APIRouter(prefix="/eventos", tags=["Eventos"])


@router.post(
    "",
    status_code=status.HTTP_201_CREATED,
    response_model=RespostaEvento,
    summary="Criar evento",
    description="Cria um novo evento no sistema. Exige perfil de administrador ou organizador.",
)
async def criar_evento(
    evento: EventoCreate = Body(..., openapi_examples=EXEMPLO_EVENTO),
    current_user: Usuario = Depends(precisa_de_permissao("pode_criar_evento")),
    db: Session = Depends(get_db),
) -> RespostaEvento:
    cat = db.query(Categoria).filter(Categoria.id == evento.categoria_id).first()
    if not cat:
        raise HTTPException(status_code=404, detail="Categoria não encontrada")

    # titulo tambem é unico (R2)
    titulo_ja_usado = db.query(Evento).filter(Evento.titulo == evento.titulo).first()
    if titulo_ja_usado:
        raise HTTPException(status_code=400, detail="Já existe evento com este título")

    # data tem que ser futura (R5)
    if evento.data_evento < date.today():
        raise HTTPException(status_code=400, detail="Não é permitido cadastrar evento com data passada")

    novo = Evento(
        titulo=evento.titulo,
        descricao=evento.descricao,
        data_evento=evento.data_evento.isoformat(),  # o banco guarda como texto
        local=evento.local,
        capacidade=evento.capacidade,
        vagas_disponiveis=evento.capacidade,  # abre com todas as vagas
        categoria_id=evento.categoria_id,
        criado_por=current_user.id,  # fica registrado quem criou (é o dono do evento)
    )
    db.add(novo)
    db.commit()
    db.refresh(novo)
    return RespostaEvento(message="Evento criado", data=novo)


@router.get(
    "",
    response_model=list[EventoOut],
    summary="Listar eventos",
    description="Lista todos os eventos do sistema. Consulta aberta (não exige login).",
)
async def listar_eventos(db: Session = Depends(get_db)) -> list[EventoOut]:
    return db.query(Evento).all()


@router.get(
    "/{evento_id}",
    response_model=EventoOut,
    summary="Ver evento",
    description="Devolve um evento pelo id. Consulta aberta (não exige login). 404 se não existir.",
)
async def ver_evento(evento_id: int, db: Session = Depends(get_db)) -> EventoOut:
    db_evento = db.query(Evento).filter(Evento.id == evento_id).first()
    if not db_evento:
        raise HTTPException(status_code=404, detail="Evento não encontrado")
    return db_evento


@router.put(
    "/{evento_id}",
    response_model=RespostaEvento,
    summary="Atualizar evento",
    description=(
        "Atualiza os dados de um evento. Organizador só altera eventos que ele criou; "
        "administrador altera qualquer um."
    ),
)
async def atualizar_evento(
    evento_id: int,
    evento: EventoUpdate = Body(..., openapi_examples=EXEMPLO_EVENTO_UPDATE),
    current_user: Usuario = Depends(precisa_de_permissao("pode_editar_evento")),
    db: Session = Depends(get_db),
) -> RespostaEvento:
    db_evento = db.query(Evento).filter(Evento.id == evento_id).first()
    if not db_evento:
        raise HTTPException(status_code=404, detail="Evento não encontrado")

    # nao da pra mexer no evento de outro organizador (alterar a URL nao adianta)
    if not eh_dono_ou_admin(current_user, db_evento.criado_por):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Você só pode alterar eventos que você criou",
        )

    dados = evento.model_dump(exclude_unset=True)

    if "titulo" in dados:
        titulo_ja_usado = (
            db.query(Evento)
            .filter(Evento.titulo == dados["titulo"], Evento.id != evento_id)
            .first()
        )
        if titulo_ja_usado:
            raise HTTPException(status_code=400, detail="Já existe evento com este título")

    if "data_evento" in dados and dados["data_evento"] < date.today():
        raise HTTPException(status_code=400, detail="Não é permitido cadastrar evento com data passada")

    if "capacidade" in dados:
        inscritos = (
            db.query(Inscrição)
            .filter(Inscrição.evento_id == evento_id, Inscrição.status == "ativa")
            .count()
        )
        if dados["capacidade"] < inscritos:
            raise HTTPException(
                status_code=400,
                detail="Capacidade não pode ser menor que o número de inscrições ativas",
            )
        # recalcula as vagas em cima da nova capacidade
        dados["vagas_disponiveis"] = dados["capacidade"] - inscritos

    if "data_evento" in dados:
        dados["data_evento"] = dados["data_evento"].isoformat()  # o banco guarda como texto

    # só muda o que veio no body
    for campo, valor in dados.items():
        setattr(db_evento, campo, valor)

    db.commit()
    db.refresh(db_evento)
    return RespostaEvento(message="Evento atualizado", data=db_evento)


@router.delete(
    "/{evento_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Deletar evento",
    description=(
        "Remove um evento do sistema junto com as inscrições e certificados dele. "
        "Somente administradores (R9)."
    ),
)
async def deletar_evento(
    evento_id: int,
    _: Usuario = Depends(precisa_de_permissao("pode_excluir_evento")),
    db: Session = Depends(get_db),
) -> None:
    db_evento = db.query(Evento).filter(Evento.id == evento_id).first()
    if not db_evento:
        raise HTTPException(status_code=404, detail="Evento não encontrado")

    # apaga na ordem certa, senao fica inscricao/certificado orfao
    inscricoes_ids = [
        i.id for i in db.query(Inscrição).filter(Inscrição.evento_id == evento_id).all()
    ]
    if inscricoes_ids:
        db.query(Certificado).filter(Certificado.inscricao_id.in_(inscricoes_ids)).delete(
            synchronize_session=False
        )
        db.query(Inscrição).filter(Inscrição.evento_id == evento_id).delete(
            synchronize_session=False
        )
    db.delete(db_evento)
    db.commit()
