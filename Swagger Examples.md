O seu projeto **Esuda Certificados** tem **22 rotas** divididas em 5 entidades (`usuarios`, `eventos`, `inscricoes`, `certificados` e `categorias`). Preencher payloads manualmente para demonstrar todas essas rotas ao professor Victor tomaria muito tempo.

Para resolver isso de forma elegante para o MVP, **não é necessário criar rotas de teste extras ou alterar suas tabelas do banco**. A solução ideal consiste em aplicar **exemplos pré-configurados (`openapi_examples`) nos schemas do Pydantic ou nos endpoints do FastAPI**, permitindo preencher os dados no Swagger com apenas **1 clique**.

Abaixo está o passo a passo de como estruturar isso no seu projeto para a apresentação da faculdade:

---

### Step 1: Criar um arquivo de Presets/Dados de Teste

Para manter seu código limpo e organizado dentro do padrão do projeto, crie um arquivo chamado `swagger_presets.py` dentro da pasta `app/core/` (ou `app/schemas/`) com os dados das suas entidades:

**`app/core/swagger_presets.py`**

```python
# Presets prontos para a apresentação do Esuda Certificados

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

```

---

### Step 2: Conectar os Presets nas Rotas do FastAPI

Abra os arquivos de rotas dentro da pasta `app/api/v1/routers/` (ex: `usuarios.py`, `eventos.py`, `inscricoes.py`) e adicione o parâmetro `Body(openapi_examples=...)` nas rotas do tipo `POST` e `PUT`:

#### Exemplo em `app/api/v1/routers/usuarios.py`:

```python
from fastapi import APIRouter, Body
from app.schemas.usuario import UsuarioCreate  # seu schema
from app.core.swagger_presets import EXEMPLO_USUARIO

router = APIRouter()

@router.post("/usuarios", status_code=201)
async def criar_usuario(
    usuario: UsuarioCreate = Body(..., openapi_examples=EXEMPLO_USUARIO)
):
    # Sua lógica existente de criação no banco
    pass

```

#### Exemplo em `app/api/v1/routers/eventos.py`:

```python
from fastapi import APIRouter, Body
from app.core.swagger_presets import EXEMPLO_EVENTO

router = APIRouter()

@router.post("/eventos", status_code=201)
async def criar_evento(
    evento = Body(..., openapi_examples=EXEMPLO_EVENTO)
):
    # Sua lógica existente de criação
    pass

```

---

### Step 3: Script de Seed/População Rápida (Bônus para a Defesa)

Para evitar o preenchimento manual de instâncias iniciais antes de testar endpoints como "Emitir Certificado" ou "Inscrever Aluno" (que exigem `usuario_id` e `evento_id` existentes no banco), você pode criar um comando ou script de inicialização rápido para popular o banco de dados.

Crie um arquivo na raiz do projeto chamado `seed.py`:

```python
# seed.py - Rode este script para popular o banco zerado em segundos!
import requests

BASE_URL = "http://localhost:8000/api/v1"

def popular_banco():
    print("🚀 Populando banco com dados de teste...")

    # 1. Criar Categorias
    cat = requests.post(f"{BASE_URL}/categorias", json={
        "nome": "Workshop", "descricao": "Eventos Práticos"
    }).json()

    # 2. Criar Usuários
    user = requests.post(f"{BASE_URL}/usuarios", json={
        "nome": "Thiago Henrique", "email": "thiago@esuda.edu.br", 
        "senha": "123", "papel": "participante"
    }).json()

    # 3. Criar Evento
    event = requests.post(f"{BASE_URL}/eventos", json={
        "titulo": "Apresentação MVP Esuda", "descricao": "Defesa de ADS",
        "data_evento": "2026-11-10", "local": "Auditório",
        "capacidade": 30, "categoria_id": cat.get("id", 1)
    }).json()

    print("✅ Banco pronto para demonstração!")

if __name__ == "__main__":
    popular_banco()

```

---

### Como apresentar para o Professor no Swagger (`/docs`):

1. Acesse `http://localhost:8000/docs`.


2. Clique na rota (ex: `POST /api/v1/usuarios`).


3. Clique no botão **Try it out**.


4. No canto superior direito da caixa de texto do payload, aparecerá o menu dropdown **Examples** com as opções (ex: `🎓 Aluno (Participante)` e `👨‍🏫 Professor (Organizador)`).
5. Clique em uma das opções: **o JSON inteiro será preenchido automaticamente**.
6. Clique em **Execute** para testar as regras de negócio e validações em tempo real.