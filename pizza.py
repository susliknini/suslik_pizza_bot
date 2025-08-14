import random
from datetime import datetime
from aiogram import Bot, Dispatcher, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, InputFile
from aiogram.utils import executor
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.contrib.fsm_storage.memory import MemoryStorage
import asyncio

TOKEN = "5000385710:AAHSXXCT4S4MafwbG7e2yZ6hmg4KiXDG-ZI"  
ADMIN_IDS = [5000673123]  
BOT_USERNAME = "SuslikPizzaBot"  
VIP_PHRASE = "пицца - @SuslikPizza"
CHANNEL_USERNAME = "@SuslikPizza"  
CHANNEL_ID = -1001234567890  

promo_text = None
users_db = {}
vip_users = set()
orders_history = []

STYLES = {
    "header": "🍕 <b>{text}</b> �,
    "warning": "⚠️ <i>{text}</i>",
    "success": "✅ <b>{text}</b>",
    "vip": "🌟 {text}",
    "admin": "👑 {text}",
    "delivery": "🚚 {text}",
    "pizza": "🍕 {text}",
    "love": "❤️ {text}",
    "channel": "📢 {text}"
}

PIZZA_TYPES = {
    "Маргарита": ["томатный соус", "моцарелла", "базилик"],
    "Пепперони": ["томатный соус", "моцарелла", "пепперони"],
    "Гавайская": ["томатный соус", "моцарелла", "ветчина", "ананасы"],
    "4 Сыра": ["сливочный соус", "моцарелла", "пармезан", "дор блю", "чеддер"],
    "Мясная": ["томатный соус", "моцарелла", "пепперони", "ветчина", "бекон"],
    "Веган": ["томатный соус", "тофу", "грибы", "оливки", "перец"]
}

PIZZA_PROGRESS = [
    ("🧑‍🍳 Начали готовить вашу пиццу...", 0),
    ("🫓 Раскатываем тесто...", 15),
    ("🍅 Добавляем томатный соус...", 25),
    ("🧀 Щедро сыпем сыр...", 40),
    ("🍖 Кладем начинку...", 55),
    ("🌶️ Добавляем специи...", 65),
    ("🔥 Отправляем в печь...", 75),
    ("🔍 Проверяем готовность...", 85),
    ("📦 Упаковываем...", 90),
    ("🛵 Передаем курьеру...", 100)
]

bot = Bot(token=TOKEN, parse_mode="HTML")
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)

class OrderStates(StatesGroup):
    waiting_for_address = State()
    waiting_for_pizza_type = State()

class AdminStates(StatesGroup):
    waiting_for_broadcast = State()
    waiting_for_promo = State()
    waiting_for_ad = State()

def create_keyboard(buttons, row_width=2):
    keyboard = InlineKeyboardMarkup(row_width=row_width)
    keyboard.add(*buttons)
    return keyboard

def get_main_menu(user_id: int):
    buttons = [
        InlineKeyboardButton("🍕 Меню", callback_data="menu"),
        InlineKeyboardButton("🛒 Заказать", callback_data="order"),
        InlineKeyboardButton("👤 Профиль", callback_data="profile"),
        InlineKeyboardButton("ℹ️ О сервисе", callback_data="about")
    ]
    if user_id in ADMIN_IDS:
        buttons.append(InlineKeyboardButton("👑 Админ-панель", callback_data="admin_panel"))
    return create_keyboard(buttons)

def get_pizza_menu():
    buttons = [
        InlineKeyboardButton(f"{name}", callback_data=f"pizza_{name}") 
        for name in PIZZA_TYPES.keys()
    ]
    buttons.append(InlineKeyboardButton("🔙 Назад", callback_data="back"))
    return create_keyboard(buttons)

def get_admin_panel():
    buttons = [
        InlineKeyboardButton("📢 Рассылка", callback_data="broadcast"),
        InlineKeyboardButton("📝 Промо-текст", callback_data="set_promo"),
        InlineKeyboardButton("📊 Статистика", callback_data="stats"),
        InlineKeyboardButton("📨 Реклама", callback_data="create_ad"),
        InlineKeyboardButton("❌ Удалить промо", callback_data="remove_promo"),
        InlineKeyboardButton("🔙 Назад", callback_data="back")
    ]
    return create_keyboard(buttons, row_width=1)

def get_back_button():
    return InlineKeyboardMarkup().add(InlineKeyboardButton("🔙 Назад", callback_data="back"))

def get_channel_subscription_keyboard():
    return InlineKeyboardMarkup().add(
        InlineKeyboardButton("Подписаться на канал", url=f"https://t.me/{CHANNEL_USERNAME[1:]}")
    ).add(
        InlineKeyboardButton("Я подписался ✅", callback_data="check_subscription")
    )

