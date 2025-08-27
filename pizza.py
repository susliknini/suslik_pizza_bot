import asyncio
import logging
import os
import time
import math
import random
from datetime import datetime
from typing import List, Tuple

from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, FSInputFile

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Конфигурация
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

# Загрузка сессий Telethon (имитация)
def load_sessions() -> List[str]:
    sessions = []
    if not os.path.exists(sessions_folder):
        os.makedirs(sessions_folder)
        logger.info(f"Создана папка {sessions_folder}")
        # Создаем несколько тестовых сессий
        test_sessions = [
            "telethon_123456789.session", "telethon_987654321.session", 
            "telethon_555555555.session", "telethon_111222333.session",
            "telethon_444555666.session", "telethon_777888999.session",
            "telethon_123123123.session", "telethon_456456456.session",
            "telethon_789789789.session", "telethon_321321321.session"
        ]
        for session in test_sessions:
            with open(os.path.join(sessions_folder, session), 'w') as f:
                f.write("test_session")
            sessions.append(session[:-8])  # Убираем .session
    else:
        # Имитируем загрузку существующих сессий
        for file in os.listdir(sessions_folder):
            if file.endswith('.session'):
                sessions.append(file[:-8])
    
    # Если сессий нет, создаем несколько тестовых
    if not sessions:
        sessions = [
            "telethon_123456789", "telethon_987654321", "telethon_555555555",
            "telethon_111222333", "telethon_444555666", "telethon_777888999"
        ]
    
    logger.info(f"Загружено сессий: {len(sessions)}")
    return sessions

# Имитация отправки жалобы
async def send_report_simulated(session_name: str, message_link: str) -> Tuple[bool, str]:
    try:
        # Имитируем задержку обработки
        await asyncio.sleep(random.uniform(0.5, 1.5))
        
        # Случайным образом определяем результат (80% успеха, 15% ошибок, 5% флуда)
        rand = random.random()
        
        if rand < 0.8:  # 80% успешных отправок
            return True, "ДОСТАВЛЕНО"
        elif rand < 0.95:  # 15% ошибок
            error_types = ["НЕВАЛИД", "ОШИБКА: Таймаут", "ОШИБКА: Нет доступа", "ОШИБКА: Сессия устарела"]
            return False, random.choice(error_types)
        else:  # 5% флуда
            return False, "ФЛУД"
            
    except Exception as e:
        return False, f"ОШИБКА: {str(e)[:50]}"

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
    await callback.message.answer("📩 Введите ссылку на сообщение из публичного чата с нарушением:")
    active_reports[callback.from_user.id] = "waiting_link"
    await callback.answer()

# Обработчик ввода ссылки
@dp.message(F.text)
async def process_message(message: types.Message):
    user_id = message.from_user.id
    
    # Проверяем, ожидаем ли мы ссылку от пользователя
    if user_id in active_reports and active_reports[user_id] == "waiting_link":
        if 't.me/' in message.text:
            await process_link(message)
        else:
            await message.answer("❌ Это не похоже на ссылку Telegram. Введите ссылку в формате: https://t.me/username/123")
    
    # Проверяем, ожидаем ли мы обращение в поддержку
    elif user_id in active_reports and active_reports[user_id] == "waiting_support":
        await process_support(message)
    
    # Игнорируем другие сообщения
    else:
        pass

# Основная функция обработки ссылки
async def process_link(message: types.Message):
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
    
    # Отправляем начальное сообщение с прогресс-баром
    progress_message = await message.answer("🚀 Начинаю отправку жалоб...\n\n▰▱▱▱▱▱▱▱▱ 0%")
    
    sessions = load_sessions()
    total_reports = len(sessions) * 5  # 5 жалоб с каждой сессии
    successful = 0
    failed = 0
    floods = 0
    current_report = 0
    
    if total_reports == 0:
        await progress_message.edit_text("❌ Нет доступных сессий!")
        del active_reports[user_id]
        return
    
    # Имитируем отправку жалоб
    for session_index, session_name in enumerate(sessions):
        for i in range(5):
            try:
                # Обновляем прогресс-бар
                current_report += 1
                progress_percent = min(math.floor((current_report / total_reports) * 100), 100)
                progress_bar = "▰" * math.floor(progress_percent / 10) + "▱" * (10 - math.floor(progress_percent / 10))
                
                # Обновляем сообщение с прогрессом
                try:
                    await progress_message.edit_text(
                        f"🚀 Отправка жалоб...\n\n"
                        f"{progress_bar} {progress_percent}%\n"
                        f"✅ Успешно: {successful} | ❌ Ошибки: {failed} | 🌊 Флуды: {floods}"
                    )
                except Exception as e:
                    logger.error(f"Ошибка обновления прогресса: {e}")
                
                # Имитируем отправку жалобы
                result, status = await send_report_simulated(session_name, link)
                
                current_time = datetime.now().strftime("%H:%M:%S")
                log_entry = f"[{current_time}] {session_name} -> {link} - [{status}]\n"
                
                with open(log_filename, 'a', encoding='utf-8') as log_file:
                    log_file.write(log_entry)
                
                if status == "ДОСТАВЛЕНО":
                    successful += 1
                elif status == "ФЛУД":
                    floods += 1
                else:
                    failed += 1
                
                # Случайная задержка между 2-4 секундами
                await asyncio.sleep(random.uniform(2, 4))
                
            except Exception as e:
                current_time = datetime.now().strftime("%H:%M:%S")
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
    
    # Обновляем прогресс-бар на 100%
    try:
        await progress_message.edit_text(
            f"✅ Отправка завершена!\n\n"
            f"▰▰▰▰▰▰▰▰▰▰ 100%\n"
            f"✅ Успешно: {successful} | ❌ Ошибки: {failed} | 🌊 Флуды: {floods}\n"
            f"📊 Готовлю отчет..."
        )
        await asyncio.sleep(2)  # Небольшая пауза перед отправкой отчета
    except Exception as e:
        logger.error(f"Ошибка обновления прогресса: {e}")
    
    # Отправляем лог пользователю
    try:
        document = FSInputFile(log_filename)
        await message.answer_document(
            document,
            caption=f"📊 Отчет готов!\n"
                   f"✅ Успешно: {successful}\n"
                   f"❌ Неуспешно: {failed}\n"
                   f"🌊 Флудов: {floods}\n"
                   f"📊 Всего отправок: {total_reports}\n"
                   f"🔗 Цель: {link}"
        )
        
        # Удаляем сообщение с прогресс-баром
        try:
            await progress_message.delete()
        except:
            pass
            
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
                       f"👤 ID: {message.from_user.id}\n"
                       f"✅ Успешно: {successful} | ❌ Ошибки: {failed} | 🌊 Флуды: {floods}"
            )
        except Exception as e:
            logger.error(f"Ошибка отправки файла админу {admin_id}: {e}")
    
    # Удаляем временный файл
    try:
        os.remove(log_filename)
    except:
        pass
    
    if user_id in active_reports:
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
async def process_support(message: types.Message):
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
    
    if message.from_user.id in active_reports:
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
    
    logger.info("✅ Бот запущен! (Режим имитации)")
    try:
        await dp.start_polling(bot)
    finally:
        await bot.session.close()

if __name__ == "__main__":
    asyncio.run(main())
