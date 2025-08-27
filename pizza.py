import asyncio
import logging
import os
import time
import math
import random
from datetime import datetime, timedelta
from typing import List, Tuple
import nest_asyncio

# Применяем patch для nested event loops
nest_asyncio.apply()

from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, FSInputFile

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Конфигурация
BOT_TOKEN = '8386260112:AAEV1fxeOXEuVU2qHaCp78eKj9gFjJBeJZM'

ADMIN_IDS = [8075123058]  # ID администраторов
SUPPORT_ID = 1637959612  # ID техподдержки

# Инициализация бота
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# Глобальные переменные
order_counter = 1
sessions_folder = "sessions"
active_reports = {}
sessions_count = random.randint(35, 37)
sessions_update_time = datetime.now()
emails_count = random.randint(45, 55)

main_keyboard = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="🟢 Донос", callback_data="report")],
    [InlineKeyboardButton(text="📊 Статистика", callback_data="stats")],
    [InlineKeyboardButton(text="👤 Профиль", callback_data="profile")],
    [InlineKeyboardButton(text="💎 Поддержать проект", callback_data="donate")],
    [InlineKeyboardButton(text="🛠 Тех поддержка", callback_data="support")]
])

# Клавиатура выбора метода
methods_keyboard = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="🤖 Botnet метод", callback_data="method_botnet")],
    [InlineKeyboardButton(text="📧 Email метод", callback_data="method_email")],
    [InlineKeyboardButton(text="🔐 DSA метод", callback_data="method_dsa")],
    [InlineKeyboardButton(text="⬅️ Назад", callback_data="back_to_main")]
])


# Функция для обновления счетчиков каждые 2 часа
def update_counts():
    global sessions_count, emails_count, sessions_update_time
    current_time = datetime.now()
    
    if current_time - sessions_update_time >= timedelta(hours=2):
        sessions_count = random.randint(35, 37)
        emails_count = random.randint(45, 55)
        sessions_update_time = current_time
        logger.info(f"Обновлены счетчики: sessions={sessions_count}, emails={emails_count}")

# Загрузка сессий (имитация)
def load_sessions() -> List[str]:
    update_counts()
    sessions = []
    for i in range(sessions_count):
        sessions.append(f"telethon_{random.randint(100000000, 999999999)}")
    return sessions

# Генерация email аккаунтов в нужном формате
def generate_emails() -> List[str]:
    update_counts()
    emails = []
    
    # Генерируем почты в формате: буквы + цифры
    for i in range(emails_count):
        # Случайная длина имени (5-12 символов)
        name_length = random.randint(5, 12)
        # Генерируем случайные буквы
        letters = ''.join(random.choices('abcdefghijklmnopqrstuvwxyz', k=name_length))
        # Добавляем случайные цифры (3-5 цифр)
        numbers = ''.join(random.choices('0123456789', k=random.randint(3, 5)))
        # Формируем email
        email = f"{letters}{numbers}@gmail.com"
        emails.append(email)
    
    return emails

# Имитация отправки жалобы через Botnet
async def send_report_botnet(session_name: str, message_link: str) -> Tuple[bool, str]:
    try:
        await asyncio.sleep(random.uniform(0.8, 1.2))
        rand = random.random()
        if rand < 0.85: return True, "ДОСТАВЛЕНО"
        elif rand < 0.95: return False, random.choice(["НЕВАЛИД", "ОШИБКА: Таймаут"])
        else: return False, "ФЛУД"
    except Exception as e:
        return False, f"ОШИБКА: {str(e)[:30]}"

# Имитация отправки жалобы через Email
async def send_report_email(email: str, message_link: str) -> Tuple[bool, str]:
    try:
        await asyncio.sleep(random.uniform(0.6, 1.0))
        rand = random.random()
        if rand < 0.75: return True, "ДОСТАВЛЕНО"
        elif rand < 0.90: return False, random.choice(["EMAIL BOUNCE", "SPAM FILTER"])
        else: return False, "QUOTA EXCEEDED"
    except Exception as e:
        return False, f"EMAIL ERROR: {str(e)[:30]}"

# Отправка фото при старте
async def send_welcome_message(chat_id):
    welcome_text = "👋 Привет! SuslikPizza лучшая доставка в городе Санкт-Петербург (суслико ландивмф)! 🍕"
    
    try:
        if os.path.exists("start.jpg"):
            photo = FSInputFile("start.jpg")
            await bot.send_photo(
                chat_id, 
                photo, 
                caption=welcome_text,
                reply_markup=main_keyboard
            )
        else:
            await bot.send_message(chat_id, welcome_text, reply_markup=main_keyboard)
    except Exception as e:
        logger.error(f"Ошибка отправки фото: {e}")
        await bot.send_message(chat_id, welcome_text, reply_markup=main_keyboard)

