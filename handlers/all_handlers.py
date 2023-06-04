import certifi
import ssl
import geopy.geocoders
import datetime

from aiogram import Router, F
from aiogram.types import (Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery, ContentType, PhotoSize)
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
from aiogram.filters import Command, CommandStart
from aiogram.filters.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.filters import Text, StateFilter
from aiogram.fsm.state import default_state
from aiogram.types import InputMediaPhoto
from aiogram.filters import and_f, or_f
# from aiogram_calendar import simple_cal_callback, SimpleCalendar, dialog_cal_callback, DialogCalendar

from geopy.distance import geodesic
from geopy.distance import distance
from geopy.geocoders import Nominatim
from geopy.extra.rate_limiter import RateLimiter
from geopy import Point
from typing import List, Tuple, Dict
from copy import deepcopy

from main import BotDB, bot
from keyboards import pagination_kb

router: Router = Router()

user_dict_template: dict = {'page': 1,
                            'bookmarks': set()}

nearest_courts: List[Tuple[int, int, str, str, str, float, float, int, int, int, int, int]] = []
users_db: dict = {}
photo_ERROR = open('/Users/todorov_want/Desktop/FinallyTgBot/handlers/ERROR_photo.jpeg', 'rb')
events_db: dict = {}
admin_events_db: dict = {}

@router.message(Command(commands=['start']), StateFilter(default_state))
async def process_start_command(message: Message):
    """
    Хэндлер
    """
    menu_botton: KeyboardButton = KeyboardButton(text=' 🏠 Меню')
    keyboard2: ReplyKeyboardMarkup = ReplyKeyboardMarkup(keyboard=[[menu_botton]],
                                                        resize_keybord=True)
    await message.answer_photo(
        photo='https://i.pinimg.com/564x/bc/99/11/bc99116f57ff62dfd621f6b935f64ec3.jpg',
        reply_markup=keyboard2)

    reg_botton: InlineKeyboardButton = InlineKeyboardButton(
        text='🤝🏼 Познакомится',
        callback_data='user_registration')
    canc_botton: InlineKeyboardButton = InlineKeyboardButton(
        text='🙅🏽 Отмена',
        callback_data='cancel_registration')
    keyboard: InlineKeyboardMarkup = InlineKeyboardMarkup(
        inline_keyboard=[[reg_botton, canc_botton]])

    await message.answer(text='Привет!\n'
                              'Этот бот - решение твоей насущной проблемы, одиночной игры в баскетбол!\n\n'
                         'Для того, чтобы лучше понимать, какого уровня игроки обитают на наших площадках и вам было удобнее выбирать себе соперников,'
                         'предлагаю познакомится 👇🏿👇🏾👇🏽👇🏼👇🏻',
                         reply_markup=keyboard)

@router.message(Command(commands=['start']), ~StateFilter(default_state))
async def process_start_command(message: Message):
    """
    Хэндлер
    """
    await message.answer(text='Вы находитесь в процессе выполнения другого дейтсвия, команда "/start" не доступна!\n\n'
                              'Для остановки заполнения, выполните команду "/cancel"(нажмите кнопку "🏠 Меню") или просто продолжайте согласно инструкциям!')

@router.message(Command(commands=['help']), StateFilter(default_state))
async def process_help_command(message: Message):
    """
    Этот хэндлер будет срабатывать на команду '/help'
    """
    # menu_botton: KeyboardButton = KeyboardButton(text=' 🏠 Меню')
    # keyboard: ReplyKeyboardMarkup = ReplyKeyboardMarkup(keyboard=[[menu_botton]],
    #                                                     resize_keybord=True,
    #                                                     one_time_keybord=True)
    await message.answer(text='Этот бот создан для объединения баскетбольного комьюнити и решения проблемы, одиночной игры в баскетбол!\n'
                                  'Краткий экскурс по интерфейсу:\n'
                                  '"⛹🏿‍♂️ Найти площадку поблизости" - нажав на нее, вы сможите согласно своей геолокации или выбранной точке на карте, найти ближайшую баскетбольную площадку со всеми характеристиками;\n'
                                  '"🗑️ Добавить новую площадку" - нажав на нее, вы сможете в несколько шагов создать новую баскетбольную площадку;\n'
                                  '"🧾 Показать мероприятия" - нажав на нее, вам будет предоставлен полный список мероприятий существующих на данный момент\n'
                                  '"📆 Назначить мероприятие" - нажав на нее, вы сможете в несколько шагов создать новое баскетбольное мероприятие с доскональным и актуальным описанием;\n'
                                  '"⚒️ Действия с игрой" - Раздел с активностями по играм, предназначенный для пользователей,'
                                  'для обозначения активности на баскетбольной площадке;\n'
                                  '"🛠️ Действия с мероприятием" - Раздел с активностями по мероприятиям, предназначенный для создателей(админов) объявлений;\n'
                                  '"🗄️ Личный кабинет" - Раздел с индивидуальной информацией для каждого пользователя;\n'
                                  '"⚙️ Тех. Поддержка" - Раздел с информацией и помощью по боту;\n')

@router.message(Command(commands=['help']), ~StateFilter(default_state))
async def process_start_command(message: Message):
    """
    Хэндлер
    """
    await message.answer(text='Вы находитесь в процессе выполнения другого дейтсвия, команда "/help" не доступна!\n\n'
                              'Для остановки заполнения, выполните команду "/cancel"(нажмите кнопку "🏠 Меню") или просто продолжайте согласно инструкциям!')

@router.message(Command(commands=['cancel']), ~StateFilter(default_state))
async def process_cancel_command_state(message: Message, state: FSMContext):
    """
    Этот хэндлер будет срабатывать на команду '/cancel'
    """
    await message.answer(text='Вы вышли из процесса заполнения, ваши данные не учтены!')
    await state.clear()

@router.message(Command(commands=['cancel']), StateFilter(default_state))
async def process_cancel_command(message: Message):
    """
    Этот хэндлер будет срабатывать на команду '/help'
    """
    await message.answer(text='Отменять нечего. Вы вне процесса заполнения!')

@router.message(Command(commands=['support']), StateFilter(default_state))
async def process_support(message: Message):
    """
    aaaa
    """
    await message.answer(text='Если у вас возникли какие либо проблемы при использовании бота,\n'
                              'то вы можете написать свою жалобу или же отзыв этому админу: @alreadygoat')

@router.message(Command(commands=['support']), ~StateFilter(default_state))
async def process_support(message: Message):
    """

    """
    await message.answer(text='Вы находитесь в процессе выполнения другого дейтсвия, команда "/support" не доступна!\n\n'
                              'Для остановки заполнения, выполните команду "/cancel"(нажмите кнопку "🏠 Меню") или просто продолжайте согласно инструкциям!')

@router.callback_query(Text(text=['tech_setting']), StateFilter(default_state))
async def process_support(callback: CallbackQuery):
    """

    """
    comand_botton: InlineKeyboardButton = InlineKeyboardButton(
        text='🔎 Подробнее о боте',
        callback_data='tech_commands')
    admin_botton: InlineKeyboardButton = InlineKeyboardButton(
        text='📲 Связаться с тех.поддержкой',
        callback_data='admin_msg')
    keyboard: InlineKeyboardMarkup = InlineKeyboardMarkup(
        inline_keyboard=[[comand_botton],
                         [admin_botton]])
    await callback.message.answer(text='Здесь вы можете подробнее узнать о боте и задать вопросы!\n',
                                  reply_markup=keyboard)
    await callback.answer()

@router.callback_query(Text(text=['tech_setting']), ~StateFilter(default_state))
async def process_support(callback: CallbackQuery):
    """

    """
    await callback.message.answer(text='Вы находитесь в процессе выполнения другого дейтсвия, кнопка " ⚙️ Тех. Поддержка" не доступна!\n\n'
                                       'Для остановки заполнения, выполните команду "/cancel"(нажмите кнопку "🏠 Меню") или просто продолжайте согласно инструкциям!')
    await callback.answer()

@router.callback_query(Text(text='tech_commands'))
async def process_support_help(callback: CallbackQuery):
    await callback.message.answer('Этот бот создан для объединения баскетбольного комьюнити и решения проблемы, одиночной игры в баскетбол!'
                                  'Краткий экскурс по интерфейсу:\n'
                                  '"⛹🏿‍♂️ Найти площадку поблизости" - нажав на нее, вы сможите согласно своей геолокации или выбранной точке на карте, найти ближайшую баскетбольную площадку со всеми характеристиками;\n'
                                  '"🗑️ Добавить новую площадку" - нажав на нее, вы сможете в несколько шагов создать новую баскетбольную площадку;\n'
                                  '"🧾 Показать мероприятия" - нажав на нее, вам будет предоставлен полный список мероприятий существующих на данный момент\n'
                                  '"📆 Назначить мероприятие" - нажав на нее, вы сможете в несколько шагов создать новое баскетбольное мероприятие с доскональным и актуальным описанием;\n'
                                  '"⚒️ Действия с игрой" - Раздел с активностями по играм, предназначенный для пользователей,\n'
                                  'для обозначения активности на баскетбольной площадке;\n'
                                  '"🛠️ Действия с мероприятием" - Раздел с активностями по мероприятиям, предназначенный для создателей(админов) объявлений;\n'
                                  '"🗄️ Личный кабинет" - Раздел с индивидуальной информацией для каждого пользователя;\n'
                                  '"⚙️ Тех. Поддержка" - Раздел с информацией и помощью по боту;\n')

    await callback.answer()

@router.callback_query(Text(text='admin_msg'))
async def process_support_dialog(callback: CallbackQuery):
    """

    """
    await callback.message.answer(text='Если у вас возникли какие-либо вопросы или предложения, то напишите этому администратору:\n'
                                       '@alreadygoat')
    await callback.answer()

@router.message(Command(commands=['contacts']), StateFilter(default_state))
async def process_contacts(message: Message):
    """

    """
    await message.answer(text='Для предложения сотрудничества, пишите на эту почту: denis6_4@mail.ru')

@router.message(Command(commands=['contacts']), ~StateFilter(default_state))
async def process_contacts(message: Message):
    """

    """
    await message.answer(text='Вы находитесь в процессе выполнения другого дейтсвия, команда "/contacts" не доступна!\n\n'
                              'Для остановки заполнения, выполните команду "/cancel"(нажмите кнопку "🏠 Меню") или просто продолжайте согласно инструкциям!')

@router.message(Text(text=['🏠 Меню']), StateFilter(default_state))
async def process_go_to_menu(message: Message):
    users_db: dict = {}
    events_db: dict = {}
    admin_events_db: dict = {}
    menu_botton: KeyboardButton = KeyboardButton(text=' 🏠 Меню')
    keyboard2: ReplyKeyboardMarkup = ReplyKeyboardMarkup(keyboard=[[menu_botton]],
                                                        resize_keybord=True)
    await message.answer_photo(
        photo='https://i.pinimg.com/564x/bc/99/11/bc99116f57ff62dfd621f6b935f64ec3.jpg',
        reply_markup=keyboard2)

    srch_botton: InlineKeyboardButton = InlineKeyboardButton(
        text='⛹🏿‍♂️ Найти площадку поблизости',
        callback_data='court_search')
    addd_botton: InlineKeyboardButton = InlineKeyboardButton(
        text='🗑️ Добавить новую площадку',
        callback_data='court_adding')
    prsn_botton: InlineKeyboardButton = InlineKeyboardButton(
        text='🗄️ Личный кабинет',
        callback_data='personal_area')
    tech_botton: InlineKeyboardButton = InlineKeyboardButton(
        text='⚙️ Тех. Поддержка',
        callback_data='tech_setting')
    setevnt_botton: InlineKeyboardButton = InlineKeyboardButton(
        text='📆 Назначить мероприятие',
        callback_data='set_event')
    casegame_botton: InlineKeyboardButton = InlineKeyboardButton(
        text='⚒️ Действия с игрой',
        callback_data='case_game')
    caseevent_botton: InlineKeyboardButton = InlineKeyboardButton(
        text='🛠️ Действия с мероприятием',
        callback_data='case_event')
    search_events_botton: InlineKeyboardButton = InlineKeyboardButton(
        text='🧾 Показать мероприятия',
        callback_data='search_events')
    keyboard: InlineKeyboardMarkup = InlineKeyboardMarkup(
        inline_keyboard=[[srch_botton],
                         [addd_botton],
                         [search_events_botton],
                         [setevnt_botton],
                         [casegame_botton],
                         [caseevent_botton],
                         [prsn_botton],
                         [tech_botton]])
    await message.answer(
        text='Ну вот и все! Вся информация собрана, система улучшена, результаы усовершенствованы!\n'
             'Вот такие функции вам доступны в нашем боте:',
        reply_markup=keyboard)

