import asyncio
import smtplib
from email.mime.text import MIMEText
from aiogram import Bot, Dispatcher, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command
import random
from datetime import datetime

BOT_TOKEN = "8258547780:AAEYBZ7-5jzitiJXA4GdSGR2cruhbDR2UGw"

# Инициализация бота и диспетчера
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# Словарь с отправителями (полный список)
senders = {
    'qstkennethadams388@gmail.com': 'itpz jkrh mtwp escx',
    'usppaullewis171@gmail.com': 'lpiy xqwi apmc xzmv',
    'ftkgeorgeanderson367@gmail.com': 'okut ecjk hstl nucy',
    'nieedwardbrown533@gmail.com': 'wvig utku ovjk appd',
    'h56400139@gmail.com': 'byrl egno xguy ksvf',
    'den.kotelnikov220@gmail.com': 'xprw tftm lldy ranp',
    'trevorzxasuniga214@gmail.com': 'egnr eucw jvxg jatq',
    'dellapreston50@gmail.com': 'qoit huon rzsd eewo',
    'neilfdhioley765@gmail.com': 'rgco uwiy qrdc gvqh',
    'hhzcharlesbaker201@gmail.com': 'mcxq vzgm quxy smhh',
    'samuelmnjassey32@gmail.com': 'lgct cjiw nufr zxjg',
    'allisonikse1922@gmail.com': 'tozo xrzu qndn mwuq',
    'corysnja1996@gmail.com': 'pfjk ocbf augx cgiy',
    'maddietrdk1999@gmail.com': 'rhqb ssiz csar cvot',
    'yaitskaya.alya@mail.ru': 'CeiYHA6GNpvuCz584eCp',
    'yelena.polikarpova.1987@mail.ru': '70Ktuvrs1iYbvSnbK8hG',
    'yeva.zuyeva.85@mail.ru': 'EBjgRqq73hue9dGhUA2R',
    'zina.yagovenko.69@mail.ru': 'QKBmpXnzFZVu9w4ewSrA',
    'ilya.yaroslavov.72@mail.ru': 'A2gNkb8n54i4T7XdPdH5',
    'maryamna.moskvina.62@mail.ru': 'dT7ftdX72cMsVemqRRqu',
    'zina.zhvikova@mail.ru': '7CwRkjeL3a5viE9we3bt',
    'boyarinova.fisa@mail.ru': 'NnJfmSBzQ9Eew09xirpY',
    'prokhor.sveshnikov.73@mail.ru': 'Ybunrxdf95gkzm6A6ipp',
    'azhikelyamov.yulian@mail.ru': 'r7hanfr0tMqcBE4Edmg0',
    'prokhor.siyantsev@mail.ru': 'yubs6kvtfpWT4Tram26e',
    'yablonev90@mail.ru': '42krThdaYbWCrCbH8UgK',
    'mari.dvornikova.86@mail.ru': 'qdEzYLWSTz6UEM2E4i0u',
    'vika.tobolenko.96@mail.ru': '3WQ2wFTwge9m2C09QsfK',
    'koporikov.yura@mail.ru': 'nJtyfjqYi91j7tk0udNx',
    'zina.podshivalova.92@mail.ru': 'u4CL3YxVutmiuTvmTrbu',
    'leha.novitskiy.71@mail.ru': 'qQZd1gMqkU906Xk2hgJJ',
    'rimma.aleksandrovicha.72@mail.ru': 'biL4m6h0h4xQrDB3PnPp',
    'polina.karaseva.1987@mail.ru': 'mxZUqPPTrZHK99jUfPhB',
    'prokhor.sablin.82@mail.ru': 'vN7FjmmCmAD0JnQsANyc',
    'kade.kostya@mail.ru': 'U0hdXu7y3c1AVeT1Vpn9',
    'yelizaveta.novokshonova.71@mail.ru': 'aKPpgaPDuwaKbX1pbcq3',
    'pozdovp@mail.ru': 'EGDd20c7s82Z0s9LmrXc',
    'siyasinovy@mail.ru': 'z2ZdsRL04JvBYZrrjrvv',
    'nina.gref.73@mail.ru': 'sitw1XTxCVgji061iqj7',
    'fil.golubkin.80@mail.ru': 'PeaLrzjbn408DEeiqmQq',
    'venedikt.babinov.71@mail.ru': 'tBewA1HQm29c2Zkira96',
    'den.verderevskiy.67@mail.ru': 'fndp7qr67dpfXBAu0ePH',
    'olga.viranovskaya.92@mail.ru': '50QSPrecgk5cMdk1YsBm',
    'uyankilovich@mail.ru': 'Muw9kX9vAhhKxbZXZ3sh',
    'clqdxtqbfj@rambler.ru': '8278384a3L51C',
    'qeuvkzwxao@rambler.ru': '72325556pMFol',
    'mgiwwgbjqt@rambler.ru': '3180204jCoAdt',
    'olwogjcicw@rambler.ru': '3993480P4Gyth',
    'qjdmjszsnc@rambler.ru': '6545403StkbOh',
    'yqoibpcoki@rambler.ru': '695328653f9Wp',
    'vnlhjjkbxr@rambler.ru': '4609313egqV59',
    'vpgcdkunar@rambler.ru': '9936120R4LYh3',
    'agycsnogqq@rambler.ru': '0234025nWwX5j',
    'ctmhzsngse@rambler.ru': '2480571s1sZvW',
    'ryztzlttdn@rambler.ru': '9416368kTX5jI',
    'hqxybovebw@rambler.ru': '8245145VhX704',
    'rejrjswkwb@rambler.ru': '5114881xCYqsB',
    'xkbecjvxnx@rambler.ru': '5670524FiFi39',
    'xnlqkfvwzx@rambler.ru': '7911186rp8L9P',
    'gvzzmqtuzy@rambler.ru': '5133370ZstXEx',
    'eijxsbjyfy@rambler.ru': '36196124YQZeI',
    'bizdlfuahq@rambler.ru': '8374903tkk2gA',
    'dhehumtsef@rambler.ru': '9126453AkhK0Z',
    'zsotxpaxvi@rambler.ru': '46227528QryxI',
    'ktsgdygeuc@rambler.ru': '1853586bnCyzK',
    'uiacgqvgpe@rambler.ru': '65280104FvoJW',
    'ynazuhytyd@rambler.ru': '1038469bD3PXc',
    'ewmyymarvi@rambler.ru': '5023318Bh3tBg',
    'wllhpdisuj@rambler.ru': '24856958LdTsS',
    'ldqicaqxqo@rambler.ru': '3878601ZNDUtq',
    'qnuumqoreq@rambler.ru': '97575207Is6tx',
    'hlqhvdwpvn@rambler.ru': '6886684bPjiyd',
    'mjjjxiuadq@rambler.ru': '0606032V81m1F',
    'qmasujqfrk@rambler.ru': '277585511anUy',
    'mfemvxqdcq@rambler.ru': '8831015UwqwWD',
    'jauvxszfam@rambler.ru': '0711044gqzrVR',
    'lkmujuagfk@rambler.ru': '08781007DLS8k',
    'kcamwmzxjo@rambler.ru': '9812873rVr1MY',
    'czkklwifon@rambler.ru': '74278883h9FP8',
    'tsjsbqyrfk@rambler.ru': '0150917jIseH2',
    'pbetvcnhzh@rambler.ru': '9952234XaKDFu',
    'bsahxcpwkw@rambler.ru': '2860163ch8Ido',
    'xphyesgbtc@rambler.ru': '6594341ERehhX',
    'egmpjoufeq@rambler.ru': '2613441hfDuWr',
    'jyaolatwam@rambler.ru': '7668835xdjLbg',
    'istooplcmf@rambler.ru': '6592403JR47Wm',
    'vxesoednot@rambler.ru': '35885918QZw94',
    'oywtklayaz@rambler.ru': '4434448KsCuTf',
    'tazxrlpjil@rambler.ru': '8342862p9Wyst',
    'aumiycpxid@rambler.ru': '4109383BuuNcN',
    'lrrztbfuzy@rambler.ru': '3646406sDO8ay',
    'ocggavguxr@rambler.ru': '6406050SL2mZG',
    'imprdsrnmd@rambler.ru': '4869746vpxksJ',
    'eidyoikavp@rambler.ru': '1243890yXPyix',
    'jtbcabsapw@rambler.ru': '566339497yHv3',
    'szokdvnzrw@rambler.ru': '5285567I3Bil1',
    'jqflrccfjs@rambler.ru': '7239478VeLuf1',
    'nhmxjawemh@rambler.ru': '22695409fkCex',
    'uoolwvvwdc@rambler.ru': '1073090zX6ebM',
    'bdnptczren@rambler.ru': '2684430DcPEuk',
    'bfghzdkurg@rambler.ru': '3874335d5hDQy',
    'ljlexsfcvo@rambler.ru': '4102671EIquGo',
    'byzjhysyyg@rambler.ru': '4637736mzdEcT',
    'tlrjbuzcyj@rambler.ru': '2437827AhPaGW',
    'denjsbmggh@rambler.ru': '228014585ayVe',
    'ekkjrcskzo@rambler.ru': '6609442MFPeDO',
    'ptpjocqobw@rambler.ru': '6047270EXk7Hb',
    'nekrxmcklm@rambler.ru': '3532718I3vV4C',
    'ulgqeqvdqy@rambler.ru': '6764301Nx25yL',
    'ezofozvhyn@rambler.ru': '43181265tC6FQ',
    'hwklsnkqky@rambler.ru': '2399374mHyEUJ',
    'elglaqexoj@rambler.ru': '9803014pMNF9p',
    'rgmjfwhhjs@rambler.ru': '3268611cfC3aR',
    'vcvwvkntgb@rambler.ru': '6536007UgTXg4',
    'phkohtlitv@rambler.ru': '0238010TXt5aN',
    'pqqqyejlqi@rambler.ru': '0429804UwSSi2',
    'toxevermnd@rambler.ru': '1801000MqDm87',
    'dicfdqgxad@rambler.ru': '2062460Tbvjlz',
    'sktsnxhcxe@rambler.ru': '35185285Pon91',
    'jpljjnrrla@rambler.ru': '0815671xPHjiw',
    'rtqpiimiid@rambler.ru': '6534672URa1mI',
    'ldygdlpizk@rambler.ru': '6686886YWhL05',
    'fqxqadaxfy@rambler.ru': '3195621x5qYdU',
    'chybzpsglw@rambler.ru': '8032931YTKllg',
    'vkctzanare@rambler.ru': '1157997LGySqk',
    'repjncygun@rambler.ru': '3300691BqYJVG',
    'khrarivdow@rambler.ru': '7168350Cmqkmj',
    'aqbeitoqdl@rambler.ru': '87552792499tS',
    'vhauhgmbnc@rambler.ru': '9276444y9YzY1',
    'cfoqabqkbi@rambler.ru': '4601718gc2Zji',
    'kmqnowhvjp@rambler.ru': '6667003L1jZxc',
    'djsdksvzhj@rambler.ru': '7523251yAKPjZ',
    'uztbbbfqbp@rambler.ru': '8265517naN9fx',
    'ljrbpfuicp@rambler.ru': '39793362TjZIk',
    'jzzdyxicjo@rambler.ru': '8117494s6CZVB',
    'gjnbtrflkc@rambler.ru': '8623171iqXOD9',
    'jfjtwncyeb@rambler.ru': '7066987lMSG2Z',
    'rfphqkyyrj@rambler.ru': '8800207M5Nj7Y',
    'ilynipkqwx@rambler.ru': '83333032WQo83',
    'ifzenleixs@rambler.ru': '69679436xM9U4',
    'oevwtysoel@rambler.ru': '6918228UC47Zs',
    'hpdkdwqvzx@rambler.ru': '0605431xMVexd',
    'ekbkufxdxx@rambler.ru': '1918712uEOQ9t',
    'zstxwfwiof@rambler.ru': '4043772UwRp5o',
    'rjmrbybhnd@rambler.ru': '5203792lDmxvC',
    'eukygnfzno@rambler.ru': '3520959hXs1Zw',
    'ljrolbwlad@rambler.ru': '0394475pK0dYa',
    'gozpezocmj@rambler.ru': '8282635Gkvuvq',
    'asytoiumwt@rambler.ru': '42141199FgP3H',
    'fbiooohghv@rambler.ru': '7338453zMbWhb',
    'ajwlalfqqu@rambler.ru': '3360915x1XVgt',
    'cvegntetwm@rambler.ru': '8091607CSuKMf',
    'jnhjnmicbt@rambler.ru': '6375986dokrgG',
    'fnaauasmjz@rambler.ru': '4160248ztCRsJ',
    'qnwmlvfwct@rambler.ru': '8367630XGXmxW',
    'lkycbhjcwp@rambler.ru': '5255980KedZTc',
    'bkyojwrkxl@rambler.ru': '1286663uHl4WQ',
    'lxddybklck@rambler.ru': '1077242JFSyQN',
    'chzhdkoxnp@rambler.ru': '0533445SI0q7c',
    'ofjxkwwomf@rambler.ru': '04956317DKrSX',
    'jlirgtapbl@rambler.ru': '8728917NdMxgN',
    'dgcceghlse@rambler.ru': '2986381aT5V36',
    'rkwfhcvlem@rambler.ru': '10022063K5qmY'
}

