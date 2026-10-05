"""sobe o servidor. uso: python run.py  (a porta pode ir depois, ex: python run.py 8080)"""

import uvicorn
import sys
from pathlib import Path

def main():
    """roda o uvicorn"""
    base_dir = Path(__file__).parent
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8000

    print(f"🚀 Iniciando Esuda Certificados em http://localhost:{port}")
    print(f"📊 Documentação disponível em http://localhost:{port}/docs")
    print(f"🔗 OpenAPI em http://localhost:{port}/openapi.json")

    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=port,
        reload=True,
        reload_dirs=[str(base_dir)],
    )

if __name__ == "__main__":
    main()
