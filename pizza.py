import asyncio
import logging
import os
import time
from datetime import datetime
from typing import List, Tuple

from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, FSInputFile
from telethon import TelegramClient
from telethon.tl.functions.messages import ReportRequest
from telethon.tl.types import InputPeerChannel, InputReportReasonSpam

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Конфигурация
API_ID = '24463378'
API_HASH = 'e7c3fb1d6c2a8b3a9422607a350754c1'
BOT_TOKEN = '8290891253:AAFbnBJPgjiUUOzeGANjDonOQWRAhSi2ni4'

ADMIN_IDS = [8075123058]  # ID администраторов
SUPPORT_ID = 1637959612  # ID техподдержки

# Инициализация бота
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# Глобальные переменные
order_counter = 1
sessions_folder = "sessions"
active_reports = {}

# Клавиатура
main_keyboard = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="🟢 Донос", callback_data="report")],
    [InlineKeyboardButton(text="👤 Профиль", callback_data="profile")],
    [InlineKeyboardButton(text="💎 Поддержать проект", callback_data="donate")],
    [InlineKeyboardButton(text="🛠 Тех поддержка", callback_data="support")]
])

# Загрузка сессий Telethon
def load_sessions() -> List[TelegramClient]:
    clients = []
    if not os.path.exists(sessions_folder):
        os.makedirs(sessions_folder)
    
    for file in os.listdir(sessions_folder):
        if file.endswith('.session'):
            session_path = os.path.join(sessions_folder, file[:-8])
            try:
                client = TelegramClient(session_path, API_ID, API_HASH)
                clients.append(client)
            except Exception as e:
                logger.error(f"Ошибка загрузки сессии {file}: {e}")
    
    return clients

# Функция для отправки жалобы
async def send_report(client: TelegramClient, message_link: str) -> Tuple[bool, str]:
    try:
        if 't.me/' in message_link:
            parts = message_link.split('/')
            if len(parts) >= 2:
                channel_username = parts[-2]
                message_id = int(parts[-1])
                
                entity = await client.get_entity(channel_username)
                peer = InputPeerChannel(entity.id, entity.access_hash)
                
                await client(ReportRequest(
                    peer=peer,
                    id=[message_id],
                    reason=InputReportReasonSpam(),
                    message="Спам"
                ))
                
                return True, "ДОСТАВЛЕНО"
                
    except Exception as e:
        error_msg = str(e)
        if "FLOOD" in error_msg.upper():
            return False, "ФЛУД"
        elif "AUTH" in error_msg.upper() or "SESSION" in error_msg.upper():
            return False, "НЕВАЛИД"
        else:
            # Обрезаем длинные ошибки
            if len(error_msg) > 50:
                error_msg = error_msg[:47] + "..."
            return False, f"ОШИБКА: {error_msg}"
    
    return False, "НЕВАЛИД"

# Обработчик команды /start
@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    await message.answer(
        "👋 Привет! SuslikPizza лучшая доставка в городе Санкт-Петербург (суслико ландивмф)! 🍕",
        reply_markup=main_keyboard
    )

# Обработчик кнопки "Донос"
@dp.callback_query(F.data == "report")
async def report_handler(callback: types.CallbackQuery):
    await callback.message.answer("📩 Введите ссылку на сообщение из публичного  чатаа с нарушением:")
    active_reports[callback.from_user.id] = "waiting_link"
    await callback.answer()