class AddGame(StatesGroup):
    latitude=State()
    longitude=State()
    result_court_id=State()

@router.message(Text(text=['🏠 Меню']), StateFilter(AddGame.result_court_id))
async def process_go_to_menu(message: Message, state: FSMContext):
    users_db: dict = {}
    events_db: dict = {}
    admin_events_db: dict = {}

    court_data = await state.get_data()
    BotDB.exit_player_from_court(message.from_user.id, court_data["result_court_id"])

    menu_botton: KeyboardButton = KeyboardButton(text=' 🏠 Меню')
    keyboard2: ReplyKeyboardMarkup = ReplyKeyboardMarkup(keyboard=[[menu_botton]],
                                                        resize_keybord=True)
    await message.answer_photo(
        photo='https://i.pinimg.com/564x/bc/99/11/bc99116f57ff62dfd621f6b935f64ec3.jpg',
        reply_markup=keyboard2)

    await state.clear()

    srch_botton: InlineKeyboardButton = InlineKeyboardButton(
        text='⛹🏿‍♂️ Найти площадку поблизости',
        callback_data='court_search')
    addd_botton: InlineKeyboardButton = InlineKeyboardButton(
        text='🗑️ Добавить новую площадку',
        callback_data='court_adding')
    prsn_botton: InlineKeyboardButton = InlineKeyboardButton(
        text='🗄️ Личный кабинет',
        callback_data='personal_area')
    tech_botton: InlineKeyboardButton = InlineKeyboardButton(
        text='⚙️ Тех. Поддержка',
        callback_data='tech_setting')
    setevnt_botton: InlineKeyboardButton = InlineKeyboardButton(
        text='📆 Назначить мероприятие',
        callback_data='set_event')
    casegame_botton: InlineKeyboardButton = InlineKeyboardButton(
        text='⚒️ Действия с игрой',
        callback_data='case_game')
    caseevent_botton: InlineKeyboardButton = InlineKeyboardButton(
        text='🛠️ Действия с мероприятием',
        callback_data='case_event')
    search_events_botton: InlineKeyboardButton = InlineKeyboardButton(
        text='🧾 Показать мероприятия',
        callback_data='search_events')
    keyboard: InlineKeyboardMarkup = InlineKeyboardMarkup(
        inline_keyboard=[[srch_botton],
                         [addd_botton],
                         [search_events_botton],
                         [setevnt_botton],
                         [casegame_botton],
                         [caseevent_botton],
                         [prsn_botton],
                         [tech_botton]])
    await message.answer(
        text='Ну вот и все! Вся информация собрана, система улучшена, результаы усовершенствованы!\n'
             'Вот такие функции вам доступны в нашем боте:',
        reply_markup=keyboard)

@router.message(Text(text=['🏠 Меню']), ~StateFilter(default_state))
async def process_go_to_menu(message: Message, state: FSMContext):
    users_db: dict = {}
    events_db: dict = {}
    admin_events_db: dict = {}
    menu_botton: KeyboardButton = KeyboardButton(text=' 🏠 Меню')
    keyboard2: ReplyKeyboardMarkup = ReplyKeyboardMarkup(keyboard=[[menu_botton]],
                                                        resize_keybord=True)
    await message.answer_photo(
        photo='https://i.pinimg.com/564x/bc/99/11/bc99116f57ff62dfd621f6b935f64ec3.jpg',
        reply_markup=keyboard2)

    await state.clear()

    srch_botton: InlineKeyboardButton = InlineKeyboardButton(
        text='⛹🏿‍♂️ Найти площадку поблизости',
        callback_data='court_search')
    addd_botton: InlineKeyboardButton = InlineKeyboardButton(
        text='🗑️ Добавить новую площадку',
        callback_data='court_adding')
    prsn_botton: InlineKeyboardButton = InlineKeyboardButton(
        text='🗄️ Личный кабинет',
        callback_data='personal_area')
    tech_botton: InlineKeyboardButton = InlineKeyboardButton(
        text='⚙️ Тех. Поддержка',
        callback_data='tech_setting')
    setevnt_botton: InlineKeyboardButton = InlineKeyboardButton(
        text='📆 Назначить мероприятие',
        callback_data='set_event')
    casegame_botton: InlineKeyboardButton = InlineKeyboardButton(
        text='⚒️ Действия с игрой',
        callback_data='case_game')
    caseevent_botton: InlineKeyboardButton = InlineKeyboardButton(
        text='🛠️ Действия с мероприятием',
        callback_data='case_event')
    search_events_botton: InlineKeyboardButton = InlineKeyboardButton(
        text='🧾 Показать мероприятия',
        callback_data='search_events')
    keyboard: InlineKeyboardMarkup = InlineKeyboardMarkup(
        inline_keyboard=[[srch_botton],
                         [addd_botton],
                         [search_events_botton],
                         [setevnt_botton],
                         [casegame_botton],
                         [caseevent_botton],
                         [prsn_botton],
                         [tech_botton]])
    await message.answer(
        text='Ну вот и все! Вся информация собрана, система улучшена, результаы усовершенствованы!\n'
             'Вот такие функции вам доступны в нашем боте:',
        reply_markup=keyboard)

# ПРОЦЕСС ДОБАВЛЕНИЯ ЮЗЕРА
class AddUser(StatesGroup):
    user_id=State()
    username=State()
    game_level=State()
    years_exprs=State()

@router.callback_query(Text(text=['user_registration']))
async def process_user_registration(callback: CallbackQuery, state: FSMContext):
    """
    Хэндлер
    """
    if (BotDB.user_exists(callback.from_user.id) == False):
        await callback.message.answer(text='Отлично! Я рад, что вы готовы со мной поделится информацией о себе,'
                                           'хоть и не столь важной для вас,'
                                            'но необходимой для всего комьюнити!\n'
                                            'Придумайте и напишите свой псевдоним, который я буду использовать в системе для составления рейтинга:')
        await state.set_state(AddUser.username)
        await callback.answer()
    else:
        srch_botton: InlineKeyboardButton = InlineKeyboardButton(
            text='⛹🏿‍♂️ Найти площадку поблизости',
            callback_data='court_search')
        addd_botton: InlineKeyboardButton = InlineKeyboardButton(
            text='🗑️ Добавить новую площадку',
            callback_data='court_adding')
        prsn_botton: InlineKeyboardButton = InlineKeyboardButton(
            text='🗄️ Личный кабинет',
            callback_data='personal_area')
        tech_botton: InlineKeyboardButton = InlineKeyboardButton(
            text='⚙️ Тех. Поддержка',
            callback_data='tech_setting')
        setevnt_botton: InlineKeyboardButton = InlineKeyboardButton(
            text='📆 Назначить мероприятие',
            callback_data='set_event')
        casegame_botton: InlineKeyboardButton = InlineKeyboardButton(
            text='⚒️ Действия с игрой',
            callback_data='case_game')
        caseevent_botton: InlineKeyboardButton = InlineKeyboardButton(
            text='🛠️ Действия с мероприятием',
            callback_data='case_event')
        search_events_botton: InlineKeyboardButton = InlineKeyboardButton(
            text='🧾 Показать мероприятия',
            callback_data='search_events')
        keyboard: InlineKeyboardMarkup = InlineKeyboardMarkup(
            inline_keyboard=[[srch_botton],
                             [addd_botton],
                             [search_events_botton],
                             [setevnt_botton],
                             [casegame_botton],
                             [caseevent_botton],
                             [prsn_botton],
                             [tech_botton]])

        await callback.message.edit_text(
            text='Вы уже зарегистрированы!\n'
                 'Вот такие функции вам доступны в нашем боте:',
            reply_markup=keyboard)
        # await callback.message.answer(
        #     text='Ну вот и все! Вся информация собрана, система улучшена, результаы усовершенствованы!\n'
        #      'Вот такие функции тебе доступны в нашем боте:',
        #     reply_markup=keyboard)
        await callback.answer()

@router.message(StateFilter(AddUser.username))
async def process_add_username(message: Message, state: FSMContext):
    """
    Эта функция сохраняет название баскетбольной площадки и запрашивает адрес.
    """
    await state.update_data(user_id=message.from_user.id)
    await state.update_data(username=message.text)

    love_botton: InlineKeyboardButton = InlineKeyboardButton(
        text='Новичок',
        callback_data='lovely_play')
    middle_botton: InlineKeyboardButton = InlineKeyboardButton(
        text='Любитель',
        callback_data='middle_play')
    extra_botton: InlineKeyboardButton = InlineKeyboardButton(
        text='Профи',
        callback_data='extra_play')
    keyboard: InlineKeyboardMarkup = InlineKeyboardMarkup(
        inline_keyboard=[[love_botton],
                         [middle_botton],
                         [extra_botton]])
    await message.answer(text="А теперь выберите свой уровень игры в баскетбол:",
                         reply_markup=keyboard)
    await state.set_state(AddUser.game_level)

@router.callback_query(StateFilter(AddUser.game_level), Text(text=['lovely_play', 'middle_play', 'extra_play']))
async def process_add_game_lvl(callback: CallbackQuery, state: FSMContext):
    """
    Хэнжлер .....
    """
    await state.update_data(game_level=callback.data)
    one_botton: InlineKeyboardButton = InlineKeyboardButton(
        text='<= 1 год',
        callback_data='one')
    two_botton: InlineKeyboardButton = InlineKeyboardButton(
        text='2 года',
        callback_data='two')
    three_botton: InlineKeyboardButton = InlineKeyboardButton(
        text='3 года',
        callback_data='three')
    four_botton: InlineKeyboardButton = InlineKeyboardButton(
        text='4 года',
        callback_data='four')
    five_botton: InlineKeyboardButton = InlineKeyboardButton(
        text='5 лет',
        callback_data='five')
    six_botton: InlineKeyboardButton = InlineKeyboardButton(
        text='6 лет',
        callback_data='six')
    seven_botton: InlineKeyboardButton = InlineKeyboardButton(
        text='7 лет',
        callback_data='seven')
    eight_botton: InlineKeyboardButton = InlineKeyboardButton(
        text='>= 8 лет ',
        callback_data='eight')
    keyboard: InlineKeyboardMarkup = InlineKeyboardMarkup(
        inline_keyboard=[[one_botton],
                         [two_botton],
                         [three_botton],
                         [four_botton],
                         [five_botton],
                         [six_botton],
                         [seven_botton],
                         [eight_botton]])
    await callback.message.edit_text(
        text='А теперь выберите, сколько по времени вы находитесь в мире баскетбола:',
        reply_markup=keyboard)
    await state.set_state(AddUser.years_exprs)
    await callback.answer()

@router.callback_query(StateFilter(AddUser.years_exprs), Text(text=['one', 'two', 'three', 'four', 'five', 'six', 'seven', 'eight']))
async def process_add_years_exp(callback: CallbackQuery, state: FSMContext):
    """
    Хэндлер
    """
    await state.update_data(years_exprs=callback.data)
    user_data = await state.get_data()
    years = 0

    if (user_data["years_exprs"] == 'one'):
        years = 1
    elif (user_data["years_exprs"] == 'two'):
        years = 2
    elif (user_data["years_exprs"] == 'three'):
        years = 3
    elif (user_data["years_exprs"] == 'four'):
        years = 4
    elif (user_data["years_exprs"] == 'five'):
        years = 5
    elif (user_data["years_exprs"] == 'six'):
        years = 6
    elif (user_data["years_exprs"] == 'seven'):
        years = 7
    else:
        years = 8

    BotDB.add_user(user_data["user_id"], user_data["username"],
                   user_data["game_level"], years)
    await state.clear()

    srch_botton: InlineKeyboardButton = InlineKeyboardButton(
        text='⛹🏿‍♂️ Найти площадку поблизости',
        callback_data='court_search')
    addd_botton: InlineKeyboardButton = InlineKeyboardButton(
        text='🗑️ Добавить новую площадку',
        callback_data='court_adding')
    prsn_botton: InlineKeyboardButton = InlineKeyboardButton(
        text='🗄️ Личный кабинет',
        callback_data='personal_area')
    tech_botton: InlineKeyboardButton = InlineKeyboardButton(
        text='⚙️ Тех. Поддержка',
        callback_data='tech_setting')
    setevnt_botton: InlineKeyboardButton = InlineKeyboardButton(
        text='📆 Назначить мероприятие',
        callback_data='set_event')
    casegame_botton: InlineKeyboardButton = InlineKeyboardButton(
        text='⚒️ Действия с игрой',
        callback_data='case_game')
    caseevent_botton: InlineKeyboardButton = InlineKeyboardButton(
        text='🛠️ Действия с мероприятием',
        callback_data='case_event')
    search_events_botton: InlineKeyboardButton = InlineKeyboardButton(
        text='🧾 Показать мероприятия',
        callback_data='search_events')
    keyboard: InlineKeyboardMarkup = InlineKeyboardMarkup(
        inline_keyboard=[[srch_botton],
                         [addd_botton],
                         [search_events_botton],
                         [setevnt_botton],
                         [casegame_botton],
                         [caseevent_botton],
                         [prsn_botton],
                         [tech_botton]])

    await callback.message.edit_text(
        text='Ну вот и все! Вся информация собрана, система улучшена, результаы усовершенствованы!\n'
             'Вот такие функции вам доступны в нашем боте:',
        reply_markup=keyboard)

    await callback.answer()

