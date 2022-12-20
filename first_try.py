import time
from aiogram import Bot, types
from aiogram.dispatcher import Dispatcher
from aiogram.utils import executor
from random import randint
from asyncio import sleep

TOKEN = '***'
#bot = telebot.TeleBot(TOKEN)
bot = Bot(token=TOKEN)
dep = Dispatcher(bot)
flag = 0

@dep.message_handler(commands=['start'])
async def hello_message(message: types.Message):
    global flag
    flag += 1
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    item_1 = types.KeyboardButton("/help")
    item_2 = types.KeyboardButton("/leave")
    item_3 = types.KeyboardButton("/infa")
    markup.add(item_1, item_2, item_3)
    await bot.send_message(message.chat.id, f"О, {message.from_user.username}, так ты у нас новенький! Ну ничего, чувствуй себя как дома!" "\n -нажми на help и узнаешь, какие команды доступны" "\n -нажми на leave и ты выйдешь из этого сокровища" "\n -нажми на infa и узнаешь лог нашего бота", reply_markup=markup)

@dep.message_handler(commands=['help'])
async def help(message):
    global flag
    flag += 1

    b1 = types.KeyboardButton("/start")
    b2 = types.KeyboardButton("/help")
    b3 = types.KeyboardButton("/leave")
    b4 = types.KeyboardButton("/infa")
    b5 = types.KeyboardButton("/nbawallpapers")
    b6 = types.KeyboardButton("/somequotes")
    b7 = types.KeyboardButton("/game")
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
    markup.add(b1, b2, b3, b4, b5, b6, b7)
    text = '''
/start -> начать
/help -> экскурс по командам
/leave -> покинуть чатик :(
/infa -> инфа бота
/nbawallpaper -> фотки команд как обои на телефон
/somquotes -> немного юмора
/rega - знакомство
    '''
    await bot.send_message(message.chat.id, text, reply_markup=markup)

@dep.message_handler(commands=['leave'])
async def byby(message) :
    global flag
    flag += 1

    text = 'Ну пока :('
    await bot.send_message(message.chat.id, text)
    await sleep(2)
    await bot.leave_chat(message.chat.id)

@dep.message_handler(commands=['infa'])
async def information(message) :
    global flag
    flag += 1
    text = '''1) бот здаровается с новыми пользователями
2) бот может обидеться и завершить процесс
3) бот умеет излогать цитаты
4) бот умеет выдвать юаскетболны обои на телефон
5) бот умеет распологать к себе пользователей и знакомиться'''
    await bot.send_message(message.chat.id, text)

@dep.message_handler(commands=['game'])
async def information(message) :
    databot = await bot.send_dice(message.from_user.id)
    databot = databot['dice']['value']
    await sleep(2)

    datauser = await bot.send_dice(message.from_user.id)
    datauser = datauser['dice']['value']
    await sleep(2)

    if databot > datauser:
        await bot.send_message(message.from_user.id, 'Ты лузер!')
    elif databot < datauser:
        await bot.send_message(message.from_user.id, 'Ты чемпион!')
    else:
        await bot.send_message(message.from_user.id, 'Ну вот опять, дружеская ничья...')

@dep.message_handler(commands=['nbawallpapers'])
async def cat(message):
    global flag
    flag += 1
    b1 = types.KeyboardButton("Los Angeles")
    b2 = types.KeyboardButton("Boston Celtics")
    b3 = types.KeyboardButton("Memphis Grizzlies")
    b4 = types.KeyboardButton("Atlanta Hawks")
    b5 = types.KeyboardButton("Golden State Warriors")
    b6 = types.KeyboardButton("Portland Trail Blazers")
    b7 = types.KeyboardButton("/help")
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
    markup.add(b1, b2, b3, b4, b5, b6, b7)
    text = '''
    -Я делаю все возможное, чтобы выигрывать, 
    будь-то сидение на скамейке, 
    размахивание полотенцем, 
    передача стакана воды партнеру по команде или бросок по финальному свистку - Коби Брайант.'''
    #bot.send_message(message.chat.id, "Legend", reply_markup=markup)
    await bot.send_message(message.chat.id, text, reply_markup=markup)

fil = open('quotes.txt', 'r', encoding='UTF-8')
quotes = fil.read().split('\n')
fil.close()

@dep.message_handler(commands=['somequotes'])
async def best_motivation(message):
    global flag
    r = randint(0, len(quotes) - 1)
    tex = quotes[r]
    await bot.send_message(message.chat.id, tex)
    await bot.send_message(message.chat.id, "На сегодня мотивации цитатками хватит!")

@dep.message_handler(content_types=['new_chat_members'])
async def hey(message):
    await bot.send_message(message.chat.id, "О, так ты у нас новенький! Ну ничего, чувствую себя как дома!")

@dep.message_handler(content_types=['audio', 'photo', 'document'])
async def whathell(message):
    await bot.send_message(message.from_user.id, 'Мне сложно понять, что вы от мееня требуете, воспользуйтесь командой /help')

@dep.message_handler(content_types=['text'])
async def get_text_message(message):
    if message.text == 'Привет':
        await bot.send_message(message.chat.id, 'Привет, как жизнь? Чем обязан?\nПредлагаю сразу знакомится, напиши: /help')

    if message.text == 'Los Angeles':
        nba1 = 'https://i.pinimg.com/564x/4d/c5/df/4dc5dfe0dc438919c59ed1106e517640.jpg'
        await bot.send_photo(message.chat.id, nba1)
        await bot.send_message(message.chat.id, 'Rest and Peace Kobe 😥')

    if message.text == 'Boston Celtics':
        nba2 = 'https://i.pinimg.com/564x/fc/19/2f/fc192fab42b31edad36f2e158e2c213a.jpg'
        await bot.send_photo(message.chat.id, nba2)
        await bot.send_message(message.chat.id, 'Tatum 🫡')

    if message.text == 'Memphis Grizzlies':
        nba3 = 'https://i.pinimg.com/564x/20/b7/91/20b79177f2acea25ba732c0c3c561c3c.jpg'
        await bot.send_photo(message.chat.id, nba3)
        await bot.send_message(message.chat.id, 'Ja Morant 🥶')

    if message.text == 'Atlanta Hawks':
        nba4 = 'https://i.pinimg.com/564x/04/bf/6e/04bf6e9e99415164d9825f7d1fbcbdcc.jpg'
        await bot.send_photo(message.chat.id, nba4)
        await bot.send_message(message.chat.id, 'Tray Young 😶‍🌫️')

    if message.text == 'Golden State Warriors':
        nba5 = 'https://i.pinimg.com/564x/cf/94/19/cf9419cc399f0ba2f32e49b5c72c4ff1.jpg'
        await bot.send_photo(message.chat.id, nba5)
        await bot.send_message(message.chat.id, 'Stef CCCCary 🤯')

    if message.text == 'Portland Trail Blazers':
        nba6 = 'https://i.pinimg.com/564x/fa/d0/6a/fad06a33b98c77641db9f7bd5a4902be.jpg'
        await bot.send_photo(message.chat.id, nba6)
        await bot.send_message(message.chat.id, 'Lillard 🫠')

    if message.text == 'Дебил' or message.text == 'Тупой':
        await bot.send_message(message.chat.id, 'Умолкаю под воздействием грубой силы...')
        await sleep(2)
        await bot.leave_chat(message.chat.id)

    if message.text == 'Выйти':
        await bot.leave_chat(message.chat.id)
    

if __name__ == '__main__':
    executor.start_polling(dep)