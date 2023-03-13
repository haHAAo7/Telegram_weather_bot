import requests
import os
import pip
import telebot
from background import keep_alive  # импорт функции для поддержки работоспособности

pip.main(['install', 'pytelegrambotapi'])

bot_token = os.environ['bot_token']
weather_key = os.environ['weather_key']
bot = telebot.TeleBot(bot_token)
region_error = "Вы не выбрали регион"
region_fail = "Нет информации по выбраному региону"


@bot.message_handler(commands=['start'])
def start_handler(message):
    user_name = message.from_user.full_name
    bot.send_message(message.from_user.id,
                     (f'Привет {user_name}, я могу подсказывать погоду. Для начала укажи место через команду /region'))


@bot.message_handler(commands=['region'])
def region_handler(message):
    bot.send_message(message.from_user.id, ('Укажите место, для которого хотите узнать прогноз погоды'))
    bot.register_next_step_handler(message, region_saver)


def region_saver(message):
    global region
    region = message.text
    bot.reply_to(message,
                 (f'Указан регион - {region}, теперь вы можете узнать прогноз погоды'))


@bot.message_handler(commands=['now'])
def now_weather(message):
    try:
        url = requests.get(f"http://api.weatherapi.com/v1/current.json?key={weather_key}&q={region}&aqi=no&lang=ru")
        data = url.json()
        try:
            temp = data['current']['temp_c']
            temp_feels = data['current']['feelslike_c']
            condition = data['current']['condition']['text']
            wind = data['current']['wind_kph']
            bot.send_message(message.from_user.id,
                             f"Температура воздуха {temp} градуса, {condition}. \nОщущается как {temp_feels} градуса. \nСкорость ветра {wind} км/ч")
        except KeyError:
            bot.send_message(message.from_user.id, region_fail)
    except NameError:
        bot.send_message(message.from_user.id, region_error)


@bot.message_handler(commands=['today'])
def today_weather(message):
    try:
        url = requests.get(
            f"http://api.weatherapi.com/v1/forecast.json?key={weather_key}&q={region}&days=1&aqi=no&alerts=no&lang=ru")
        data = url.json()
        day = data['forecast']['forecastday'][0]['hour']
        weather_today = "Погода на сегодня:\n"
        try:
            for hour in day:
                time = hour['time'].partition(' ')[2]
                temp = str(hour['temp_c'])
                condition = hour['condition']['text']
                weather_today += f'{time} — {temp} градуса. {condition}\n'
            bot.send_message(message.from_user.id, weather_today)
        except KeyError:
            bot.send_message(message.from_user.id, region_fail)
    except NameError:
        bot.send_message(message.from_user.id, region_error)


@bot.message_handler(commands=['tomorrow'])
def tomorrow_weather(message):
    try:
        url = requests.get(
            f"http://api.weatherapi.com/v1/forecast.json?key={weather_key}&q={region}&days=2&aqi=no&alerts=no&lang=ru")
        data = url.json()
        weather_tomorrow = "Погода на завтра:\n"
        try:
            day = data["forecast"]["forecastday"][1]
            condition = day['day']['condition']['text']
            morning = f"\nПогода утром: {day['hour'][0]['temp_c']} — {day['hour'][5]['temp_c']}.\n"
            daytime = f"Погода днем: {day['hour'][6]['temp_c']} — {day['hour'][11]['temp_c']}\n"
            evening = f"Погода вечером: {day['hour'][12]['temp_c']} — {day['hour'][17]['temp_c']}\n"
            night = f"Погода ночью: {day['hour'][18]['temp_c']} — {day['hour'][23]['temp_c']}\n"
            weather_tomorrow += condition + morning + daytime + evening + night
            bot.send_message(message.from_user.id, weather_tomorrow)
        except KeyError:
            bot.send_message(message.from_user.id, region_fail)
    except NameError:
        bot.send_message(message.from_user.id, region_error)


@bot.message_handler(content_types=['text'])
def get_text_message(message):
    bot.send_message(message.from_user.id, "Для начала работы укажи регион через /region")


keep_alive()  # запускаем flask-сервер в отдельном потоке.
bot.polling(non_stop=True, interval=0)  # запуск бота