# ПРОЦЕСС ОТКАЗА ЮЗЕРА ОТ РЕГИСТРАЦИИ
@router.callback_query(Text(text=['cancel_registration']))
async def process_user_cancel_registration(callback: CallbackQuery):
    """
    Хэндлер
    """
    srch_botton: InlineKeyboardButton = InlineKeyboardButton(
        text='⛹🏿‍♂️ Найти площадку поблизости',
        callback_data='court_search')
    addd_botton: InlineKeyboardButton = InlineKeyboardButton(
        text='🗑️ Добавить новую площадку',
        callback_data='court_adding')
    prsn_botton: InlineKeyboardButton = InlineKeyboardButton(
        text='🗄️ Личный кабинет',
        callback_data='personal_area')
    tech_botton: InlineKeyboardButton = InlineKeyboardButton(
        text='⚙️ Тех. Поддержка',
        callback_data='tech_setting')
    setevnt_botton: InlineKeyboardButton = InlineKeyboardButton(
        text='📆 Назначить мероприятие',
        callback_data='set_event')
    casegame_botton: InlineKeyboardButton = InlineKeyboardButton(
        text='⚒️ Действия с игрой',
        callback_data='case_game')
    caseevent_botton: InlineKeyboardButton = InlineKeyboardButton(
        text='🛠️ Действия с мероприятием',
        callback_data='case_event')
    search_events_botton: InlineKeyboardButton = InlineKeyboardButton(
        text='🧾 Показать мероприятия',
        callback_data='search_events')
    keyboard: InlineKeyboardMarkup = InlineKeyboardMarkup(
        inline_keyboard=[[srch_botton],
                         [addd_botton],
                         [search_events_botton],
                         [setevnt_botton],
                         [casegame_botton],
                         [caseevent_botton],
                         [prsn_botton],
                         [tech_botton]])
    await callback.message.answer(text='Очень жаль! Без этого и нам, и вам будет сложно определить уровень игроков'
                               'внутри нашего комьюнити, что усложнит процесс поиска игры.\n'
                               'Оданко, вам все еще доступны все основные функции нашего бота!\nНаслаждайтесь:',
                                reply_markup=keyboard)
    await callback.answer()

# ПРОЦЕСС ДОБАВЛЕНИЯ ПЛОЩАДКИ
class AddCourt(StatesGroup):
    user_id = State()
    name = State()
    image_id = State()
    address = State()
    latitude = State()
    longitude = State()

@router.callback_query(Text(text=['court_adding']))
async def add_court(callback: CallbackQuery, state: FSMContext):
    """
    Эта функция начинает процесс добавления новой баскетбольной площадки в базу данных.
    """
    await callback.message.answer("Введите название баскетбольной площадки(то, что всегда на слуху в узком кругу играющих лиц):")
    await state.set_state(AddCourt.name)
    await callback.answer()

@router.message(Command(commands=['add_court']), StateFilter(default_state))
async def add_court(message: Message, state: FSMContext):
    """
    Эта функция начинает процесс добавления новой баскетбольной площадки в базу данных.
    """
    await message.answer("Введите название баскетбольной площадки(то, что всегда на слуху в узком кругу играющих лиц):")
    await state.set_state(AddCourt.name)

@router.message(Command(commands=['add_court']), ~StateFilter(default_state))
async def add_court(message: Message, state: FSMContext):
    """
    Эта функция начинает процесс добавления новой баскетбольной площадки в базу данных.
    """
    await message.answer('Вы находитесь в процессе выполнения другого дейтсвия, команда "/add_court" не доступна!\n\n'
                         'Для остановки заполнения, выполните команду "/cancel"(нажмите кнопку "🏠 Меню") или просто продолжайте согласно инструкциям!')

@router.message(StateFilter(AddCourt.name))
async def add_court_name(message: Message, state: FSMContext):
    """
    Эта функция сохраняет название баскетбольной площадки и запрашивает адрес.
    """
    await state.update_data(user_id=message.from_user.id)
    await state.update_data(name=message.text)

    yes_photo: InlineKeyboardButton = InlineKeyboardButton(
        text='Могу загрузить',
        callback_data='send_photo')
    not_photo: InlineKeyboardButton = InlineKeyboardButton(
        text='Нет возможности',
        callback_data='notsend_photo')
    keyboard: InlineKeyboardMarkup = InlineKeyboardMarkup(
        inline_keyboard=[[yes_photo],
                         [not_photo]])

    await message.answer("Есть ли у вас возможность загрузить фотографию площадки?",
                         reply_markup=keyboard)
    await state.set_state(AddCourt.image_id)

# @router.message(StateFilter(AddCourt.name))
# async def warning_not_name(message: Message):
#     """
#     Хэндлер
#     """
#     await message.answer(text='То, что вы отправили не похоже на название!\n'
#                               'Введите оригинальное название, состоящие ТОЛЬКО из букв!\n'
#                               'Если вы хотите прервать заполнение анкеты - '
#                               'отправьте команду /cancel(нажмите кнопку "🏠 Меню")')




@router.callback_query(Text(text=['send_photo', 'notsend_photo']), StateFilter(AddCourt.image_id))
async def process_photo_choosing(callback: CallbackQuery, state: FSMContext):
    if (callback.data == 'send_photo'):
        await callback.message.answer('Загрузите сюда фото площадки:')
    else:
        await state.update_data(image_id="https://i.pinimg.com/564x/a3/d2/16/a3d2164292452e51212a33f7844aab86.jpg")
        await callback.message.answer('Введите корректный адрес, как указано в примере(Граничная улица, 11/1, микрорайон Ольгино, Балашиха, Московская область):')
        await state.set_state(AddCourt.address)
    await callback.answer()

@router.message(StateFilter(AddCourt.image_id), F.photo[-1].as_('largest_photo'))
async def process_photo_sent(message: Message,
                             state: FSMContext,
                             largest_photo: PhotoSize):
    """
    Хэнжлер
    """
    await state.update_data(image_id=largest_photo.file_id)
    await message.answer('Введите корректный адрес, как указано в примере(Граничная улица, 11/1, микрорайон Ольгино, Балашиха, Московская область):')
    await state.set_state(AddCourt.address)

@router.message(StateFilter(AddCourt.image_id))
async def warning_not_photo(message: Message):
    """
    as
    """
    await message.answer(text='На этом шаге отправьте '
                              'фото или нажмите на одну из кнопок!\n'
                              'Если вы хотите прервать '
                              'заполнение анкеты - отправьте команду /cancel(нажмите кнопку "🏠 Меню")')

@router.message(StateFilter(AddCourt.address), F.content_type == ContentType.TEXT)
async def add_court_address(message: Message, state: FSMContext):
    """
    Эта функция сохраняет адрес баскетбольной площадки и запрашивает координаты.
    """
    await state.update_data(address=message.text)
    geolocation_botton1: KeyboardButton = KeyboardButton(text='📍 Поделиться геолокацией',
                                                         request_location=True)
    geolocation_botton3: KeyboardButton = KeyboardButton(text='🗺️ Ввести координаты')
    geolocation_botton4: KeyboardButton = KeyboardButton(text='🫵🏼 Указать на карте')
    menu_botton: KeyboardButton = KeyboardButton(text=' 🏠 Меню')
    keyboard: ReplyKeyboardMarkup = ReplyKeyboardMarkup(keyboard=[[geolocation_botton1],
                                                                  [geolocation_botton3],
                                                                  [geolocation_botton4],
                                                                  [menu_botton]],
                                                        resize_keybord=True,
                                                        one_time_keybord=True)
    await message.answer(
        "И в заключительном шаге добавления корта нам понадобиться более точная геолокация для определения местопложения площадки,\n"
        "выберите удобный вам способ из предложенных кнопок:",
        reply_markup=keyboard)
    await state.set_state(AddCourt.latitude)

@router.message(F.content_type == ContentType.LOCATION, StateFilter(AddCourt.latitude))  # 'Поделиться геолокацией'
async def ad_court_address(message: Message, state: FSMContext):
    """
    Обработчик геопозиции новой площадки
    """
    await state.update_data(latitude=message.location.latitude)
    await state.update_data(longitude=message.location.longitude)

    # ПРОЦЕСС ОБРАЩЕНИЯ К АПИ GEOPY
    ctx = ssl._create_unverified_context(cafile=certifi.where())
    geopy.geocoders.options.default_ssl_context = ctx
    geolocator = Nominatim(user_agent='SetCourt', scheme='https')
    # geolocator = RateLimiter(geolocator.geocode, min_delay_seconds=1)
    # collisions['geocodes'] = collisions['location_string'].apply(geolocator)
    geo_str = str(message.location.latitude) + ", " + str(message.location.longitude)
    location = geolocator.reverse(geo_str)
    await state.update_data(address=location.address)

    user_data = await state.get_data()
    result_id = BotDB.add_court(user_data["user_id"], user_data["name"], user_data["image_id"],
                    user_data["address"], user_data["latitude"], user_data["longitude"])

    await state.clear()

    menu_botton: KeyboardButton = KeyboardButton(text=' 🏠 Меню')
    keyboard2: ReplyKeyboardMarkup = ReplyKeyboardMarkup(keyboard=[[menu_botton]],
                                                         resize_keybord=True)
    await message.answer(text='Отлично! Площадка успешно добавлена!',
                         reply_markup=keyboard2)

    if (user_data["image_id"] != user_data["user_id"]):
        await message.answer_photo(
            photo=user_data["image_id"],
            caption=f'Название площадки: {user_data["name"]}\n\n'
                    f'Адрес площадки: {user_data["address"]}\n\n'
                    f'Геолокация данной площадки:\n'
                    f'{user_data["latitude"]}, {user_data["longitude"]}\n\n',
            reply_murkup=keyboard2)
    else:
        await message.answer(
            text=f'Название площадки: {user_data["name"]}\n\n'
                 f'Адрес площадки: {user_data["address"]}\n\n'
                 f'Геолокация данной площадки:\n'
                 f'{user_data["latitude"]}, {user_data["longitude"]}\n\n',
            reply_murkup=keyboard2)

@router.message(Text(text=['🗺️ Ввести координаты']), StateFilter(AddCourt.latitude))
async def add_court_address(message: Message, state: FSMContext):
    menu_botton: KeyboardButton = KeyboardButton(text=' 🏠 Меню')
    keyboard2: ReplyKeyboardMarkup = ReplyKeyboardMarkup(keyboard=[[menu_botton]],
                                                         resize_keybord=True)
    await message.answer(text='Введите координаты данного корта,'
                              'как указано в примере(55.746999, 37.988368)',
                         reply_markup=keyboard2)
    await state.set_state(AddCourt.longitude)


@router.message(StateFilter(AddCourt.longitude), F.content_type == ContentType.TEXT)
async def add_court_coordinates(message: Message, state: FSMContext):
    menu_botton: KeyboardButton = KeyboardButton(text=' 🏠 Меню')
    keyboard2: ReplyKeyboardMarkup = ReplyKeyboardMarkup(keyboard=[[menu_botton]],
                                                         resize_keybord=True)
    try:
        lat, lng = message.text.split(',')
        lat, lng = float(lat.strip()), float(lng.strip())
        await state.update_data(latitude=lat)
        await state.update_data(longitude=lng)

        # ПРОЦЕСС ОБРАЩЕНИЯ К АПИ GEOPY
        ctx = ssl._create_unverified_context(cafile=certifi.where())
        geopy.geocoders.options.default_ssl_context = ctx
        geolocator = Nominatim(user_agent='SetCourt', scheme='https')
        # geolocator = RateLimiter(geolocator.geocode, min_delay_seconds=1)
        # collisions['geocodes'] = collisions['location_string'].apply(geolocator)
        geo_str = str(lat) + ", " + str(lng)
        location = geolocator.reverse(geo_str)
        await state.update_data(address=location.address)

        user_data = await state.get_data()
        result_id = BotDB.add_court(user_data["user_id"], user_data["name"], user_data["image_id"],
                                    user_data["address"], user_data["latitude"], user_data["longitude"])

        await state.clear()
        await message.answer(text='Отлично! Площадка успешно добавлена!')
        if (user_data["image_id"] != user_data["user_id"]):
            await message.answer_photo(
                photo=user_data["image_id"],
                caption=f'Название площадки: {user_data["name"]}\n\n'
                        f'Адрес площадки: {user_data["address"]}\n\n'
                        f'Геолокация данной площадки:\n'
                        f'{user_data["latitude"]}, {user_data["longitude"]}\n\n',
                reply_murkup=keyboard2)
        else:
            await message.answer(
                text=f'Название площадки: {user_data["name"]}\n\n'
                     f'Адрес площадки: {user_data["address"]}\n\n'
                     f'Геолокация данной площадки:\n'
                     f'{user_data["latitude"]}, {user_data["longitude"]}\n\n',
                reply_murkup=keyboard2)
        await state.clear()
    except ValueError:
        await message.reply(
            "Не валидный формат координат.\n"
            "Введите в таком формате: 40.7128, -74.0060")