def format_message(style, text, **kwargs):
    return STYLES[style].format(text=text, **kwargs)

def check_vip_status(user: types.User):
    try:
        return hasattr(user, 'bio') and user.bio and VIP_PHRASE.lower() in user.bio.lower()
    except:
        return False

async def check_channel_subscription(user_id: int):
    try:
        member = await bot.get_chat_member(CHANNEL_ID, user_id)
        return member.status in ['member', 'administrator', 'creator']
    except:
        return False

async def update_user(user: types.User):
    user_id = user.id
    is_vip = check_vip_status(user)
    
    if user_id not in users_db:
        users_db[user_id] = {
            'name': user.full_name,
            'username': user.username,
            'registration_date': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'orders_count': 0,
            'is_vip': is_vip,
            'vip_since': datetime.now().strftime("%Y-%m-%d %H:%M:%S") if is_vip else None,
            'favorite_pizza': None
        }
    
    if is_vip and not users_db[user_id]['is_vip']:
        users_db[user_id]['is_vip'] = True
        users_db[user_id]['vip_since'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        if user.username:
            vip_users.add(user.username.lower())
        return True
    
    return False

@dp.message_handler(commands=['start', 'pizza'])
async def handle_commands(message: types.Message):
    user = message.from_user
    chat_type = message.chat.type
    
    if chat_type == 'private':
        is_subscribed = await check_channel_subscription(user.id)
        if not is_subscribed:
            await message.answer(
                format_message("channel", "Для использования бота необходимо подписаться на наш канал!") + "\n\n" +
                f"Канал: {CHANNEL_USERNAME}",
                reply_markup=get_channel_subscription_keyboard()
            )
            return
    
    vip_updated = await update_user(user)
    
    if message.text.startswith('/pizza') and chat_type != 'private':
        parts = message.text.split(maxsplit=1)
        if len(parts) > 1:
            await process_group_order(message, parts[1].strip())
        else:
            await message.reply(
                format_message("warning", "Укажите адрес: /pizza [адрес]") + 
                "\nПример: <code>/pizza ул. Пушкина 15, кв. 42</code>"
            )
        return
    
    welcome_text = format_message("header", "Suslik Pizza - лучшая пицца в городе!") + "\n\n"
    welcome_text += format_message("pizza", "Доставка с любовью!") + "\n\n"
    welcome_text += format_message("vip", f"Добавь в био '{VIP_PHRASE}' для VIP статуса")
    
    if vip_updated:
        welcome_text += "\n\n" + format_message("vip", "Поздравляем! Вы получили VIP статус!")
    
    try:
        await message.answer_photo(
            InputFile('start.jpg'),
            caption=welcome_text,
            reply_markup=get_main_menu(user.id)
        )
    except:
        await message.answer(
            welcome_text,
            reply_markup=get_main_menu(user.id)
        )
    
    if chat_type == 'private':
        await message.delete()

@dp.callback_query_handler(lambda c: c.data == 'check_subscription')
async def check_subscription_callback(callback_query: types.CallbackQuery):
    await bot.answer_callback_query(callback_query.id)
    
    is_subscribed = await check_channel_subscription(callback_query.from_user.id)
    if is_subscribed:
        await handle_commands(callback_query.message)
    else:
        await callback_query.message.answer(
            format_message("warning", "Вы ещё не подписались на канал!"),
            reply_markup=get_channel_subscription_keyboard()
        )

@dp.callback_query_handler(lambda c: c.data.startswith('pizza_'))
async def handle_pizza_selection(callback_query: types.CallbackQuery, state: FSMContext):
    pizza_type = callback_query.data[6:]
    await bot.answer_callback_query(callback_query.id)
    
    await bot.send_message(
        callback_query.from_user.id,
        format_message("header", f"Вы выбрали: {pizza_type}") + "\n" +
        format_message("pizza", f"Состав: {', '.join(PIZZA_TYPES[pizza_type])}") + "\n\n" +
        format_message("delivery", "Теперь введите адрес доставки:"),
        reply_markup=get_back_button()
    )
    
    async with state.proxy() as data:
        data['pizza_type'] = pizza_type
    
    await OrderStates.waiting_for_address.set()

@dp.callback_query_handler(lambda c: c.data in ['menu', 'order', 'profile', 'about', 'admin_panel', 'broadcast', 'back', 'stats', 'set_promo', 'create_ad', 'remove_promo'])
async def handle_callbacks(callback_query: types.CallbackQuery, state: FSMContext):
    await bot.answer_callback_query(callback_query.id)
    user_id = callback_query.from_user.id
    
    if callback_query.data not in ['back', 'about']:
        is_subscribed = await check_channel_subscription(user_id)
        if not is_subscribed:
            await callback_query.message.answer(
                format_message("channel", "Для использования бота необходимо подписаться на наш канал!") + "\n\n" +
                f"Канал: {CHANNEL_USERNAME}",
                reply_markup=get_channel_subscription_keyboard()
            )
            return
    
    if callback_query.data == 'menu':
        await show_menu(callback_query)
    elif callback_query.data == 'order':
        await start_order(callback_query)
    elif callback_query.data == 'profile':
        await show_profile(callback_query)
    elif callback_query.data == 'about':
        await show_about(callback_query)
    elif callback_query.data == 'admin_panel' and user_id in ADMIN_IDS:
        await show_admin_panel(callback_query)
    elif callback_query.data == 'broadcast' and user_id in ADMIN_IDS:
        await start_broadcast(callback_query, state)
    elif callback_query.data == 'stats' and user_id in ADMIN_IDS:
        await show_stats(callback_query)
    elif callback_query.data == 'set_promo' and user_id in ADMIN_IDS:
        await set_promo_text(callback_query, state)
    elif callback_query.data == 'create_ad' and user_id in ADMIN_IDS:
        await create_advertisement(callback_query, state)
    elif callback_query.data == 'remove_promo' and user_id in ADMIN_IDS:
        await remove_promo_text(callback_query)
    elif callback_query.data == 'back':
        await back_to_main(callback_query)

async def show_menu(callback_query: types.CallbackQuery):
    menu_text = format_message("header", "Наше меню") + "\n\n"
    for name, ingredients in PIZZA_TYPES.items():
        menu_text += f"<b>{name}</b>\n🍽️ {', '.join(ingredients)}\n\n"
    
    await bot.send_message(
        callback_query.from_user.id,
        menu_text,
        reply_markup=get_back_button()
    )

async def start_order(callback_query: types.CallbackQuery):
    await bot.send_message(
        callback_query.from_user.id,
        format_message("header", "Выберите тип пиццы:"),
        reply_markup=get_pizza_menu()
    )

async def show_profile(callback_query: types.CallbackQuery):
    user_id = callback_query.from_user.id
    user_data = users_db.get(user_id, {})
    
    profile_text = format_message("header", "Ваш профиль") + "\n\n"
    profile_text += f"👤 Имя: {user_data.get('name', 'Неизвестно')}\n"
    profile_text += f"📅 Регистрация: {user_data.get('registration_date', 'Неизвестно')}\n"
    profile_text += f"🛒 Заказов: {user_data.get('orders_count', 0)}\n"
    
    if user_data.get('is_vip'):
        profile_text += format_message("vip", f"VIP статус с {user_data.get('vip_since')}") + "\n"
    
    await bot.send_message(
        user_id,
        profile_text,
        reply_markup=get_back_button()
    )

async def show_about(callback_query: types.CallbackQuery):
    about_text = format_message("header", "О нашем сервисе") + "\n\n"
    about_text += format_message("pizza", "Мы готовим пиццу с любовью!") + "\n"
    about_text += format_message("delivery", "Быстрая доставка по всему городу") + "\n\n"
    about_text += format_message("vip", f"Добавьте в био '{VIP_PHRASE}' для VIP статуса")
    
    await bot.send_message(
        callback_query.from_user.id,
        about_text,
        reply_markup=get_back_button()
    )

async def show_admin_panel(callback_query: types.CallbackQuery):
    await bot.send_message(
        callback_query.from_user.id,
        format_message("admin", "Админ-панель") + "\n" +
        f"👥 Пользователей: {len(users_db)}\n" +
        f"🛒 Заказов: {len(orders_history)}",
        reply_markup=get_admin_panel()
    )

async def show_stats(callback_query: types.CallbackQuery):
    await bot.send_message(
        callback_query.from_user.id,
        format_message("admin", "Статистика") + "\n" +
        f"👥 Пользователей: {len(users_db)}\n" +
        f"🛒 Заказов: {len(orders_history)}\n" +
        f"🌟 VIP: {sum(user['is_vip'] for user in users_db.values())}",
        reply_markup=get_admin_panel()
    )

async def back_to_main(callback_query: types.CallbackQuery):
    await bot.send_message(
        callback_query.from_user.id,
        format_message("header", "Главное меню"),
        reply_markup=get_main_menu(callback_query.from_user.id)
    )

async def start_broadcast(callback_query: types.CallbackQuery, state: FSMContext):
    await bot.send_message(
        callback_query.from_user.id,
        format_message("admin", "Введите текст рассылки:"),
        reply_markup=get_back_button()
    )
    await AdminStates.waiting_for_broadcast.set()

async def set_promo_text(callback_query: types.CallbackQuery, state: FSMContext):
    await bot.send_message(
        callback_query.from_user.id,
        format_message("admin", "Введите текст для промо-подписи:"),
        reply_markup=get_back_button()
    )
    await AdminStates.waiting_for_promo.set()

async def create_advertisement(callback_query: types.CallbackQuery, state: FSMContext):
    await bot.send_message(
        callback_query.from_user.id,
        format_message("admin", "Отправьте рекламное сообщение:"),
        reply_markup=get_back_button()
    )
    await AdminStates.waiting_for_ad.set()

async def remove_promo_text(callback_query: types.CallbackQuery):
    global promo_text
    promo_text = None
    await bot.send_message(
        callback_query.from_user.id,
        format_message("success", "Промо-подпись удалена!"),
        reply_markup=get_admin_panel()
    )

@dp.message_handler(state=AdminStates.waiting_for_broadcast)
async def process_broadcast(message: types.Message, state: FSMContext):
    await message.answer(
        format_message("success", "Рассылка завершена!"),
        reply_markup=get_admin_panel()
    )
    await state.finish()

@dp.message_handler(state=AdminStates.waiting_for_promo)
async def process_promo_text(message: types.Message, state: FSMContext):
    global promo_text
    promo_text = message.text
    await message.answer(
        format_message("success", "Промо-подпись сохранена!"),
        reply_markup=get_admin_panel()
    )
    await state.finish()

@dp.message_handler(state=AdminStates.waiting_for_ad)
async def process_advertisement(message: types.Message, state: FSMContext):
    await message.answer(
        format_message("success", "Реклама отправлена!"),
        reply_markup=get_admin_panel()
    )
    await state.finish()

async def process_group_order(message: types.Message, address: str):
    user = message.from_user
    user_id = user.id
    
    if user_id not in users_db:
        await update_user(user)
    
    pizza_type = random.choice(list(PIZZA_TYPES.keys()))
    is_vip = users_db[user_id].get('is_vip', False)
    
    progress_msg = await send_pizza_progress(
        message.chat.id,
        users_db[user_id]['name'],
        address,
        pizza_type,
        is_vip
    )
    
    orders_history.append({
        'user_id': user_id,
        'address': address,
        'pizza_type': pizza_type,
        'is_vip': is_vip,
        'date': datetime.now()
    })
    
    await complete_order(
        message.chat.id,
        progress_msg,
        users_db[user_id]['name'],
        address,
        random.randint(1, 10),
        pizza_type,
        is_vip
    )

@dp.message_handler(state=OrderStates.waiting_for_address)
async def process_private_order(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    address = message.text
    
    async with state.proxy() as data:
        pizza_type = data.get('pizza_type')
    
    is_vip = users_db[user_id].get('is_vip', False)
    
    progress_msg = await send_pizza_progress(
        message.chat.id,
        users_db[user_id]['name'],
        address,
        pizza_type,
        is_vip
    )
    
    orders_history.append({
        'user_id': user_id,
        'address': address,
        'pizza_type': pizza_type,
        'is_vip': is_vip,
        'date': datetime.now()
    })
    
    await complete_order(
        message.chat.id,
        progress_msg,
        users_db[user_id]['name'],
        address,
        random.randint(1, 10),
        pizza_type,
        is_vip
    )
    await state.finish()

async def send_pizza_progress(chat_id, user_name, address, pizza_type, is_vip=False):
    progress_message = await bot.send_message(
        chat_id,
        format_message("delivery", f"Заказ для {user_name}")
    )
    
    for step, percent in PIZZA_PROGRESS:
        text = f"{step} {percent}%\n"
        text += f"📍 Адрес: {address}\n"
        text += f"🍕 Пицца: {pizza_type}\n"
        if is_vip:
            text += format_message("vip", "VIP заказ!")
        
        await bot.edit_message_text(
            text,
            chat_id,
            progress_message.message_id
        )
        await asyncio.sleep(0.5)
    
    return progress_message.message_id

async def complete_order(chat_id, message_id, user_name, address, count, pizza_type, is_vip=False):
    text = format_message("success", f"Заказ готов! {user_name}") + "\n"
    text += f"🍕 Количество: {count}\n"
    text += f"📍 Адрес: {address}\n"
    
    if is_vip:
        text += "\n" + format_message("vip", "Спасибо за VIP статус!")
    
    if promo_text:
        text += "\n" + format_message("pizza", promo_text)
    
    await bot.edit_message_text(
        text,
        chat_id,
        message_id,
        reply_markup=get_main_menu(chat_id) if chat_id > 0 else None
    )

if __name__ == '__main__':
    print("Бот запущен!")
    executor.start_polling(dp, skip_updates=True)