# Почты для отправки
target_emails = [
    'sms@telegram.org',
    'dmca@telegram.org',
    'abuse@telegram.org',
    'sticker@telegram.org',
    'support@telegram.org'
]

# Данные для пиццерии
pizzerias = ["🍕 Пиццерия 'У Луиджи'", "🍕 Пиццерия 'Гастрономическая'"]
pizza_types = ["Пепперони", "Маргарита", "4 сыра"]
status_messages = ["🧑‍🍳 Повар замешивает тесто...", "🍅 Добавляем свежие помидоры..."]

def create_progress_bar(percentage):
    filled = '▓' * int(percentage / 10)
    empty = '░' * (10 - len(filled))
    return f"{filled}{empty} {percentage}%"

# Синхронная функция для отправки email
def send_email_sync(email, password, target, complaint_text):
    try:
        if '@gmail.com' in email:
            server = smtplib.SMTP('smtp.gmail.com', 587)
        elif '@mail.ru' in email:
            server = smtplib.SMTP('smtp.mail.ru', 465)
        else:
            return False
            
        server.starttls()
        server.login(email, password)
        
        msg = MIMEText(complaint_text)
        msg['From'] = email
        msg['To'] = target
        msg['Subject'] = "Жалоба"
        
        server.sendmail(email, target, msg.as_string())
        server.quit()
        return True
    except Exception as e:
        print(f"Ошибка при отправке с {email}: {e}")
        return False