@router.message(Text(text=['🫵🏼 Указать на карте']), StateFilter(AddCourt.latitude))
async def add_court_address(message: Message, state: FSMContext):
    menu_botton: KeyboardButton = KeyboardButton(text=' 🏠 Меню')
    keyboard2: ReplyKeyboardMarkup = ReplyKeyboardMarkup(keyboard=[[menu_botton]],
                                                         resize_keybord=True)
    await message.answer(
        text='1. Нажмите на скрепку 📎 рядом с окном ввода сообщения.\n'
             '2. Нажмите "Геопозиция".\n'
             '3. Выберите место на карте.\n'
             '4. Нажмите "Отправить выбранную геопозицию".\n',
        reply_murkup=keyboard2)
    await state.set_state(AddCourt.longitude)

@router.message(F.content_type == ContentType.LOCATION, StateFilter(AddCourt.longitude))  # Я НЕ ПРОВЕРЯЮ ПРАВИЛЬНОСТЬ АДРЕСА
async def ad_court_address(message: Message, state: FSMContext):
    """
    Обработчик геопозиции новой площадки
    """
    await state.update_data(latitude=message.location.latitude)
    await state.update_data(longitude=message.location.longitude)

    # ПРОЦЕСС ОБРАЩЕНИЯ К АПИ GEOPY
    ctx = ssl._create_unverified_context(cafile=certifi.where())
    geopy.geocoders.options.default_ssl_context = ctx
    geolocator = Nominatim(user_agent='SetCourt', scheme='https')
    # geolocator = RateLimiter(geolocator.geocode, min_delay_seconds=1)
    # collisions['geocodes'] = collisions['location_string'].apply(geolocator)
    geo_str = str(message.location.latitude) + ", " + str(message.location.longitude)
    location = geolocator.reverse(geo_str)
    await state.update_data(address=location.address)

    # print(geo_str)
    # print(location.address)

    user_data = await state.get_data()
    result_id = BotDB.add_court(user_data["user_id"], user_data["name"], user_data["image_id"],
                    user_data["address"], user_data["latitude"], user_data["longitude"])

    await state.clear()

    menu_botton: KeyboardButton = KeyboardButton(text=' 🏠 Меню')
    keyboard2: ReplyKeyboardMarkup = ReplyKeyboardMarkup(keyboard=[[menu_botton]],
                                                         resize_keybord=True)
    await message.answer(text='Отлично! Площадка успешно добавлена!',
                         reply_markup=keyboard2)

    await message.answer_photo(
        photo=user_data["image_id"],
        caption=f'Название площадки: {user_data["name"]}\n\n'
                f'Адрес площадки: {user_data["address"]}\n\n'
                f'Геолокация данной площадки:\n'
                f'{user_data["latitude"]}, {user_data["longitude"]}\n\n',
        reply_murkup=keyboard2)

# ПРОЦЕСС ПОИСКА БЛИЖАЙШЕЙ ПЛОЩАДКИ
class SearchCourt(StatesGroup):
    event=State()

@router.callback_query(Text(text=['court_search']), StateFilter(default_state))
async def process_search_court(callback: CallbackQuery, state: FSMContext):
    """
    Обработчик ....
    """
    menu_botton: KeyboardButton = KeyboardButton(text=' 🏠 Меню')
    geolocation_botton: KeyboardButton = KeyboardButton(text='📍 Поделиться геолокацией',
                                                        request_location=True)
    geolocation_botton3: KeyboardButton = KeyboardButton(text='🗺️ Ввести координаты')
    geolocation_botton4: KeyboardButton = KeyboardButton(text='🫵🏼 Указать на карте')
    keyboard: ReplyKeyboardMarkup = ReplyKeyboardMarkup(keyboard=[[geolocation_botton],
                                                                  [geolocation_botton3],
                                                                  [geolocation_botton4],
                                                                  [menu_botton]],
                                                        resize_keybord=True,
                                                        one_time_keybord=True)
    await callback.message.answer(
        "Для поиска ближайшей площадки мне понадобиться местоположение, относительно которого нужно искать.\n"
        "Вы можете поделиться своей геолокацией(соответсвенно поиск будет идти от вашего текущего местоположения), а также указать точное местоположение, "
        "указав на карте или введя данные координаты вручную:",
        reply_markup=keyboard)
    await state.set_state(SearchCourt.event)
    await callback.answer()

@router.message(Command(commands=['search_courts']), StateFilter(default_state))
async def process_search_court(message: Message, state: FSMContext):
    """
    Обработчик ....
    """
    menu_botton: KeyboardButton = KeyboardButton(text=' 🏠 Меню')
    geolocation_botton: KeyboardButton = KeyboardButton(text='📍 Поделиться геолокацией',
                                                        request_location=True)
    geolocation_botton3: KeyboardButton = KeyboardButton(text='🗺️ Ввести координаты')
    geolocation_botton4: KeyboardButton = KeyboardButton(text='🫵🏼 Указать на карте')
    keyboard: ReplyKeyboardMarkup = ReplyKeyboardMarkup(keyboard=[[geolocation_botton],
                                                                  [geolocation_botton3],
                                                                  [geolocation_botton4],
                                                                  [menu_botton]],
                                                        resize_keybord=True,
                                                        one_time_keybord=True)
    await message.answer(
        text="Для поиска ближайшей площадки мне понадобиться местоположение, относительно которого нужно искать.\n"
        "Вы можете поделиться своей геолокацией(соответсвенно поиск будет идти от вашего текущего местоположения), а также указать точное местоположение, "
        "указав на карте или введя данные координат вручную:\n",
        reply_markup=keyboard)
    await state.set_state(SearchCourt.event)

@router.message(Text(text='🗺️ Ввести координаты'), StateFilter(SearchCourt.event))
async def process_coord_point(message: Message, state: FSMContext):
    menu_botton: KeyboardButton = KeyboardButton(text=' 🏠 Меню')
    keyboard: ReplyKeyboardMarkup = ReplyKeyboardMarkup(keyboard=[[menu_botton]],
                                                        resize_keybord=True)
    await message.answer(text="Введите точные координаты согласно формату: широта, долгота(как в примере: 40.7128, -74.0060)",
                         reply_markup=keyboard)
    await state.set_state(SearchCourt.event)

@router.message(StateFilter(SearchCourt.event), F.content_type == ContentType.TEXT, ~Text(text='🫵🏼 Указать на карте'))
async def process_point_on_map(message: Message, state: FSMContext):
    try:
        lat, lng = message.text.split(',')
        lat, lng = float(lat.strip()), float(lng.strip())

        nearest_courts_data = BotDB.get_courts_nearby(lat, lng)
        menu_botton: KeyboardButton = KeyboardButton(text=' 🏠 Меню')
        keyboard: ReplyKeyboardMarkup = ReplyKeyboardMarkup(keyboard=[[menu_botton]],
                                                            resize_keybord=True)
        if (nearest_courts_data == None or nearest_courts_data == []):
            await message.answer(text='Прошу прощения, мне не удалось найти площадок по близости!',
                                 reply_markup=keyboard)
            await state.clear()
        else:
            users_db[message.from_user.id] = [[0], nearest_courts_data]
            data = users_db[message.from_user.id][1][users_db[message.from_user.id][0][0]]
            await message.answer_photo(
                photo=data[3],
                caption=f'Название площадки: {data[2]}\n\n'
                        f'Адрес площадки: {data[4]}\n\n'
                        f'Геолокация данной площадки: {data[5]}, {data[6]}\n\n'
                        f'Количество людей на данной площадке: {data[7]}\n\n'
                        f'В данный момент:\n'
                        f'  🟢 Новички: {data[8]}\n\n'
                        f'  🟡 Люители: {data[9]}\n\n'
                        f'  🔴 Профи: {data[10]}\n\n'
                        f'Средняя продолжительность занятия баскетболом: {data[11]} лет\n\n',
                reply_markup=pagination_kb.create_pagination_keyboard(
                    'backward',
                    f'{users_db[message.from_user.id][0][0] + 1}/{len(users_db[message.from_user.id][1])}',
                    'forward'))
            await state.set_state(SearchCourt.event)

    except ValueError:
        await message.reply(
            "Не валидный формат координат.\n"
            "Пожалуйста, введите в таком формате: 40.7128, -74.0060")


@router.message(Text(text='🫵🏼 Указать на карте'), StateFilter(SearchCourt.event))
async def process_point_on_map(message: Message, state: FSMContext):
    menu_botton: KeyboardButton = KeyboardButton(text=' 🏠 Меню')
    keyboard2: ReplyKeyboardMarkup = ReplyKeyboardMarkup(keyboard=[[menu_botton]],
                                                         resize_keybord=True)
    await message.answer(
        text='1. Нажмите на скрепку 📎 рядом с окном ввода сообщения.\n'
             '2. Нажмите "Геопозиция".\n'
             '3. Выберите место на карте.\n'
             '4. Нажмите "Отправить выбранную геопозицию".\n',
        reply_murkup=keyboard2)
    await state.set_state(SearchCourt.event)


@router.message(F.content_type == ContentType.LOCATION, StateFilter(SearchCourt.event)) # МОГ НЕ ПОЛУЧИТЬ
async def process_get_location(message: Message, state: FSMContext):
    """
    Обработчик ....
    """
    latitude = message.location.latitude
    longitude = message.location.longitude

    nearest_courts_data = BotDB.get_courts_nearby(latitude, longitude)
    menu_botton: KeyboardButton = KeyboardButton(text=' 🏠 Меню')
    keyboard: ReplyKeyboardMarkup = ReplyKeyboardMarkup(keyboard=[[menu_botton]],
                                                        resize_keybord=True)
    if (nearest_courts_data == None or nearest_courts_data == []):
        await message.answer(text='Прошу прощения, мне не удалось найти площадок по близости!',
                             reply_markup=keyboard)
        await state.clear()
    else:
        users_db[message.from_user.id] = [[0], nearest_courts_data]
        data = users_db[message.from_user.id][1][users_db[message.from_user.id][0][0]]
        await message.answer_photo(
            photo=data[3],
            caption=f'Название площадки: {data[2]}\n\n'
                    f'Адрес площадки: {data[4]}\n\n'
                    f'Геолокация данной площадки: {data[5]}, {data[6]}\n\n'
                    f'Количество людей на данной площадке: {data[7]}\n\n'
                    f'В данный момент:\n'
                    f'  🟢 Новички: {data[8]}\n\n'
                    f'  🟡 Люители: {data[9]}\n\n'
                    f'  🔴 Профи: {data[10]}\n\n'
                    f'Средняя продолжительность занятия баскетболом: {data[11]} лет\n\n',
            reply_markup=pagination_kb.create_pagination_keyboard(
                        'backward',
                        f'{users_db[message.from_user.id][0][0] + 1}/{len(users_db[message.from_user.id][1])}',
                        'forward'))
        await state.set_state(SearchCourt.event)

@router.callback_query(Text(text='forward'), StateFilter(SearchCourt.event))
async def process_forward_press(callback: CallbackQuery):
    """
    Этот хэндлер будет срабатывать на нажатие инлайн-кнопки "вперед"
    во время взаимодействия пользователя с сообщением-книгой
    """
    if users_db[callback.from_user.id][0][0] < len(users_db[callback.from_user.id][1]) - 1:
        users_db[callback.from_user.id][0][0] += 1
        data = users_db[callback.from_user.id][1][users_db[callback.from_user.id][0][0]]
        await callback.message.edit_media(
            media=InputMediaPhoto(
                media=data[3],
                caption=f'Название площадки: {data[2]}\n\n'
                        f'Адрес площадки: {data[4]}\n\n'
                        f'Геолокация данной площадки: {data[5]}, {data[6]}\n\n'
                        f'Количество людей на данной площадке: {data[7]}\n\n'
                        f'В данный момент:\n'
                        f'  🟢 Новички: {data[8]}\n\n'
                        f'  🟡 Люители: {data[9]}\n\n'
                        f'  🔴 Профи: {data[10]}\n\n'
                        f'Средняя продолжительность занятия баскетболом: {data[11]} лет\n\n'),
            reply_markup=pagination_kb.create_pagination_keyboard(
                'backward',
                f'{users_db[callback.from_user.id][0][0] + 1}/{len(users_db[callback.from_user.id][1])}',
                'forward'))
    await callback.answer()

