import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database.conexao import pegar_sessao
from app.models.certificado import Certificado
from app.models.inscricao import Inscricao
from app.schemas.certificado import CertificadoCriar, CertificadoResposta

router = APIRouter(prefix="/certificados", tags=["Certificados"])


@router.post("", response_model=CertificadoResposta, status_code=status.HTTP_201_CREATED)
def emitir_certificado(dados: CertificadoCriar, db: Session = Depends(pegar_sessao)):
    inscricao = db.query(Inscricao).filter(Inscricao.id == dados.inscricao_id).first()
    if not inscricao:
        raise HTTPException(status_code=404, detail="Inscrição não encontrada")

    # regra de negocio: só emite certificado pra inscrição ativa
    if inscricao.status != "ativa":
        raise HTTPException(status_code=400, detail="Só pode emitir certificado para inscrição ativa")

    # regra de negocio: não pode emitir certificado duplicado
    ja_tem = db.query(Certificado).filter(Certificado.inscricao_id == inscricao.id).first()
    if ja_tem:
        raise HTTPException(status_code=400, detail="Já existe um certificado emitido para essa inscrição")

    certificado = Certificado(
        inscricao_id=inscricao.id,
        # gera um código aleatório de 8 caracteres pro certificado
        codigo=uuid.uuid4().hex[:8].upper()
    )
    db.add(certificado)
    db.commit()
    db.refresh(certificado)
    return certificado


@router.get("", response_model=list[CertificadoResposta])
def listar_certificados(skip: int = 0, limit: int = 100, db: Session = Depends(pegar_sessao)):
    return db.query(Certificado).offset(skip).limit(limit).all()


@router.get("/{certificado_id}", response_model=CertificadoResposta)
def buscar_certificado(certificado_id: int, db: Session = Depends(pegar_sessao)):
    certificado = db.query(Certificado).filter(Certificado.id == certificado_id).first()
    if not certificado:
        raise HTTPException(status_code=404, detail="Certificado não encontrado")
    return certificado
