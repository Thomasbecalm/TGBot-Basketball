import os

from dataclasses import dataclass
from environs import Env

# from dotenv import load_dotenv

# Find .env file with os variables
# load_dotenv("dev.env")
# retrieve config variables
# try:
# BOT_TOKEN = "6190353623:AAErMAOxCUeb-8g2VBUB24lhj7XTurLqm1Q"  # os.getenv('BOT_TOKEN')
# BOT_OWNERS = [int(x) for x in os.getenv('BOT_OWNERS').split(",")]
# except (TypeError, ValueError) as ex:
# print("Error while reading config:", ex)

@dataclass
class DatabaseConfig:
    database: str         # Название базы данных
    db_host: str          # URL-адрес базы данных
    db_user: str          # Username пользователя базы данных
    db_password: str      # Пароль к базе данных

@dataclass
class TgBot:
    token: str            # Токен для доступа к телеграм-боту
    admin_ids: list[int]  # Список id администраторов бота

@dataclass
class Config:
    tg_bot: TgBot
    db: DatabaseConfig

# def load_config(path: str | None) -> Config:
#     env: Env = Env()
#     env.read_env(path)
#     return Config(tg_bot=TgBot(token=env('BOT_TOKEN'),
#                                admin_ids=list(map(int, env.list('ADMIN_IDS')))),
#                   db=DatabaseConfig(database=env('DATABASE'),
#                                     db_host=env('DB_HOST'),
#                                     db_user=env('DB_USER'),
#                                     db_password=env('DB_PASSWORD')))

env: Env = Env()
env.read_env("/Users/todorov_want/Desktop/FinallyTgBot/dev.env")

config = Config(tg_bot=TgBot(token=env('BOT_TOKEN'),
                             admin_ids=list(map(int, env.list('ADMIN_IDS')))),
                db=DatabaseConfig(database=env('DATABASE'),
                                  db_host=env('DB_HOST'),
                                  db_user=env('DB_USER'),
                                  db_password=env('DB_PASSWORD')))

print('BOT_TOKEN:', config.tg_bot.token)
print('ADMIN_IDS:', config.tg_bot.admin_ids)
print()
print('DATABASE:', config.db.database)
print('DB_HOST:', config.db.db_host)
print('DB_USER:', config.db.db_user)
print('DB_PASSWORD:', config.db.db_password)