@router.callback_query(Text(text='backward'), StateFilter(SearchCourt.event))
async def process_backward_press(callback: CallbackQuery):
    """
    Этот хэндлер будет срабатывать на нажатие инлайн-кнопки "назад"
    во время взаимодействия пользователя с сообщением-книгой
    """
    if users_db[callback.from_user.id][0][0] > 0:
        users_db[callback.from_user.id][0][0] -= 1
        data = users_db[callback.from_user.id][1][users_db[callback.from_user.id][0][0]]
        await callback.message.edit_media(
            media=InputMediaPhoto(
                media=data[3],
                caption=f'Название площадки: {data[2]}\n\n'
                        f'Адрес площадки: {data[4]}\n\n'
                        f'Геолокация данной площадки: {data[5]}, {data[6]}\n\n'
                        f'Количество людей на данной площадке: {data[7]}\n\n'
                        f'В данный момент:\n'
                        f'  🟢 Новички: {data[8]}\n\n'
                        f'  🟡 Люители: {data[9]}\n\n'
                        f'  🔴 Профи: {data[10]}\n\n'
                        f'Средняя продолжительность занятия баскетболом: {data[11]} лет\n\n'),
            reply_markup=pagination_kb.create_pagination_keyboard(
                'backward',
                f'{users_db[callback.from_user.id][0][0] + 1}/{len(users_db[callback.from_user.id][1])}',
                'forward'))
    await callback.answer()

# ПРОЦЕСС ДЕЙСТВИЯ С ИГРОЙ И МЕРОПРИЯТИЯМИ
@router.callback_query(Text(text='case_game'), StateFilter(default_state))
async def process_start_exit_game(callback: Message):
    stgame_botton: InlineKeyboardButton = InlineKeyboardButton(
        text='🏀 Начать игру',
        callback_data='start_game')
    exgame_botton: InlineKeyboardButton = InlineKeyboardButton(
        text='🙅🏿‍♂️ Прекратить игру',
        callback_data='exit_game')
    keyboard: InlineKeyboardMarkup = InlineKeyboardMarkup(
        inline_keyboard=[[stgame_botton],
                         [exgame_botton]])
    await callback.message.answer(
        text='В этом разделе вам доступны функции для того, чтобы присоединиться к игре на любом из кортов, '
             'а также выхода из нее, при условии если вы уже находитесь на корте:',
        reply_markup=keyboard)
    await callback.answer()

@router.callback_query(Text(text='case_game'), ~StateFilter(default_state))
async def process_start_exit_game(callback: Message):
    await callback.message.answer(
        text='Вы находитесь в процессе выполнения другого дейтсвия, кнопка "⚒️ Действия с игрой" не доступна!\n\n'
             'Для остановки заполнения, выполните команду "/cancel"(нажмите кнопку "🏠 Меню") или просто продолжайте согласно инструкциям!')

@router.callback_query(Text(text='case_event'), StateFilter(default_state))
async def process_start_exit_game(callback: Message):
    # set_event_botton: InlineKeyboardButton = InlineKeyboardButton(
    #     text='Назначить мероприятие',
    #     callback_data='set_event')
    start_event_botton: InlineKeyboardButton = InlineKeyboardButton(
        text='🏀 Начать мероприятие',
        callback_data='start_event')
    exit_event_botton: InlineKeyboardButton = InlineKeyboardButton(
        text='🙅🏿‍♂️ Заввершить мероприятие',
        callback_data='exit_event')
    edit_event_botton: InlineKeyboardButton = InlineKeyboardButton(
        text='🔖 Редактировать мероприятие',
        callback_data='edit_event')
    keyboard: InlineKeyboardMarkup = InlineKeyboardMarkup(
        inline_keyboard=[[start_event_botton],
                         [exit_event_botton],
                         [edit_event_botton]])
    await callback.message.answer(
        text='В этом разделе вам доступны функции для того, чтобы начать, завршить и редактировать мероприятие.\n'
             'Принудительно начинать или завершать мероприятие, выбор за вами.\n'
             'По умолчанию мероприятие начнется согласно той дате, которую вы укажите в процессе создания:',
        reply_markup=keyboard)

@router.callback_query(Text(text='case_event'), ~StateFilter(default_state))
async def process_start_exit_game(callback: Message):
    await callback.message.answer(
        text='Вы находитесь в процессе выполнения другого дейтсвия, кнопка "⚒️ Действия с мероприятием" не доступна!\n\n'
             'Для остановки заполнения, выполните команду "/cancel"(нажмите кнопку "🏠 Меню") или просто продолжайте согласно инструкциям!')

class StartEvent(StatesGroup):
    event=State()

@router.callback_query(Text(text='start_event'), StateFilter(default_state))
async def process_start_event(callback: CallbackQuery, state: FSMContext):
    all_events_by_admin = BotDB.get_all_events_by_admin(callback.from_user.id)
    if (all_events_by_admin == None or all_events_by_admin == []):
        await callback.message.answer(text='Вы до этого не создали ни одного мероприятия!')
    else:
        admin_events_db[callback.from_user.id] = [[0], all_events_by_admin]
        data = admin_events_db[callback.from_user.id][1][admin_events_db[callback.from_user.id][0][0]]
        player = "🔴 Профи"
        if (data[4] == 'lovely_play'):
            player = "🟢 Новичок"
        elif (data[4] == 'middle_play'):
            player = "🟡 Любитель"
        acs = "🔐 Закрытое мероприятие"
        if (data[3] == 'open_event'):
            acs = "🔓 Открытое мероприятие"
        await callback.message.answer(
            text=f'Мероприятие: {data[2]}\n\n'
                 f'Адрес мероприятия: {data[5]}\n\n'
                 f'Геолокация данного мероприятия: {data[6]}, {data[7]}\n\n'
                 f'Требуемый уровень: {player}\n\n'
                 f'Доступ: {acs}\n\n'
                 f'Дата и время начала: {data[8]} {data[9]}\n\n'
                 f'Описание: {data[10]}',
            reply_markup=pagination_kb.create_pagination_keyboard(
                'backwa',
                f'{admin_events_db[callback.from_user.id][0][0] + 1}/{len(admin_events_db[callback.from_user.id][1])}',
                'forwa'))
        await callback.message.answer(text='Вот все баскетбольные мероприятия, созданные вами!\n'
                                           'Нажав на кнопку по центру вы сможете принудительно начать его!')
        await state.set_state(StartEvent.event)
    await callback.answer()

@router.callback_query(Text(text='forwa'), StateFilter(StartEvent.event))
async def process_forward_press(callback: CallbackQuery, state: FSMContext):
    """
    Этот хэндлер будет срабатывать на нажатие инлайн-кнопки "вперед"
    во время взаимодействия пользователя с сообщением-книгой
    """
    if admin_events_db[callback.from_user.id][0][0] < len(admin_events_db[callback.from_user.id][1]) - 1:
        admin_events_db[callback.from_user.id][0][0] += 1
        data = admin_events_db[callback.from_user.id][1][admin_events_db[callback.from_user.id][0][0]]
        if (data[4] == 'lovely_play'):
            player = "🟢 Новичок"
        elif (data[4] == 'middle_play'):
            player = "🟡 Любитель"
        acs = "🔐 Закрытое мероприятие"
        if (data[3] == 'open_event'):
            acs = "🔓 Открытое мероприятие"
        await callback.message.edit_text(
            text=f'Мероприятие: {data[2]}\n\n'
                              f'Адрес мероприятия: {data[5]}\n\n'
                              f'Геолокация данного мероприятия: {data[6]}, {data[7]}\n\n'
                              f'Требуемый уровень: {player}\n\n'
                              f'Доступ: {acs}\n\n'
                              f'Дата и время начала: {data[8]} {data[9]}\n\n'
                              f'Описание: {data[10]}',
            reply_markup=pagination_kb.create_pagination_keyboard(
                'backwa',
                f'{admin_events_db[callback.from_user.id][0][0] + 1}/{len(admin_events_db[callback.from_user.id][1])}',
                'forwa'))
        await state.set_state(StartEvent.event)
    await callback.answer()

@router.callback_query(Text(text='backwa'), StateFilter(StartEvent.event))
async def process_backward_press(callback: CallbackQuery, state: FSMContext):
    """
    Этот хэндлер будет срабатывать на нажатие инлайн-кнопки "назад"
    во время взаимодействия пользователя с сообщением-книгой
    """
    if admin_events_db[callback.from_user.id][0][0] > 0:
        admin_events_db[callback.from_user.id][0][0] -= 1
        data = admin_events_db[callback.from_user.id][1][admin_events_db[callback.from_user.id][0][0]]
        if (data[4] == 'lovely_play'):
            player = "🟢 Новичок"
        elif (data[4] == 'middle_play'):
            player = "🟡 Любитель"
        acs = "🔐 Закрытое мероприятие"
        if (data[3] == 'open_event'):
            acs = "🔓 Открытое мероприятие"
        await callback.message.edit_text(
            text=f'Мероприятие: {data[2]}\n\n'
                              f'Адрес мероприятия: {data[5]}\n\n'
                              f'Геолокация данного мероприятия: {data[6]}, {data[7]}\n\n'
                              f'Требуемый уровень: {player}\n\n'
                              f'Доступ: {acs}\n\n'
                              f'Дата и время начала: {data[8]} {data[9]}\n\n'
                              f'Описание: {data[10]}',
            reply_markup=pagination_kb.create_pagination_keyboard(
                'backwa',
                f'{admin_events_db[callback.from_user.id][0][0] + 1}/{len(admin_events_db[callback.from_user.id][1])}',
                'forwa'))
        await state.set_state(StartEvent.event)
    await callback.answer()

@router.callback_query(lambda x: '/' in x.data and x.data.replace('/', '').isdigit(), StateFilter(StartEvent.event))
async def process_middle_press(callback: CallbackQuery, state: FSMContext):
    id = admin_events_db[callback.from_user.id][1][admin_events_db[callback.from_user.id][0][0]][0]
    BotDB.set_active_by_id(id)
    await callback.message.answer(text='Мероприятие переключено в активный режим!')
    await state.clear()
    await callback.answer()

class ExitEvent(StatesGroup):
    event=State()

@router.callback_query(Text(text='exit_event'), StateFilter(default_state))
async def process_finish_event(callback: CallbackQuery, state: FSMContext):
    all_events_by_admin = BotDB.get_all_events_by_admin(callback.from_user.id)
    if (all_events_by_admin == None or all_events_by_admin == []):
        await callback.message.answer(text='Вы до этого не создали ни одного мероприятия!')
    else:
        admin_events_db[callback.from_user.id] = [[0], all_events_by_admin]
        data = admin_events_db[callback.from_user.id][1][admin_events_db[callback.from_user.id][0][0]]
        player = "🔴 Профи"
        if (data[4] == 'lovely_play'):
            player = "🟢 Новичок"
        elif (data[4] == 'middle_play'):
            player = "🟡 Любитель"
        acs = "🔐 Закрытое мероприятие"
        if (data[3] == 'open_event'):
            acs = "🔓 Открытое мероприятие"
        await callback.message.answer(
            text=f'Мероприятие: {data[2]}\n\n'
                              f'Адрес мероприятия: {data[5]}\n\n'
                              f'Геолокация данного мероприятия: {data[6]}, {data[7]}\n\n'
                              f'Требуемый уровень: {player}\n\n'
                              f'Доступ: {acs}\n\n'
                              f'Дата и время начала: {data[8]} {data[9]}\n\n'
                              f'Описание: {data[10]}',
            reply_markup=pagination_kb.create_pagination_keyboard(
                'backwa',
                f'{admin_events_db[callback.from_user.id][0][0] + 1}/{len(admin_events_db[callback.from_user.id][1])}',
                'forwa'))
        await callback.message.answer(text='Вот все баскетбольные мероприятия, созданные вами!\n'
                                           'Нажав на кнопку по центру вы сможете принудительно завершить его!')
        await state.set_state(ExitEvent.event)
    await callback.answer()