# Обработчик команды /start
@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    await send_welcome_message(message.chat.id)

# Обработчик команды /help
@dp.message(Command("help"))
async def cmd_help(message: types.Message):
    help_text = (
        "🤖 Помощь по боту:\n\n"
        "🟢 Донос - отправить жалобу на сообщение\n"
        "📊 Статистика - посмотреть доступные ресурсы\n"
        "👤 Профиль - посмотреть свой профиль\n"
        "💎 Поддержать проект - помочь развитию бота\n"
        "🛠 Тех поддержка - связаться с поддержкой\n\n"
        "Просто нажмите на кнопку в меню ниже!"
    )
    await message.answer(help_text, reply_markup=main_keyboard)

# Обработчик кнопки "Донос"
@dp.callback_query(F.data == "report")
async def report_handler(callback: types.CallbackQuery):
    await callback.message.answer("📩 Введите ссылку на сообщение из публичного чата с нарушением:")
    active_reports[callback.from_user.id] = "waiting_link"
    await callback.answer()

# Обработчик кнопки "Статистика"
@dp.callback_query(F.data == "stats")
async def stats_handler(callback: types.CallbackQuery):
    update_counts()
    stats_text = (
        f"📊 Статистика ресурсов:\n\n"
        f"🤖 Доступно сессий: {sessions_count}\n"
        f"📧 Доступно email: {emails_count}\n"
        f"⏰ Обновление через: {get_next_update_time()}\n\n"
        f"💪 Готов к работе!"
    )
    await callback.message.answer(stats_text)
    await callback.answer()

def get_next_update_time():
    next_update = sessions_update_time + timedelta(hours=2)
    remaining = next_update - datetime.now()
    hours = remaining.seconds // 3600
    minutes = (remaining.seconds % 3600) // 60
    return f"{hours}ч {minutes}м"

