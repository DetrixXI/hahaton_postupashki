from pydantic_settings import BaseSettings
from pydantic import BaseModel


class InitializationConf(BaseModel):
    port: int = 8000
    host: str = "0.0.0.0"

class DB(BaseModel):
    async_url: str = "sqlite+aiosqlite:///./all_db.db"
    sync_url: str = "sqlite:///./all_db.db"

class Settings(BaseSettings):
    #Для старта приложения фастапи
    initial: InitializationConf = InitializationConf()

    #ДБ
    database: DB = DB()

    #секурити часть
    secret_key : str = ")@p)85yZlHMFWVwxK74jlH4hfyGB$W)k*e4o+!UsoOm!9fK)IW4xL^k=b@upvKGUs_b!KYROjn8258DL4CjH2RiEwEbnjU!tNf3s"
    algo: str = "HS256"
    access_t_exp_sec: int = 3000000
    refresh_t_exp_min: int = 30
    ...

settings = Settings()