@router.callback_query(Text(text='forwa'), StateFilter(ExitEvent.event))
async def process_forward_press(callback: CallbackQuery, state: FSMContext):
    """
    Этот хэндлер будет срабатывать на нажатие инлайн-кнопки "вперед"
    во время взаимодействия пользователя с сообщением-книгой
    """
    if admin_events_db[callback.from_user.id][0][0] < len(admin_events_db[callback.from_user.id][1]) - 1:
        admin_events_db[callback.from_user.id][0][0] += 1
        data = admin_events_db[callback.from_user.id][1][admin_events_db[callback.from_user.id][0][0]]
        if (data[4] == 'lovely_play'):
            player = "🟢 Новичок"
        elif (data[4] == 'middle_play'):
            player = "🟡 Любитель"
        acs = "🔐 Закрытое мероприятие"
        if (data[3] == 'open_event'):
            acs = "🔓 Открытое мероприятие"
        await callback.message.edit_text(
            text=f'Мероприятие: {data[2]}\n\n'
                              f'Адрес мероприятия: {data[5]}\n\n'
                              f'Геолокация данного мероприятия: {data[6]}, {data[7]}\n\n'
                              f'Требуемый уровень: {player}\n\n'
                              f'Доступ: {acs}\n\n'
                              f'Дата и время начала: {data[8]} {data[9]}\n\n'
                              f'Описание: {data[10]}',
            reply_markup=pagination_kb.create_pagination_keyboard(
                'backwa',
                f'{admin_events_db[callback.from_user.id][0][0] + 1}/{len(admin_events_db[callback.from_user.id][1])}',
                'forwa'))
        await state.set_state(ExitEvent.event)
    await callback.answer()

@router.callback_query(Text(text='backwa'), StateFilter(ExitEvent.event))
async def process_backward_press(callback: CallbackQuery, state: FSMContext):
    """
    Этот хэндлер будет срабатывать на нажатие инлайн-кнопки "назад"
    во время взаимодействия пользователя с сообщением-книгой
    """
    if admin_events_db[callback.from_user.id][0][0] > 0:
        admin_events_db[callback.from_user.id][0][0] -= 1
        data = admin_events_db[callback.from_user.id][1][admin_events_db[callback.from_user.id][0][0]]
        if (data[4] == 'lovely_play'):
            player = "🟢 Новичок"
        elif (data[4] == 'middle_play'):
            player = "🟡 Любитель"
        acs = "🔐 Закрытое мероприятие"
        if (data[3] == 'open_event'):
            acs = "🔓 Открытое мероприятие"
        await callback.message.edit_text(
            text=f'Мероприятие: {data[2]}\n\n'
                              f'Адрес мероприятия: {data[5]}\n\n'
                              f'Геолокация данного мероприятия: {data[6]}, {data[7]}\n\n'
                              f'Требуемый уровень: {player}\n\n'
                              f'Доступ: {acs}\n\n'
                              f'Дата и время начала: {data[8]} {data[9]}\n\n'
                              f'Описание: {data[10]}',
            reply_markup=pagination_kb.create_pagination_keyboard(
                'backwa',
                f'{admin_events_db[callback.from_user.id][0][0] + 1}/{len(admin_events_db[callback.from_user.id][1])}',
                'forwa'))
        await state.set_state(ExitEvent.event)
    await callback.answer()

@router.callback_query(lambda x: '/' in x.data and x.data.replace('/', '').isdigit(), StateFilter(ExitEvent.event))
async def process_middle_press(callback: CallbackQuery, state: FSMContext):
    id = admin_events_db[callback.from_user.id][1][admin_events_db[callback.from_user.id][0][0]][0]
    BotDB.set_disactive_by_id(id)
    await callback.message.answer(text='Мероприятие завершено!')
    await state.clear()
    await callback.answer()

class EditEvent(StatesGroup):
    event=State()

@router.callback_query(Text(text='edit_event'), StateFilter(default_state))
async def process_start_event(callback: CallbackQuery, state: FSMContext):
    update_event_botton: InlineKeyboardButton = InlineKeyboardButton(
        text='🧮 Изменить данные',
        callback_data='update_event')
    finish_event_botton: InlineKeyboardButton = InlineKeyboardButton(
        text='🙅🏿‍♂️ Удалить мероприятие',
        callback_data='delete_event')

    keyboard: InlineKeyboardMarkup = InlineKeyboardMarkup(
        inline_keyboard=[[update_event_botton],
                         [finish_event_botton]])
    await callback.message.answer(text='Что вы желаете изменить в вашем мероприятии?',
                                        reply_markup=keyboard)
    await state.set_state(EditEvent.event)
    await callback.answer()

@router.callback_query(Text(text='update_event'), StateFilter(EditEvent.event))
async def process_edit_event_edit_data(callback: CallbackQuery):
    await callback.answer()

class DeleteEvent(StatesGroup):
    event=State()

@router.callback_query(Text(text='delete_event'))
async def process_edit_event_delete(callback: CallbackQuery, state: FSMContext):
    all_events_by_admin = BotDB.get_all_events_by_admin(callback.from_user.id)
    if (all_events_by_admin == None or all_events_by_admin == []):
        await callback.message.answer(text='Вы до этого не создали ни одного мероприятия!')
    else:
        admin_events_db[callback.from_user.id] = [[0], all_events_by_admin]
        data = admin_events_db[callback.from_user.id][1][admin_events_db[callback.from_user.id][0][0]]
        player = "🔴 Профи"
        if (data[4] == 'lovely_play'):
            player = "🟢 Новичок"
        elif (data[4] == 'middle_play'):
            player = "🟡 Любитель"
        acs = "🔐 Закрытое мероприятие"
        if (data[3] == 'open_event'):
            acs = "🔓 Открытое мероприятие"
        await callback.message.answer(
            text=f'Мероприятие: {data[2]}\n\n'
                              f'Адрес мероприятия: {data[5]}\n\n'
                              f'Геолокация данного мероприятия: {data[6]}, {data[7]}\n\n'
                              f'Требуемый уровень: {player}\n\n'
                              f'Доступ: {acs}\n\n'
                              f'Дата и время начала: {data[8]} {data[9]}\n\n'
                              f'Описание: {data[10]}',
            reply_markup=pagination_kb.create_pagination_keyboard(
                'backw',
                f'{admin_events_db[callback.from_user.id][0][0] + 1}/{len(admin_events_db[callback.from_user.id][1])}',
                'forw'))
        await callback.message.answer(text='Вот все баскетбольные мероприятия, созданные вами!\n'
                                           'Нажав на кнопку по центру вы сможете удалить, выбранное мероприятие!')
        await state.set_state(DeleteEvent.event)
    await callback.answer()

@router.callback_query(Text(text='forw'), StateFilter(DeleteEvent.event))
async def process_forward_press(callback: CallbackQuery, state: FSMContext):
    """
    Этот хэндлер будет срабатывать на нажатие инлайн-кнопки "вперед"
    во время взаимодействия пользователя с сообщением-книгой
    """
    if admin_events_db[callback.from_user.id][0][0] < len(admin_events_db[callback.from_user.id][1]) - 1:
        admin_events_db[callback.from_user.id][0][0] += 1
        data = admin_events_db[callback.from_user.id][1][admin_events_db[callback.from_user.id][0][0]]
        if (data[4] == 'lovely_play'):
            player = "🟢 Новичок"
        elif (data[4] == 'middle_play'):
            player = "🟡 Любитель"
        acs = "🔐 Закрытое мероприятие"
        if (data[3] == 'open_event'):
            acs = "🔓 Открытое мероприятие"
        await callback.message.edit_text(
            text=f'Мероприятие: {data[2]}\n\n'
                              f'Адрес мероприятия: {data[5]}\n\n'
                              f'Геолокация данного мероприятия: {data[6]}, {data[7]}\n\n'
                              f'Требуемый уровень: {player}\n\n'
                              f'Доступ: {acs}\n\n'
                              f'Дата и время начала: {data[8]} {data[9]}\n\n'
                              f'Описание: {data[10]}',
            reply_markup=pagination_kb.create_pagination_keyboard(
                'backw',
                f'{admin_events_db[callback.from_user.id][0][0] + 1}/{len(admin_events_db[callback.from_user.id][1])}',
                'forw'))
        await state.set_state(DeleteEvent.event)
    await callback.answer()

@router.callback_query(Text(text='backw'), StateFilter(DeleteEvent.event))
async def process_backward_press(callback: CallbackQuery, state: FSMContext):
    """
    Этот хэндлер будет срабатывать на нажатие инлайн-кнопки "назад"
    во время взаимодействия пользователя с сообщением-книгой
    """
    if admin_events_db[callback.from_user.id][0][0] > 0:
        admin_events_db[callback.from_user.id][0][0] -= 1
        data = admin_events_db[callback.from_user.id][1][admin_events_db[callback.from_user.id][0][0]]
        if (data[4] == 'lovely_play'):
            player = "🟢 Новичок"
        elif (data[4] == 'middle_play'):
            player = "🟡 Любитель"
        acs = "🔐 Закрытое мероприятие"
        if (data[3] == 'open_event'):
            acs = "🔓 Открытое мероприятие"
        await callback.message.edit_text(
            text=f'Мероприятие: {data[2]}\n\n'
                              f'Адрес мероприятия: {data[5]}\n\n'
                              f'Геолокация данного мероприятия: {data[6]}, {data[7]}\n\n'
                              f'Требуемый уровень: {player}\n\n'
                              f'Доступ: {acs}\n\n'
                              f'Дата и время начала: {data[8]} {data[9]}\n\n'
                              f'Описание: {data[10]}',
            reply_markup=pagination_kb.create_pagination_keyboard(
                'backw',
                f'{admin_events_db[callback.from_user.id][0][0] + 1}/{len(admin_events_db[callback.from_user.id][1])}',
                'forw'))
        await state.set_state(DeleteEvent.event)
    await callback.answer()

@router.callback_query(lambda x: '/' in x.data and x.data.replace('/', '').isdigit(), StateFilter(DeleteEvent.event))
async def process_page_press(callback: CallbackQuery):
    id = admin_events_db[callback.from_user.id][1][admin_events_db[callback.from_user.id][0][0]][0]
    BotDB.delete_event_by_id(id)
    await callback.message.answer('Мероприятие успешно удалено!')
    await callback.answer()

# ПРОЦЕСС ЗАПУСКА/ЗАВЕРШЕНИЯ АКТИВНОГО БАСКЕТБОЛЬНОГО МЕРОПРИЯТИЯ

@router.callback_query(Text(text=['start_game']), StateFilter(default_state))
async def process_start_game(callback: CallbackQuery, state: FSMContext):
    """
    Хэндлер
    """
    menu_botton: KeyboardButton = KeyboardButton(text=' 🏠 Меню')
    geolocation_botton: KeyboardButton = KeyboardButton(text='📍 Поделиться геолокацией',
                                                        request_location=True)
    keyboard: ReplyKeyboardMarkup = ReplyKeyboardMarkup(keyboard=[[geolocation_botton],
                                                                  [menu_botton]],
                                                        resize_keybord=True,
                                                        one_time_keybord=True)
    await callback.message.answer('Оу, вы уже дошли до площадки? Это превосходно, а теперь отметьте для остальных,'
                                  'что вы находитесь на этом корте, для этого надо поделится геопозицией, так как мне необходимо знать, что вы находитесь на площадке:',
                                  reply_markup=keyboard)
    await state.set_state(AddGame.latitude)
    await callback.answer()

@router.message(Command(commands=['start_game']), StateFilter(default_state))
async def process_start_game(message: Message, state: FSMContext):
    """
    Хэндлер
    """
    menu_botton: KeyboardButton = KeyboardButton(text=' 🏠 Меню')
    geolocation_botton: KeyboardButton = KeyboardButton(text='📍 Поделиться геолокацией',
                                                        request_location=True)
    keyboard: ReplyKeyboardMarkup = ReplyKeyboardMarkup(keyboard=[[geolocation_botton],
                                                                  [menu_botton]],
                                                        resize_keybord=True,
                                                        one_time_keybord=True)
    await message.answer('Оу, вы уже дошли до площадки? Это превосходно, а теперь отметьте для остальных,'
                         'что вы находитесь на этом корте, для этого надо поделится геопозицией, так как мне необходимо знать, что вы находитесь на площадке:',
                         reply_markup=keyboard)
    await state.set_state(AddGame.latitude)

