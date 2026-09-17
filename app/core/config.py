from pydantic_settings import BaseSettings, SettingsConfigDict


class Configuracoes(BaseSettings):
    # configuracoes gerais do projeto
    # da pra mudar qualquer uma dessas criando um arquivo .env na raiz
    nome_projeto: str = "Esuda Certificados"
    database_url: str = "sqlite:///./esuda.db"

    model_config = SettingsConfigDict(env_file=".env")