# Обработчик ввода ссылки
@dp.message(F.text.contains("t.me/"))
async def process_link(message: types.Message):
    if message.from_user.id not in active_reports:
        return
    
    link = message.text.strip()
    user_id = message.from_user.id
    global order_counter
    
    # Создаем лог файл
    log_filename = f"SuslikPizza_log{order_counter}.txt"
    order_counter += 1
    
    with open(log_filename, 'w', encoding='utf-8') as log_file:
        log_file.write(f"SuslikPizza log | botnet-method\n")
        log_file.write("-" * 42 + "\n")
        log_file.write(f"Пользователь: {message.from_user.id} (@{message.from_user.username})\n")
        log_file.write(f"Ссылка: {link}\n")
        log_file.write("-" * 42 + "\n")
    
    await message.answer("🚀 Начинаю отправку жалоб...")
    
    clients = load_sessions()
    successful = 0
    failed = 0
    floods = 0
    
    for client in clients:
        for i in range(5):
            try:
                async with client:
                    result, status = await send_report(client, link)
                    current_time = datetime.now().strftime("%H:%M:%S")
                    session_name = os.path.basename(client.session.filename)
                    
                    log_entry = f"[{current_time}] {session_name} -> {link} - [{status}]\n"
                    
                    with open(log_filename, 'a', encoding='utf-8') as log_file:
                        log_file.write(log_entry)
                    
                    if status == "ДОСТАВЛЕНО":
                        successful += 1
                    elif status == "ФЛУД":
                        floods += 1
                    else:
                        failed += 1
                    
                    await asyncio.sleep(3)
                    
            except Exception as e:
                current_time = datetime.now().strftime("%H:%M:%S")
                session_name = os.path.basename(client.session.filename) if client else "unknown"
                error_msg = str(e)
                if len(error_msg) > 50:
                    error_msg = error_msg[:47] + "..."
                log_entry = f"[{current_time}] {session_name} -> {link} - [ОШИБКА: {error_msg}]\n"
                
                with open(log_filename, 'a', encoding='utf-8') as log_file:
                    log_file.write(log_entry)
                
                failed += 1
                logger.error(f"Ошибка: {e}")
    
    # Записываем итоги
    with open(log_filename, 'a', encoding='utf-8') as log_file:
        log_file.write("-" * 42 + "\n")
        log_file.write(f"Успешно: {successful}\n")
        log_file.write(f"Неуспешно: {failed}\n")
        log_file.write(f"Флудов: {floods}\n")
    
    # Отправляем лог пользователю
    try:
        document = FSInputFile(log_filename)
        await message.answer_document(
            document,
            caption=f"📊 Отчет готов!\n"
                   f"✅ Успешно: {successful}\n"
                   f"❌ Неуспешно: {failed}\n"
                   f"🌊 Флудов: {floods}"
        )
    except Exception as e:
        logger.error(f"Ошибка отправки файла пользователю: {e}")
        await message.answer(
            f"📊 Отчет готов!\n"
            f"✅ Успешно: {successful}\n"
            f"❌ Неуспешно: {failed}\n"
            f"🌊 Флудов: {floods}\n"
            f"⚠️ Файл не отправлен: {e}"
        )
    
    # Отправляем лог админам
    for admin_id in ADMIN_IDS:
        try:
            document = FSInputFile(log_filename)
            await bot.send_document(
                admin_id,
                document,
                caption=f"📋 Новый отчет от @{message.from_user.username}\n"
                       f"👤 ID: {message.from_user.id}"
            )
        except Exception as e:
            logger.error(f"Ошибка отправки файла админу {admin_id}: {e}")
    
    # Удаляем временный файл
    try:
        os.remove(log_filename)
    except:
        pass
    
    del active_reports[user_id]

# Обработчик кнопки "Профиль"
@dp.callback_query(F.data == "profile")
async def profile_handler(callback: types.CallbackQuery):
    user = callback.from_user
    profile_text = (
        f"👤 Ваш профиль:\n"
        f"🆔 ID: {user.id}\n"
        f"📛 Username: @{user.username}\n"
        f"👀 Имя: {user.first_name} {user.last_name or ''}"
    )
    await callback.message.answer(profile_text)
    await callback.answer()

# Обработчик кнопки "Тех поддержка"
@dp.callback_query(F.data == "support")
async def support_handler(callback: types.CallbackQuery):
    await callback.message.answer("📝 Опишите вашу проблему:")
    active_reports[callback.from_user.id] = "waiting_support"
    await callback.answer()

# Обработчик обращения в поддержку
@dp.message(F.text)
async def process_support(message: types.Message):
    if message.from_user.id not in active_reports:
        return
    
    if active_reports[message.from_user.id] == "waiting_support":
        support_text = (
            f"🆘 Новое обращение в поддержку:\n"
            f"👤 От: @{message.from_user.username}\n"
            f"🆔 ID: {message.from_user.id}\n"
            f"📝 Текст:\n{message.text}"
        )
        
        for admin_id in ADMIN_IDS + [SUPPORT_ID]:
            try:
                await bot.send_message(admin_id, support_text)
            except Exception as e:
                logger.error(f"Ошибка отправки сообщения админу {admin_id}: {e}")
        
        await message.answer("✅ Ваше обращение отправлено в поддержку!")
        del active_reports[message.from_user.id]

# Обработчик кнопки "Поддержать проект"
@dp.callback_query(F.data == "donate")
async def donate_handler(callback: types.CallbackQuery):
    await callback.message.answer(
        "💎 Поддержать проект можно по ссылке:\n"
        "https://t.me/send?start=IV2HJyZJ6rrz\n\n"
        "🙏 Спасибо за вашу поддержку! 💖"
    )
    await callback.answer()

# Запуск бота
async def main():
    if not os.path.exists(sessions_folder):
        os.makedirs(sessions_folder)
        logger.info(f"Создана папка {sessions_folder}")
    
    logger.info("✅ Бот запущен!")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
