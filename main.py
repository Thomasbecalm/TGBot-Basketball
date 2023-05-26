import logging
import handlers
import asyncio

from aiogram import Bot, Dispatcher
from database import BotDB
from config import config
from aiogram.types import BotCommand
from aiogram.fsm.storage.memory import MemoryStorage

# from config_data.config import load_config
# config = load_config('<путь к файлу .env>')

BotDB = BotDB('playgrounds.db')
bot: Bot = Bot(token=config.tg_bot.token, parse_mode='HTML')
dp: Dispatcher = Dispatcher()
logger = logging.getLogger(__name__)

# # Initialize logging
# logging.basicConfig(
#         level=logging.INFO,
#         format='%(filename)s:%(lineno)d #%(levelname)-8s '
#                '[%(asctime)s] - %(name)s - %(message)s')
#
# # Выводим в консоль информацию о начале запуска бота
# logger.info('Starting bot')
#
#
# storage: MemoryStorage = MemoryStorage()
#
# bot: Bot = Bot(token=config.tg_bot.token,
#                parse_mode='HTML')
# dp: Dispatcher = Dispatcher()

# Создаем асинхронную функцию
async def set_main_menu(bot: Bot):
    # Создаем список с командами и их описанием для кнопки menu
    main_menu_commands = [
        BotCommand(command='/start',
                   description='Запуск бота'),
        BotCommand(command='/help',
                   description='Справка по работе бота'),
        BotCommand(command='/cancel',
                   description='Отмена действий'),
        BotCommand(command='/support',
                   description='Поддержка'),
        BotCommand(command='/contacts',
                   description='Другие способы связи'),

        BotCommand(command='/add_court',
                   description='Добавление площадки'),
        BotCommand(command='/search_courts',
                   description='Поиск ближайших площадок'),
        BotCommand(command='/start_game',
                   description='Начать активность на площадке'),
        BotCommand(command='/exit_game',
                   description='Закончить активность на площадке'),
        BotCommand(command='/set_event',
                   description='Назначить баскетбольное мероприятие'),
        BotCommand(command='/payments',
                   description='Платежи')]
    await bot.set_my_commands(main_menu_commands)

# Функция конфигурирования и запуска бота
async def main():
    """
    Функция конфигурирования и запуска бота
    """
    logging.basicConfig(
        level=logging.INFO,
        format='%(filename)s:%(lineno)d #%(levelname)-8s '
               '[%(asctime)s] - %(name)s - %(message)s')

    logger.info('Starting bot')

    dp.include_router(handlers.all_handlers.router)
    dp.startup.register(set_main_menu)

    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())


# 1.Проблема с не уникальными айдишниками юзеров для дата бейз
# 2.Нужно закрывать баззззу
# 3.Нужно настроить список команд в MENU
# 4.Нужно везде, где можно расставить кнопки
# 5.Голосование за название площадки относительно геолокации
# 6.КОЛИЧЕСТВО ЧЕЛОВЕК НА ПЛОЩАДКЕ
# 7.ПОКАЗЫВАТЬ АНКЕТУ ПОЛЬЗОВАТЕЛЯ ПОСЛЕ ЕГО РЕГИСТРАЦИИ
# 8.НОРМАЛЬНЫЙ ПОКАЗ ПЛОЩАДОК
# 9.НАДО ПОПРОБОВАТЬ ДОБАВЛЯТЬ НА ОПРЕДЕЛЕННОЕ ВРЕМЯ В БАЗУ, ПОСЛЕ ИСТЕЧЕНИЯ ВЫЧЕТАТЬ
# 10. после того как юзер начинает игру, он не может пользоваться интерфейсом, пока не выйдет из игры
# 11. проблема с обновлением годов опыта игры в баскетбол в момент участие и выхода с игры
# 12. прблема с таймпикерами и датапикерами, нужно вручную исправлять библиотеки
# 12. ВЫБОР ТОЛЬКО ОДНОГО УРОВНЯ ИГРОКОВ ДЛЯ МЕРОПРИЯТИЯ
# 12. КРИТЕРИЙ ПОИСКА МЕРОПРИЯТИЙ ДЛЯ ПОЛЬЗОАВТЕЛЯ
# ПОКАЗАТЬ МЕРОПРТИЯТИЯ ОШИБКА ЛИСТАНИЯ!!!!!!!
# позволить ввдодить любое название для мероприятия
#


# КРИКИ ТЕСТЫ ;;;;;;;;;;;;;; ОЧЕНЬ НЕ ЮЗЕР ВРЕНДЛИ ;;;;;;;;;;;;;;;;;;;
# 1. ДВЕ ПЛОЩАДКИ РЯДОМ
# 2. ДОБАВЛЕНИЯ ОДИНАКОВЫХ ЮЗЕРОВ И ПЛОЩАДОК В БАЗУ
# 3. НЕТ ВОЗМОЖНОСТИ СМОТРЕТЬ ПЛОЩАДКИ ПО-ДАЛЬШЕ(относительно своей геолокации)




# MAIN TASKS:
# /add_court
# /search_court(nearest)
# /play
# /find_place
# /registationuser
# /add_meropriutie
# /personal_area



# не нажимется кнопка геолокации на компе
# дима видит мои площадки
# Довление площадки из дома
#