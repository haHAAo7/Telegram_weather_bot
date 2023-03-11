import requests
import os
import pip
import telebot
from background import keep_alive  # импорт функции для поддержки работоспособности

pip.main(['install', 'pytelegrambotapi'])

bot_token = os.environ['bot_token']
weather_key = os.environ['weather_key']
bot = telebot.TeleBot(bot_token)


@bot.message_handler(commands=['start'])
def start_handler(message):
    user_name = message.from_user.full_name
    bot.send_message(message.from_user.id,
                     (f'Привет {user_name}, я могу подсказывать погоду. Для начала укажи место через команду /region'))


@bot.message_handler(commands=['region'])
def region_handler(message):
    bot.send_message(message.from_user.id, ('Напиши место, в котором хочешь узнать погоду'))
    bot.register_next_step_handler(message, region_saver)


def region_saver(message):
    global region
    region = message.text
    bot.reply_to(message,
                 (f'Указан регион - {region}, теперь вы можете посмотреть погоду на сегодня или ближайшие 3 дня'))


@bot.message_handler(commands=['today'])
def today_weather(message):
    try:
        url = requests.get(f"http://api.weatherapi.com/v1/current.json?key={weather_key}&q={region}&aqi=no&lang=ru")
        data = url.json()
        try:
            temp = data['current']['temp_c']
            temp_feels = data['current']['feelslike_c']
            condition = data['current']['condition']['text']
            wind = data['current']['wind_kph']
            bot.send_message(message.from_user.id,
                             f"Температура воздуха {temp} градуса, {condition} \nОщущается как {temp_feels} градуса\n Скорость ветра {wind} км/ч")
        except KeyError:
            bot.send_message(message.from_user.id, "Нет информации по выбраному месту")
    except NameError:
        bot.send_message(message.from_user.id, "Вы не выбрали регион")


@bot.message_handler(content_types=['text'])
def get_text_message(message):
    bot.send_message(message.from_user.id, "Для начала работы укажи регион через /region")


# echo-функция, которая отвечает на любое текстовое сообщение таким же текстом

keep_alive()  # запускаем flask-сервер в отдельном потоке.
bot.polling(non_stop=True, interval=0)  # запуск бота