@router.message(StateFilter(AddGame.latitude))
async def process_set_active(message: Message, state: FSMContext):
    """
    Hendler ...
    """
    await state.update_data(latitude=message.location.latitude)
    await state.update_data(longitude=message.location.longitude)

    user_data = await state.get_data()
    search_result = BotDB.get_nearest_court(user_data["latitude"], user_data["longitude"])
    if (search_result == None):
        await message.answer('По всей видимости, вы еще не рядом с площадкой!')
    else:
        await state.update_data(result_court_id=search_result["id"])

        yes_botton: InlineKeyboardButton = InlineKeyboardButton(
            text='Да, эта площадка!\n'
                 'Начать игру!',
            callback_data='yes_court')
        not_botton: InlineKeyboardButton = InlineKeyboardButton(
            text='Не, это другая!',
            callback_data='not_court')

        keyboard: InlineKeyboardMarkup = InlineKeyboardMarkup(
            inline_keyboard=[[yes_botton, not_botton]])

        await message.answer_photo(
            photo=search_result["image_id"],
            caption=f'Имя площадки: {search_result["name"]}\n\n'
                    f'Адрес площадки: {search_result["address"]}\n\n'
                    f'Геолокация данной площадки: {search_result["latitude"]}, {search_result["longitude"]}\n\n'
                    f'Количество людей на данной площадке: {search_result["players"]}\n\n'
                    f'В данный момент:\n'
                    f'  🟢 Новички: {search_result["green_player"]}\n\n'
                    f'  🟡 Люители: {search_result["yellow_player"]}\n\n'
                    f'  🔴 Профи: {search_result["red_player"]}\n\n'
                    f'Средняя продолжительность занятия баскетболом: {search_result["years"]} лет\n\n',
            reply_markup=keyboard)

        await state.set_state(AddGame.result_court_id)

@router.callback_query(Text(text=['yes_court', 'not_court']), StateFilter(AddGame.result_court_id))
async def process_agreeting_court(callback: CallbackQuery, state: FSMContext):
    if (callback.data == ['not_court']):
        await callback.message.answer('Видимо, вы искали другой корт!')
    else:
        court_data = await state.get_data()
        BotDB.add_player_on_court(callback.from_user.id, court_data["result_court_id"])
        await callback.message.answer(text='Отлично, теперь все знают что вы на этой площадке!\n'
                                      'Когда вы закончите играть, просто нажмите на кнопку "🙅🏿‍♂️ Прекратить игру" или '
                                      'выполните команду "/exit_game", и вы сможете продолжить использование этого бота\n')
    await callback.answer()
    # await state.clear()