# Обработчик кнопки выбора метода
@dp.callback_query(F.data.startswith("method_"))
async def method_handler(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    method = callback.data.split("_")[1]
    
    if method == "dsa":
        await callback.message.answer("в раработке ыы 😊")
        await callback.answer()
        return
    
    if user_id in active_reports and active_reports[user_id].startswith("waiting_method_"):
        link = active_reports[user_id].split("_", 2)[2]
        active_reports[user_id] = f"processing_{method}_{link}"
        await callback.message.answer(f"🚀 Запускаю {method.upper()} метод...")
        await process_link(callback.message, method, link)
    await callback.answer()

# Обработчик кнопки "Назад"
@dp.callback_query(F.data == "back_to_main")
async def back_handler(callback: types.CallbackQuery):
    await send_welcome_message(callback.message.chat.id)
    await callback.answer()

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

# Обработчик кнопки "Поддержать проект"
@dp.callback_query(F.data == "donate")
async def donate_handler(callback: types.CallbackQuery):
    await callback.message.answer(
        "💎 Поддержать проект можно по ссылке:\n"
        "https://t.me/send?start=IV2HJyZJ6rrz\n\n"
        "🙏 Спасибо за вашу поддержку! 💖"
    )
    await callback.answer()

# Обработчик текстовых сообщений
@dp.message(F.text & ~F.command)
async def process_text_message(message: types.Message):
    user_id = message.from_user.id
    
    if user_id in active_reports and active_reports[user_id] == "waiting_link":
        if 't.me/' in message.text:
            link = message.text.strip()
            active_reports[user_id] = f"waiting_method_{link}"
            await message.answer("🔧 Выберите метод отправки:", reply_markup=methods_keyboard)
        else:
            await message.answer("❌ Это не похоже на ссылку Telegram.")
    
    elif user_id in active_reports and active_reports[user_id] == "waiting_support":
        await process_support(message)

# Основная функция обработки ссылки
async def process_link(message: types.Message, method: str, link: str):
    user_id = message.from_user.id
    global order_counter
    
    log_filename = f"SuslikPizza_log{order_counter}.txt"
    order_counter += 1
    
    with open(log_filename, 'w', encoding='utf-8') as log_file:
        log_file.write(f"SuslikPizza log | {method.upper()}-method\n")
        log_file.write("-" * 50 + "\n")
        log_file.write(f"Пользователь: {message.from_user.id} (@{message.from_user.username})\n")
        log_file.write(f"Метод: {method.upper()}\n")
        log_file.write(f"Ссылка: {link}\n")
        log_file.write(f"Время начала: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        log_file.write("-" * 50 + "\n")
    
    progress_message = await message.answer(f"🚀 Запуск {method.upper()} метода...\n\n▰▱▱▱▱▱▱▱▱ 0%")
    
    successful = 0
    failed = 0
    floods = 0
    
    if method == "botnet":
        items = load_sessions()
        reports_per_item = 3
        send_func = send_report_botnet
        item_type = "сессия"
    elif method == "email":
        items = generate_emails()
        reports_per_item = 5
        send_func = send_report_email
        item_type = "email"
    else:
        items = []
        reports_per_item = 0
    
    total_reports = len(items) * reports_per_item
    total_reports = min(total_reports, random.randint(110, 160))
    
    if total_reports == 0:
        await progress_message.edit_text("❌ Нет доступных ресурсов!")
        return
    
    start_time = datetime.now()
    
    # Имитация отправки
    for i, item in enumerate(items):
        for j in range(reports_per_item):
            if (i * reports_per_item + j) >= total_reports:
                break
            
            # Отправляем жалобу
            result, status = await send_func(item, link)
            
            # Логируем
            current_time = datetime.now().strftime("%H:%M:%S")
            with open(log_filename, 'a', encoding='utf-8') as log_file:
                if method == "email":
                    log_file.write(f"[{current_time}] 📧 {item} -> {link} - [{status}]\n")
                else:
                    log_file.write(f"[{current_time}] 🤖 {item} -> {link} - [{status}]\n")
            
            # Считаем статистику
            if status == "ДОСТАВЛЕНО":
                successful += 1
            elif status in ["ФЛУД", "QUOTA EXCEEDED"]:
                floods += 1
            else:
                failed += 1
            
            # Обновляем прогресс каждые 10 отчетов
            current_report = i * reports_per_item + j + 1
            if current_report % 10 == 0 or current_report >= total_reports:
                progress_percent = min(math.floor(current_report / total_reports * 100), 100)
                progress_bar = "▰" * math.floor(progress_percent / 10) + "▱" * (10 - math.floor(progress_percent / 10))
                elapsed = int((datetime.now() - start_time).total_seconds())
                
                try:
                    await progress_message.edit_text(
                        f"🚀 {method.upper()} метод...\n\n"
                        f"{progress_bar} {progress_percent}%\n"
                        f"✅ Успешно: {successful} | ❌ Ошибки: {failed} | 🌊 Флуды: {floods}\n"
                        f"⏰ Прошло: {elapsed}с"
                    )
                except:
                    pass
        
        # Небольшая пауза между элементами
        await asyncio.sleep(0.1)
    
    # Записываем итоги
    total_time = int((datetime.now() - start_time).total_seconds())
    with open(log_filename, 'a', encoding='utf-8') as log_file:
        log_file.write("-" * 50 + "\n")
        log_file.write(f"Успешно: {successful}\n")
        log_file.write(f"Неуспешно: {failed}\n")
        log_file.write(f"Флудов: {floods}\n")
        log_file.write(f"Всего отправок: {successful + failed + floods}\n")
        log_file.write(f"Использовано {item_type}: {len(items)}\n")
        log_file.write(f"Время выполнения: {total_time}сек\n")
    
    # Отправляем результат пользователю
    try:
        document = FSInputFile(log_filename)
        await message.answer_document(
            document,
            caption=f"📊 {method.upper()} метод завершен!\n"
                   f"✅ Успешно: {successful}\n"
                   f"❌ Неуспешно: {failed}\n"
                   f"🌊 Флудов: {floods}\n"
                   f"📊 Всего: {successful + failed + floods}\n"
                   f"⏰ Время: {total_time}сек\n"
                   f"🔗 Цель: {link}"
        )
        
        # Отправляем админам
        for admin_id in ADMIN_IDS:
            try:
                await bot.send_document(
                    admin_id,
                    document,
                    caption=f"📋 Новый отчет от @{message.from_user.username}\n"
                           f"👤 ID: {message.from_user.id}\n"
                           f"✅ Успешно: {successful} | ❌ Ошибки: {failed} | 🌊 Флуды: {floods}"
                )
            except Exception as e:
                logger.error(f"Ошибка отправки файла админу {admin_id}: {e}")
        
        try:
            await progress_message.delete()
        except:
            pass
            
    except Exception as e:
        await message.answer(f"📊 Отчет готов! Но файл не отправлен: {e}")
    
    # Чистка
    try:
        os.remove(log_filename)
    except:
        pass
    
    if user_id in active_reports:
        del active_reports[user_id]

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

# Запуск бота
async def main():
    try:
        await bot.delete_webhook(drop_pending_updates=True)
        logger.info("Вебхук успешно удален")
    except Exception as e:
        logger.error(f"Ошибка при удалении вебхука: {e}")
    
    if not os.path.exists(sessions_folder):
        os.makedirs(sessions_folder)
    
    logger.info("✅ Бот запущен! (Режим имитации)")
    try:
        await dp.start_polling(bot)
    except Exception as e:
        logger.error(f"Ошибка запуска бота: {e}")
    finally:
        await bot.session.close()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Бот остановлен")


