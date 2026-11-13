"""rotas de certificados"""

from datetime import date
from uuid import uuid4

from fastapi import APIRouter, Body, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.deps import get_current_active_user, precisa_de_permissao
from app.core.swagger_presets import EXEMPLO_CERTIFICADO, EXEMPLO_CERTIFICADO_STATUS
from app.database.database import get_db
from app.models.models import Certificado, Evento, Inscrição, Usuario
from app.schemas.schemas import (
    CertificadoCreate,
    CertificadoOut,
    CertificadoStatusUpdate,
    RespostaCertificado,
)


router = APIRouter(prefix="/certificados", tags=["Certificados"])


def _certificados_do_organizador(db: Session, usuario: Usuario) -> list[Certificado]:
    """certificados de inscricoes de eventos criados pelo organizador"""
    eventos_ids = [
        e.id for e in db.query(Evento).filter(Evento.criado_por == usuario.id).all()
    ]
    if not eventos_ids:
        return []
    inscricoes_ids = [
        i.id for i in db.query(Inscrição).filter(Inscrição.evento_id.in_(eventos_ids)).all()
    ]
    return (
        db.query(Certificado)
        .filter(Certificado.inscricao_id.in_(inscricoes_ids))
        .all()
    )


@router.post(
    "",
    status_code=status.HTTP_201_CREATED,
    response_model=RespostaCertificado,
    summary="Emitir certificado",
    description=(
        "Emite um certificado para uma inscrição. Exige perfil de administrador ou "
        "organizador e inscrição ativa (R8). Cada inscrição gera no máximo um certificado (R10)."
    ),
)
async def emitir(
    certi: CertificadoCreate = Body(..., openapi_examples=EXEMPLO_CERTIFICADO),
    _: Usuario = Depends(precisa_de_permissao("pode_emitir_certificado")),
    db: Session = Depends(get_db),
) -> RespostaCertificado:
    insc = db.query(Inscrição).filter(Inscrição.id == certi.inscricao_id).first()
    if not insc:
        raise HTTPException(status_code=404, detail="Inscrição não encontrada")

    # so emite pra inscricao que ta ativa (R8)
    if insc.status != "ativa":
        raise HTTPException(status_code=400, detail="Só é possível emitir certificado para inscrição ativa")

    # uma inscricao so gera um certificado (R10)
    ja_tem = db.query(Certificado).filter(Certificado.inscricao_id == insc.id).first()
    if ja_tem:
        raise HTTPException(status_code=400, detail="Certificado já emitido para esta inscrição")

    novo = Certificado(
        inscricao_id=insc.id,
        usuario_id=insc.usuario_id,
        # codigo com parte aleatoria pra nunca repetir (o formato ESUDA- id na 1AV colidia)
        codigo_certificacao=f"ESUDA-{insc.id}-{uuid4().hex[:8].upper()}",
        data_emissao=date.today(),
        status="pendente",
    )
    db.add(novo)
    db.commit()
    db.refresh(novo)
    return RespostaCertificado(message="Certificado emitido", data=novo)


@router.get(
    "",
    response_model=list[CertificadoOut],
    summary="Listar certificados",
    description=(
        "Participante vê os próprios certificados, organizador vê os dos eventos que "
        "criou e administrador vê todos."
    ),
)
async def listar_certificados(
    current_user: Usuario = Depends(get_current_active_user),
    db: Session = Depends(get_db),
) -> list[CertificadoOut]:
    if current_user.papel == "admin":
        return db.query(Certificado).all()

    if current_user.papel == "organizador":
        return _certificados_do_organizador(db, current_user)

    return db.query(Certificado).filter(Certificado.usuario_id == current_user.id).all()


@router.put(
    "/{cert_id}",
    response_model=RespostaCertificado,
    summary="Atualizar certificado",
    description=(
        "Atualiza o status do certificado. Exige perfil de administrador ou organizador. "
        "Certificado cancelado não volta de status (é terminal)."
    ),
)
async def atualizar_certificado(
    cert_id: int,
    dados: CertificadoStatusUpdate = Body(..., openapi_examples=EXEMPLO_CERTIFICADO_STATUS),
    _: Usuario = Depends(precisa_de_permissao("pode_emitir_certificado")),
    db: Session = Depends(get_db),
) -> RespostaCertificado:
    db_cert = db.query(Certificado).filter(Certificado.id == cert_id).first()
    if not db_cert:
        raise HTTPException(status_code=404, detail="Certificado não encontrado")

    # cancelado nao volta (regra nova da 2AV, pra historico ficar confiavel)
    if db_cert.status == "cancelado" and dados.status != "cancelado":
        raise HTTPException(status_code=400, detail="Certificado cancelado não pode mudar de status")

    if dados.status == "emitido" and db_cert.status != "emitido":
        db_cert.data_emissao = date.today()  # emissao de verdade é quando vira emitido

    db_cert.status = dados.status
    db.commit()
    db.refresh(db_cert)
    return RespostaCertificado(message="Certificado atualizado", data=db_cert)


@router.delete(
    "/{cert_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Deletar certificado",
    description="Remove certificado do sistema. Somente administradores.",
)
async def deletar_certificado(
    cert_id: int,
    _: Usuario = Depends(precisa_de_permissao("pode_excluir_certificado")),
    db: Session = Depends(get_db),
) -> None:
    db_cert = db.query(Certificado).filter(Certificado.id == cert_id).first()
    if not db_cert:
        raise HTTPException(status_code=404, detail="Certificado não encontrado")
    db.delete(db_cert)
    db.commit()