@router.callback_query(~Text(text=['exit_game']), StateFilter(AddGame.result_court_id))
async def process_exit_game(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer('Вы еще находитесь на игре!')

@router.message(~Command(commands=['exit_game']), StateFilter(AddGame.result_court_id))
async def process_exit_game(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer('Вы еще находитесь на игре!')

@router.callback_query(Text(text=['exit_game']), StateFilter(AddGame.result_court_id))
async def process_exit_game(callback: CallbackQuery, state: FSMContext):
    """
    Хэндлер для принудительного завершения участия в баскетбольном мероприятии
    """
    court_data = await state.get_data()
    BotDB.exit_player_from_court(callback.message.from_user.id, court_data["result_court_id"])
    await callback.message.answer('Превосходно, теперь все знают, что на этой площадке на одного прекрасного игрока стало меньше!')
    await state.clear()
    await callback.answer()

@router.message(Command(commands=['exit_game']), StateFilter(AddGame.result_court_id))
async def process_exit_game(message: Message, state: FSMContext):
    """
    Хэндлер для принудительного завершения участия в баскетбольном мероприятии
    """
    court_data = await state.get_data()
    BotDB.exit_player_from_court(message.from_user.id, court_data["result_court_id"])
    await message.answer('Превосходно, теперь все знают, что на этой площадке на одного прекрасного игрока стало меньше!')
    await state.clear()

@router.callback_query(Text(text=['exit_game']), ~StateFilter(AddGame.result_court_id))
async def cannot_exit_game(callback: CallbackQuery):
    await callback.message.answer('Вы еще не начинали играть!\n'
                                  'Воспользуйся кнопкой "🏀 Начать игру"(или командой /start_game)')
    await callback.answer()

@router.message(Command(commands=['exit_game']), ~StateFilter(AddGame.result_court_id))
async def cannot_exit_game(message: Message):
    await message.answer('Вы еще не начинали играть!\n'
                         'Воспользуйся кнопкой "🏀 Начать игру"(или командой /start_game)')

# ПРОЦЕСС ЛИЧНОГО КАБИНЕТА
@router.callback_query(Text(text=['personal_area']), StateFilter(default_state))
async def open_personal_area(callback: CallbackQuery):
    if (BotDB.user_exists(callback.from_user.id) != False):
        # favcourts_botton: InlineKeyboardButton = InlineKeyboardButton(
        #     text=' ❤︎ Мои площадки',
        #     callback_data='courts_me')
        # review_botton: InlineKeyboardButton = InlineKeyboardButton(
        #     text=' 📜 Мои отзывы',
        #     callback_data='review_me')
        area_botton: InlineKeyboardButton = InlineKeyboardButton(
            text=' 🙍🏿‍♂️ Профиль',
            callback_data='personal_me')
        keyboard: InlineKeyboardMarkup = InlineKeyboardMarkup(
            inline_keyboard=[[area_botton]])  # [favcourts_botton] [review_botton]
        await callback.message.answer(
            text='Ваш личный кабинет:',
            reply_markup=keyboard)
    else:
        reg_botton: InlineKeyboardButton = InlineKeyboardButton(
            text='🤝🏼 Познакомится',
            callback_data='user_registration')
        canc_botton: InlineKeyboardButton = InlineKeyboardButton(
            text='🙅🏽 Отмена',
            callback_data='cancel_registration')
        keyboard: InlineKeyboardMarkup = InlineKeyboardMarkup(
            inline_keyboard=[[reg_botton, canc_botton]])
        await callback.message.answer(text='Вы еще не прошли регистрацию!\n'
                                           'Желаете пройти?',
                                      reply_markup=keyboard)
    await callback.answer()

@router.callback_query(Text(text=['personal_area']), ~StateFilter(default_state))
async def open_personal_area(callback: CallbackQuery):
    await callback.message.answer('Вы находитесь в процессе заполнения! Выйдите в меню или просто продолжите!')
    await callback.answer()

@router.callback_query(Text(text=['personal_me']), StateFilter(default_state))
async def open_profil(callback: CallbackQuery):
    about_botton: InlineKeyboardButton = InlineKeyboardButton(
        text='Обо мне',
        callback_data='about_me')
    social_botton: InlineKeyboardButton = InlineKeyboardButton(
        text='Соц. сети',
        callback_data='social_me')
    number_botton: InlineKeyboardButton = InlineKeyboardButton(
        text='Телефон',
        callback_data='number_me')
    photo_botton: InlineKeyboardButton = InlineKeyboardButton(
        text='Фото',
        callback_data='photo_me')

    keyboard: InlineKeyboardMarkup = InlineKeyboardMarkup(
        inline_keyboard=[[about_botton],
                         [social_botton],
                         [number_botton],
                         [photo_botton]])
    await callback.message.answer(
        text='Ваш личная информация:',
        reply_markup=keyboard)

    await callback.answer()


# ПРОЦЕСС НАЗНАЧЕНИЯ БАСКЕТБОЛЬНОГО МЕРОПРИЯТИЯ НА ОПРЕДЕЛЕННУЮ ДАТУ
class AddEvent(StatesGroup):
    admin_id=State()
    eventname=State()
    acsess=State()
    levels=State()
    address=State()
    latitude=State()
    longitude=State()
    date=State()
    time=State()
    description=State()

@router.message(Command(commands=['set_event']), StateFilter(default_state))
async def process_set_event(message: Message, state: FSMContext):
    """

    """
    await message.answer(text='Для того, чтобы назначить баскетбольное мероприятие, мне от вас потребуется '
                              'уточняющая информация о том, где будет проводиться, когда и какой статус!')
    await message.answer(text='Придумайте название для своего басктбольного меропритяия:')
    await state.set_state(AddEvent.eventname)

@router.callback_query(Text(text=['set_event']), StateFilter(default_state))
async def process_set_event(callback: CallbackQuery, state: FSMContext):
    """

    """
    await callback.message.answer(text='Для того, чтобы назначить баскетбольное мероприятие, мне от вас потребуется '
                                       'уточняющая информация о том, где будет проводиться, когда и какой статус!')
    await callback.message.answer(text='Придумайте название для своего басктбольного меропритяия:')
    await state.set_state(AddEvent.eventname)
    await callback.answer()

@router.message(StateFilter(AddEvent.eventname), F.text.isalpha())
async def process_name_event(message: Message, state: FSMContext):
    await state.update_data(admin_id=message.from_user.id)
    await state.update_data(eventname=message.text)

    open_event_botton: InlineKeyboardButton = InlineKeyboardButton(
        text='🔓 Открытое!',
        callback_data='open_event')
    close_event_botton: InlineKeyboardButton = InlineKeyboardButton(
        text='🔐 Закрытое!',
        callback_data='close_event')

    keyboard: InlineKeyboardMarkup = InlineKeyboardMarkup(
        inline_keyboard=[[open_event_botton, close_event_botton]])

    await message.answer(text='Это закрытое или открытое мероприятие:',
                         reply_markup=keyboard)
    await state.set_state(AddEvent.acsess)

@router.message(StateFilter(AddEvent.eventname))
async def process_name_event(message: Message, state: FSMContext):
    await message.answer('Вы ввели некорректное имя, используйте ТОЛЬКО буквенные символы!')


@router.callback_query(Text(text=['open_event', 'close_event']), StateFilter(AddEvent.acsess))
async def process_acsess_event(callback: CallbackQuery, state: FSMContext):
    await state.update_data(acsess=callback.data)

    love_botton: InlineKeyboardButton = InlineKeyboardButton(
        text='Новичок',
        callback_data='lovely_play')
    middle_botton: InlineKeyboardButton = InlineKeyboardButton(
        text='Любитель',
        callback_data='middle_play')
    extra_botton: InlineKeyboardButton = InlineKeyboardButton(
        text='Профи',
        callback_data='extra_play')
    keyboard: InlineKeyboardMarkup = InlineKeyboardMarkup(
        inline_keyboard=[[love_botton],
                         [middle_botton],
                         [extra_botton]])

    await callback.message.answer(text='Допустимый уровень игроков:',
                                  reply_markup=keyboard)
    await state.set_state(AddEvent.levels)
    await callback.answer()

@router.callback_query(Text(text=['lovely_play', 'middle_play', 'extra_play']), StateFilter(AddEvent.levels))
async def process_levels_event(callback: CallbackQuery, state: FSMContext):
    await state.update_data(levels=callback.data)

    geolocation_botton1: KeyboardButton = KeyboardButton(text='📍 Поделиться геолокацией',
                                                         request_location=True)
    geolocation_botton3: KeyboardButton = KeyboardButton(text='🗺️ Ввести координаты')
    geolocation_botton4: KeyboardButton = KeyboardButton(text='🫵🏼 Указать на карте')
    menu_botton: KeyboardButton = KeyboardButton(text=' 🏠 Меню')
    keyboard: ReplyKeyboardMarkup = ReplyKeyboardMarkup(keyboard=[[geolocation_botton1],
                                                                  [geolocation_botton3],
                                                                  [geolocation_botton4],
                                                                  [menu_botton]],
                                                        resize_keybord=True,
                                                        one_time_keybord=True)
    await callback.message.answer(text='Выберите удобный способ для предоставления будущего местоположения этого мероприятия 👇🏻',
                                  reply_markup=keyboard)
    await state.set_state(AddEvent.address)
    await callback.answer()

@router.message(F.content_type == ContentType.LOCATION, StateFilter(AddEvent.address))
async def ad_court_address(message: Message, state: FSMContext):
    """
    Обработчик геопозиции новой площадки
    """
    await state.update_data(latitude=message.location.latitude)
    await state.update_data(longitude=message.location.longitude)

    # API NAMINATIM GEOPY
    ctx = ssl._create_unverified_context(cafile=certifi.where())
    geopy.geocoders.options.default_ssl_context = ctx
    geolocator = Nominatim(user_agent='SetCourt', scheme='https')
    geo_str = str(message.location.latitude) + ", " + str(message.location.longitude)
    location = geolocator.reverse(geo_str)

    await state.update_data(address=location.address)

    menu_botton: KeyboardButton = KeyboardButton(text=' 🏠 Меню')
    keyboard2: ReplyKeyboardMarkup = ReplyKeyboardMarkup(keyboard=[[menu_botton]],
                                                         resize_keybord=True)
    await message.answer(text='Напишите дату проведения как в примере: 12.01.1965(день.месяц.год)',
                         reply_markup=keyboard2)
    await state.set_state(AddEvent.date)

@router.message(Text(text='🗺️ Ввести координаты'), StateFilter(AddEvent.address))
async def add_court_address(message: Message, state: FSMContext):
    menu_botton: KeyboardButton = KeyboardButton(text=' 🏠 Меню')
    keyboard2: ReplyKeyboardMarkup = ReplyKeyboardMarkup(keyboard=[[menu_botton]],
                                                         resize_keybord=True)
    await message.answer(text='Введите координаты данного корта,'
                              'как указано в примере: 55.746999, 37.988368 (широта, долгота)',
                         reply_markup=keyboard2)
    await state.set_state(AddEvent.latitude)

@router.message(StateFilter(AddEvent.latitude), F.content_type == ContentType.TEXT)
async def add_court_coordinates(message: Message, state: FSMContext):
    menu_botton: KeyboardButton = KeyboardButton(text=' 🏠 Меню')
    keyboard2: ReplyKeyboardMarkup = ReplyKeyboardMarkup(keyboard=[[menu_botton]],
                                                         resize_keybord=True)
    try:
        lat, lng = message.text.split(',')
        lat, lng = float(lat.strip()), float(lng.strip())
        await state.update_data(latitude=lat)
        await state.update_data(longitude=lng)

        ctx = ssl._create_unverified_context(cafile=certifi.where())
        geopy.geocoders.options.default_ssl_context = ctx
        geolocator = Nominatim(user_agent='SetCourt', scheme='https')
        geo_str = str(message.location.latitude) + ", " + str(message.location.longitude)
        location = geolocator.reverse(geo_str)

        await state.update_data(address=location.address)

        await message.answer(text='Напишите дату проведения как в примере: 12.01.1965 (день.месяц.год)',
                             reply_markup=keyboard2)

        await state.set_state(AddEvent.date)

    except ValueError:
        await message.reply(
            "Не валидный формат координат.\n"
            "Пожалуйста, введите в таком формате: 40.7128, -74.0060")

@router.message(Text(text='🫵🏼 Указать на карте'), StateFilter(AddEvent.address))
async def add_court_address(message: Message, state: FSMContext):
    menu_botton: KeyboardButton = KeyboardButton(text=' 🏠 Меню')
    keyboard2: ReplyKeyboardMarkup = ReplyKeyboardMarkup(keyboard=[[menu_botton]],
                                                         resize_keybord=True)
    await message.answer(
        text='1. Нажмите на скрепку 📎 рядом с окном ввода сообщения.\n'
             '2. Нажмите "Геопозиция".\n'
             '3. Выберите место на карте.\n'
             '4. Нажмите "Отправить выбранную геопозицию".\n',
        reply_murkup=keyboard2)
    await state.set_state(AddEvent.longitude)

@router.message(F.content_type == ContentType.LOCATION, StateFilter(AddEvent.longitude))  # Я НЕ ПРОВЕРЯЮ ПРАВИЛЬНОСТЬ АДРЕСА
async def ad_court_address(message: Message, state: FSMContext):
    """
    Обработчик геопозиции новой площадки
    """
    await state.update_data(latitude=message.location.latitude)
    await state.update_data(longitude=message.location.longitude)

    # ПРОЦЕСС ОБРАЩЕНИЯ К АПИ GEOPY
    ctx = ssl._create_unverified_context(cafile=certifi.where())
    geopy.geocoders.options.default_ssl_context = ctx
    geolocator = Nominatim(user_agent='SetCourt', scheme='https')
    # geolocator = RateLimiter(geolocator.geocode, min_delay_seconds=1)
    # collisions['geocodes'] = collisions['location_string'].apply(geolocator)
    geo_str = str(message.location.latitude) + ", " + str(message.location.longitude)
    location = geolocator.reverse(geo_str)

    await state.update_data(address=location.address)

    menu_botton: KeyboardButton = KeyboardButton(text=' 🏠 Меню')
    keyboard2: ReplyKeyboardMarkup = ReplyKeyboardMarkup(keyboard=[[menu_botton]],
                                                         resize_keybord=True)

    await message.answer(text='Напишите дату проведения как в примере: 12.01.1965 (день.месяц.год)',
                         reply_markup=keyboard2)
    await state.set_state(AddEvent.date)

@router.message(StateFilter(AddEvent.date))
async def add_data_event(message: Message, state: FSMContext):
    await state.update_data(date=message.text)

    await message.answer(text='Напишите время начала как указано в примере: 12:00 или 18:45')
    await state.set_state(AddEvent.time)

@router.message(StateFilter(AddEvent.time))
async def add_time_event(message: Message, state: FSMContext):
    await state.update_data(time=message.text)

    await message.answer(text='Напишите описание к своему баскетбольному мероприятию:')
    await state.set_state(AddEvent.description)

@router.message(StateFilter(AddEvent.description), F.content_type == ContentType.TEXT)
async def add_description_event(message: Message, state: FSMContext):
    await state.update_data(description=message.text)
    user_data = await state.get_data()
    BotDB.add_basketball_event(user_data["admin_id"],
                               user_data["eventname"],
                               user_data["acsess"],
                               user_data["levels"],
                               user_data["address"],
                               user_data["latitude"],
                               user_data["longitude"],
                               user_data["date"],
                               user_data["time"],
                               user_data["description"])
    await message.answer(text='Мероприятие успешно добавлено')
    player = "🔴 Профи"
    if (user_data["levels"] == 'lovely_play'):
        player = "🟢 Новичок"
    elif (user_data["levels"] == 'middle_play'):
        player = "🟡 Любитель"
    acs = "🔐 Закрытое мероприятие"
    if (user_data["acsess"] == 'open_event'):
        acs = "🔓 Открытое мероприятие"
    await message.answer(text=f'Мероприятие: {user_data["eventname"]}\n\n'
                              f'Адрес мероприятия: {user_data["address"]}\n\n'
                              f'Геолокация данного мероприятия: {user_data["latitude"]}, {user_data["longitude"]}\n\n'
                              f'Требуемый уровень: {player}\n\n'
                              f'Доступ: {acs}\n\n'
                              f'Дата и время начала: {user_data["date"]} {user_data["time"]}\n\n'
                              f'Описание: {user_data["description"]}')
    await state.clear()

# ПРОЦЕСС ПОИСКА МЕРОПРИЯТИЙ
class SearchEvents(StatesGroup):
    event=State()

@router.callback_query(Text(text='search_events'), StateFilter(default_state))
async def get_events(callback: CallbackQuery, state: FSMContext):
    all_events = BotDB.get_all_events()
    if (all_events != []):
        events_db[callback.from_user.id] = [[0], all_events]
        data = events_db[callback.from_user.id][1][events_db[callback.from_user.id][0][0]]
        player = "🔴 Профи"
        if (data[4] == 'lovely_play'):
            player = "🟢 Новичок"
        elif (data[4] == 'middle_play'):
            player = "🟡 Любитель"
        acs = "🔐 Закрытое мероприятие"
        if (data[3] == 'open_event'):
            acs = "🔓 Открытое мероприятие"
        await callback.message.answer(
            text=f'Мероприятие: {data[2]}\n\n'
                                  f'Адрес мероприятия: {data[5]}\n\n'
                                  f'Геолокация данного мероприятия: {data[6]}, {data[7]}\n\n'
                                  f'Требуемый уровень: {player}\n\n'
                                  f'Доступ: {acs}\n\n'
                                  f'Дата и время начала: {data[8]} {data[9]}\n\n'
                                  f'Описание: {data[10]}',
            reply_markup=pagination_kb.create_pagination_keyboard(
                'backwar',
                f'{events_db[callback.from_user.id][0][0] + 1}/{len(events_db[callback.from_user.id][1])}',
                'forwar'))
        await callback.message.answer(text='Нажав на центральную кнопку вы сможете зарегистрироваться на это мероприятие!')
        await state.set_state(SearchEvents.event)
    else:
        await callback.message.answer('Инициированных мероприятий в данный момент нет!')
    await callback.answer()

@router.callback_query(Text(text='forwar'), StateFilter(SearchEvents.event))
async def process_forward_press(callback: CallbackQuery, state: FSMContext):
    """
    Этот хэндлер будет срабатывать на нажатие инлайн-кнопки "вперед"
    во время взаимодействия пользователя с сообщением-книгой
    """
    if events_db[callback.from_user.id][0][0] < len(events_db[callback.from_user.id][1]) - 1:
        events_db[callback.from_user.id][0][0] += 1
        data = events_db[callback.from_user.id][1][events_db[callback.from_user.id][0][0]]
        if (data[4] == 'lovely_play'):
            player = "🟢 Новичок"
        elif (data[4] == 'middle_play'):
            player = "🟡 Любитель"
        acs = "🔐 Закрытое мероприятие"
        if (data[3] == 'open_event'):
            acs = "🔓 Открытое мероприятие"
        await callback.message.edit_text(
            text=f'Мероприятие: {data[2]}\n\n'
                                  f'Адрес мероприятия: {data[5]}\n\n'
                                  f'Геолокация данного мероприятия: {data[6]}, {data[7]}\n\n'
                                  f'Требуемый уровень: {player}\n\n'
                                  f'Доступ: {acs}\n\n'
                                  f'Дата и время начала: {data[8]} {data[9]}\n\n'
                                  f'Описание: {data[10]}',
            reply_markup=pagination_kb.create_pagination_keyboard(
                'backwar',
                f'{events_db[callback.from_user.id][0][0] + 1}/{len(events_db[callback.from_user.id][1])}',
                'forwar'))
        # await callback.message.answer(
        #     text='Нажав на центральную кнопку вы сможете зарегистрироваться на это мероприятие!')
    await callback.answer()

@router.callback_query(Text(text='backwar'), StateFilter(SearchEvents.event))
async def process_backward_press(callback: CallbackQuery, state: FSMContext):
    """
    Этот хэндлер будет срабатывать на нажатие инлайн-кнопки "назад"
    во время взаимодействия пользователя с сообщением-книгой
    """
    if events_db[callback.from_user.id][0][0] > 0:
        events_db[callback.from_user.id][0][0] -= 1
        data = events_db[callback.from_user.id][1][events_db[callback.from_user.id][0][0]]
        if (data[4] == 'lovely_play'):
            player = "🟢 Новичок"
        elif (data[4] == 'middle_play'):
            player = "🟡 Любитель"
        acs = "🔐 Закрытое мероприятие"
        if (data[3] == 'open_event'):
            acs = "🔓 Открытое мероприятие"
        await callback.message.edit_text(
            text=f'Мероприятие: {data[2]}\n\n'
                                  f'Адрес мероприятия: {data[5]}\n\n'
                                  f'Геолокация данного мероприятия: {data[6]}, {data[7]}\n\n'
                                  f'Требуемый уровень: {player}\n\n'
                                  f'Доступ: {acs}\n\n'
                                  f'Дата и время начала: {data[8]} {data[9]}\n\n'
                                  f'Описание: {data[10]}',
            reply_markup=pagination_kb.create_pagination_keyboard(
                'backwar',
                f'{events_db[callback.from_user.id][0][0] + 1}/{len(events_db[callback.from_user.id][1])}',
                'forwar'))
        # await callback.message.answer(
        #     text='Нажав на центральную кнопку вы сможете зарегистрироваться на это мероприятие!')
    await callback.answer()

@router.callback_query(lambda x: '/' in x.data and x.data.replace('/', '').isdigit(), StateFilter(SearchEvents.event))
async def process_middle_presed(callback: CallbackQuery, state: FSMContext):
    if (BotDB.user_exists(callback.from_user.id) == False):
        reg_botton: InlineKeyboardButton = InlineKeyboardButton(
            text='🤝🏼 Познакомится',
            callback_data='user_registration')
        canc_botton: InlineKeyboardButton = InlineKeyboardButton(
            text='🙅🏽 Отмена',
            callback_data='cancel_registration')
        keyboard: InlineKeyboardMarkup = InlineKeyboardMarkup(
            inline_keyboard=[[reg_botton, canc_botton]])
        await callback.message.answer(text='Вы еще не зарегистрированы как новый пользователь в боте!\n'
                                           'Но вы можете сделать это сейчас:',
                                      reply_markup=keyboard)
    else:
        user_info = BotDB.get_info_about_user(callback.from_user.id)
        # events_db[callback.from_user.id] = [[0], all_events]
        event_level = events_db[callback.from_user.id][1][events_db[callback.from_user.id][0][0]][4]
        event_id = events_db[callback.from_user.id][1][events_db[callback.from_user.id][0][0]][0]
        print(event_id)
        if (event_level != user_info[4]):
            await callback.message.answer(text='Уровень игры не соответствует нужному!')
        else:
            BotDB.add_player_on_event(callback.message.from_user.id, event_id)
            await callback.message.answer(text='Вы успешно зарегистрированы!')
    await state.clear()
    await callback.answer()


@router.message()
async def procces_handl_another_messages(message: Message):
    """
    Обработка всех остальных сообщений
    """
    menu_botton: KeyboardButton = KeyboardButton(text=' 🏠 Меню')
    keyboard2: ReplyKeyboardMarkup = ReplyKeyboardMarkup(keyboard=[[menu_botton]],
                                                         resize_keybord=True)
    await message.answer(text='Ваш запрос мне не понятен!',
                         reply_markup=keyboard2)