# Асинхронная обертка для отправки email
async def send_email_async(email, password, target, complaint_text):
    return await asyncio.to_thread(send_email_sync, email, password, target, complaint_text)

@dp.message(Command("start"))
async def start(message: types.Message):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🍕 Купить пиццу", callback_data="buy_pizza")],
        [InlineKeyboardButton(text="👤 Профиль", callback_data="profile")]
    ])
    await message.answer("Привет! Я suslik pizza bot - лучшая доставка пиццы!", reply_markup=keyboard)

@dp.callback_query(lambda c: c.data == "buy_pizza")
async def buy_pizza(callback: types.CallbackQuery):
    await callback.message.answer("Пожалуйста, введите текст вашей жалобы:")
    await callback.answer()

@dp.callback_query(lambda c: c.data == "profile")
async def show_profile(callback: types.CallbackQuery):
    user = callback.from_user
    profile_text = f"👤 Ваш профиль:\nID: {user.id}\nИмя: {user.first_name}"
    await callback.message.answer(profile_text)
    await callback.answer()

@dp.message()
async def process_complaint(message: types.Message):
    if not message.text.strip():
        await message.answer("Текст жалобы не может быть пустым.")
        return
    
    pizzeria = random.choice(pizzerias)
    pizza = random.choice(pizza_types)
    
    # Процесс приготовления пиццы
    preparing_msg = await message.answer(f"🍕 Ваш заказ из {pizzeria}: {pizza}\n⏳ Начинаем приготовление...")
    
    for percent in range(0, 101, 5):
        if percent % 15 == 0:
            await preparing_msg.edit_text(
                f"🍕 Ваш заказ: {pizza}\n"
                f"{random.choice(status_messages)}\n"
                f"{create_progress_bar(percent)}"
            )
        await asyncio.sleep(0.2)
    
    await preparing_msg.edit_text(f"✅ Ваша пицца {pizza} готова!\n⏳ Начинаем отправку жалоб...")
    
    success_count = 0
    fail_count = 0
    total_accounts = len(senders)
    
    progress_msg = await message.answer(
        f"📤 Отправка жалоб:\n{create_progress_bar(0)}\n"
        f"├ Успешно: 0\n└ Неуспешно: 0"
    )
    
    # Отправка жалоб
    for i, (email, password) in enumerate(senders.items()):
        progress = int((i + 1) / total_accounts * 100)
        
        for target in target_emails:
            if await send_email_async(email, password, target, message.text):
                success_count += 1
            else:
                fail_count += 1
            
            await progress_msg.edit_text(
                f"📤 Отправка жалоб:\n{create_progress_bar(progress)}\n"
                f"├ Успешно: {success_count}\n└ Неуспешно: {fail_count}"
            )
            await asyncio.sleep(1)
    
    current_time = datetime.now().strftime("%H:%M:%S")
    await progress_msg.edit_text(
        f"✅ Отправка завершена в {current_time}!\n"
        f"📊 Результаты:\n├ Успешно: {success_count}\n└ Неуспешно: {fail_count}\n"
        f"🍕 Приятного аппетита!"
    )

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())

