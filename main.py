import telebot
from telebot import types
import requests
from datetime import datetime, timedelta

BOT_TOKEN = "8179092727:AAFuKcTZAgJrMGdMGLYYGukCV64UHcY2sx8"
API_TOKEN = "69b9e0a9db675b45445ec37e847a0b2b"


bot = telebot.TeleBot(BOT_TOKEN)

@bot.message_handler(commands=['sicret'])
def sicret(message):
    msg = bot.send_message(message.chat.id, "Введите пароль:")
    bot.register_next_step_handler(msg, check_password)


def check_password(message):
    if message.text.lower().strip() == "чубар":
        bot.send_message(message.chat.id,
            "🔥 Код верный!\nВот чит-коды на GTA Vice City:\n\n"
            "PANZER — танк\n"
            "ASPIRINE — здоровье\n"
            "BIGBANG — взрыв всех машин\n"
            "COMEFLYWITHME — летающие машины\n"
            "SEAWAYS — машины ездят по воде"
        )
    else:
        bot.send_message(
            message.chat.id,
            "❌ Неверно!\nПодсказка: лучшая лагманхана 😉"
        )


def get_airport_code(city_name):
    url = "https://api.travelpayouts.com/data/ru/cities.json"

    try:
        r = requests.get(url)
        cities = r.json()

        for c in cities:
            if city_name.lower() in c["name"].lower():
                return c["code"]
    except:
        return None

    return None


def search_oneway_nearby(origin_code, dest_code):
    url = "https://api.travelpayouts.com/aviasales/v3/prices_for_dates"
    today = datetime.today()
    results = []

    for i in range(3):
        date = (today + timedelta(days=i)).strftime("%Y-%m-%d")

        params = {
            "origin": origin_code,
            "destination": dest_code,
            "departure_at": date,
            "sorting": "price",
            "limit": 5,
            "token": API_TOKEN
        }

        r = requests.get(url, params=params)
        data = r.json()

        if "data" in data and data["data"]:
            for f in data["data"]:
                results.append({
                    "date": date,
                    "price": f["price"],
                    "airline": f.get("airline", "—"),
                    "flight_number": f.get("flight_number", "—")
                })

    results = sorted(results, key=lambda x: x["price"])
    return results[:5]



def main_menu():
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
    kb.add("Поиск билетов", "О нас")
    kb.add("Помощь", "Купить билет")
    return kb


@bot.message_handler(commands=["start"])
def start(message):
    bot.send_message(
        message.chat.id,
        "✈ Добро пожаловать в бот поиска авиабилетов!\nВыберите действие:",
        reply_markup=main_menu()
    )


@bot.message_handler(func=lambda m: m.text == "Поиск билетов")
def ask_route(message):
    bot.send_message(
        message.chat.id,
        "Введите маршрут.\nПример: *Алматы Астана*",
        parse_mode="Markdown"
    )



@bot.message_handler(func=lambda m: m.text not in ["Поиск билетов", "О нас", "Помощь", "Купить билет"])
def process_route(message):
    try:
        parts = message.text.split()
        if len(parts) != 2:
            bot.send_message(message.chat.id, "Пиши так: Город1 Город2\nПример: Алматы Астана")
            return

        city_from = parts[0]
        city_to = parts[1]

        bot.send_message(message.chat.id, f"🔍 Ищу билеты: {city_from} → {city_to}")

        from_code = get_airport_code(city_from)
        to_code = get_airport_code(city_to)

        if not from_code or not to_code:
            bot.send_message(message.chat.id, "❌ Не нашел код аэропорта. Попробуй другой город.")
            return

        flights = search_oneway_nearby(from_code, to_code)

        if not flights:
            bot.send_message(message.chat.id, "❌ Билетов нет на сегодня и ближайшие даты")
        else:
            text = f"✈ Билеты {city_from} → {city_to} на ближайшие даты:\n\n"
            for f in flights:
                text += f"""
ДАТА: {f['date']}
СУММА: {f['price']}₸
НОМЕР САМОЛЕТА: {f['airline']} {f['flight_number']}
"""

            bot.send_message(message.chat.id, text)

    except Exception as e:
        bot.send_message(message.chat.id, f"Ошибка: {e}")



@bot.message_handler(func=lambda m: m.text == "Помощь")
def help_message(message):
    text = """
📌 Как пользоваться ботом:
1) Нажми "Поиск билетов"
2) Напиши два города: Алматы Астана
3) Бот найдёт билеты на сегодня, завтра и послезавтра

Примеры городов:
Алматы → ALA  
Астана → NQZ  
Шымкент → CIT  
Москва → MOW  
"""
    bot.send_message(message.chat.id, text, parse_mode="Markdown")



@bot.message_handler(func=lambda m: m.text == "О нас")
def about(message):
    bot.send_message(message.chat.id, "Мы ищем самые дешёвые билеты по реальным данным Aviasales ✈🔥")



@bot.message_handler(func=lambda m: m.text == "Купить билет")
def buy_ticket(message):
    bot.send_message(
        message.chat.id,
        "💳 Чтобы купить билет, введите данные карты:\n\n"
        "Номер карты: ____ ____ ____ ____\n"
        "Срок: _/_\n"
        "CVC: ___"
    )


print("работаю")
bot.polling(none_stop=True) 
