"""rotas de certificados"""

from fastapi import APIRouter, Body, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.models.models import Certificado, Inscrição


router = APIRouter(prefix="/certificados", tags=["Certificados"])


@router.post(
    "",
    status_code=status.HTTP_201_CREATED,
    summary="Emitir certificado",
    description="Emite um certificado para inscrição",
)
async def emitir(
    certi: dict = Body(
        ...,
        openapi_examples={
            "Emissao": {
                "summary": "Emitir certificado",
                "description": "Emite certificado para inscrição",
                "value": {"inscricao_id": 1},
            }
        },
    ),
    db: Session = Depends(get_db),
):
    insc = db.query(Inscrição).filter(Inscrição.id == certi.get("inscricao_id")).first()
    if not insc:
        raise HTTPException(status_code=404, detail="Inscrição não encontrada")

    # uma inscricao so gera um certificado
    ja_tem = db.query(Certificado).filter(Certificado.inscricao_id == certi["inscricao_id"]).first()
    if ja_tem:
        raise HTTPException(status_code=400, detail="Certificado já emitido para esta inscrição")

    novo = Certificado(
        inscricao_id=certi["inscricao_id"],
        usuario_id=insc.usuario_id,
        codigo_certificacao=f"ESUDA-{insc.id}-{certi['inscricao_id']}",
        status="pendente",
    )
    db.add(novo)
    db.commit()
    db.refresh(novo)
    return {"success": True, "message": "Certificado emitido", "data": {"id": novo.id, "codigo": novo.codigo_certificacao}}


@router.get(
    "",
    summary="Listar certificados",
    description="Lista todos os certificados do sistema",
)
async def listar_certificados(db: Session = Depends(get_db)):
    certs = db.query(Certificado).all()
    return [
        {"id": c.id, "codigo": c.codigo_certificacao, "status": c.status, "inscricao_id": c.inscricao_id}
        for c in certs
    ]


@router.put(
    "/{cert_id}",
    summary="Atualizar certificado",
    description="Atualiza status do certificado",
)
async def atualizar_certificado(
    cert_id: int,
    dados: dict = Body(
        ...,
        openapi_examples={
            "Emitido": {
                "summary": "Certificado emitido",
                "description": "Atualiza status para emitido",
                "value": {"status": "emitido"},
            }
        },
    ),
    db: Session = Depends(get_db),
) -> dict:
    db_cert = db.query(Certificado).filter(Certificado.id == cert_id).first()
    if not db_cert:
        raise HTTPException(status_code=404, detail="Certificado não encontrado")

    if "status" in dados:
        db_cert.status = dados["status"]
        db.commit()
        db.refresh(db_cert)

    return {"success": True, "message": "Certificado atualizado", "data": {"id": db_cert.id, "status": db_cert.status}}


@router.delete(
    "/{cert_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Deletar certificado",
    description="Remove certificado do sistema",
)
async def deletar_certificado(cert_id: int, db: Session = Depends(get_db)) -> None:
    db_cert = db.query(Certificado).filter(Certificado.id == cert_id).first()
    if db_cert:
        db.delete(db_cert)
        db.commit()
