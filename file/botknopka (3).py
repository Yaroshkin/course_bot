# -*- coding: utf-8 -*-
import telebot
import requests
import json

from telebot import types
from api import TOKEN, API_KEY

bot = telebot.TeleBot(TOKEN)
URL = 'https://api.openweathermap.org/data/2.5/weather'
SELECT_CITY = "?q={0}&appid={1}"

@bot.message_handler(commands=['start'])
def start(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row('Погода 🌦', 'Курс 💲')
    bot.send_message(message.chat.id, text="Привіт, {0.first_name}! Обери, що тобі показати ".format(message.from_user), reply_markup=markup)


@bot.message_handler(content_types=['text'])
def text(message):
    if message.text == 'Погода 🌦':
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        markup.row('Днепр ','Киев','Запорожье','Кривой рог')
        markup.row('Одесса','Львов','Харьков','Донецк')
        markup.row('Назад ⬅')
        bot.send_message(message.chat.id, text="Обери, погоду якого міста показати".format(message.from_user), reply_markup=markup)
    elif message.text == 'Днепр':
        ent(message)
    elif message.text == 'Киев':
        ent(message)
    elif message.text == 'Запорожье':
        ent(message)
    elif message.text == 'Кривой рог':
        ent(message)
    elif message.text == 'Одесса':
        ent(message)
    elif message.text == 'Львов':
        ent(message)
    elif message.text == 'Харьков':
        ent(message)
    elif message.text == 'Донецк':
        ent(message)
    elif message.text == 'Назад ⬅':
        start(message)
    elif message.text == 'Курс 💲':
        response = requests.get('https://api.privatbank.ua/p24api/pubinfo?json&exchange&coursid=5')
        json_data = json.loads(response.text)
        emoji ={'USD': '$', 'EUR': '€', 'BTC': '₿'}
        textmg=''
        for babki in json_data:
            textmg += emoji[babki["ccy"]]+' '+babki["ccy"]+'   '+babki["buy"]+'  '+babki["sale"]+'\n'
        bot.send_message(message.chat.id, textmg)

def ent(message):
    response = requests.get(URL + SELECT_CITY.format(message.text, API_KEY))
    json_dt = json.loads(response.text)
    print(json_dt)
    txtw = ''
    weath = json_dt.get('weather')
    if weath[0]['description'] == 'overcast clouds':
        weath[0]['description'] = 'Хмарно ☁'
    elif weath[0]['description'] == 'light rain':
        weath[0]['description'] = 'Легкий дощ ☔'
    elif weath[0]['description'] == 'clear sky':
        weath[0]['description'] = 'Ясно 🌤'
    elif weath[0]['description'] == 'moderate rain':
        weath[0]['description'] = 'Легкий дощ 🌦'
    elif weath[0]['description'] == 'scattered clouds':
        weath[0]['description'] = 'Розсіяні хмари ⛅'
    elif weath[0]['description'] == 'few clouds':
        weath[0]['description'] = 'Трохи хмарно ⛅'
    print(weath[0]['description'])
    # for weath in json_dt['weather']:
    #     print(weath['description'])
    # if weath['description'] == 'overcast clouds':
    #     weath['description'] == 'хмарно'
    wind = json_dt.get('wind')
    temp = json_dt.get('main')
    country = json_dt.get('sys')
    if country['country'] == 'UA':
        country['country'] += '🇺🇦'
    
    print(country['country'])
    print(float(("{0:.1f}").format(temp['temp']-273.15)))
    print(float(("{0:.1f}").format(temp['feels_like']-273.15)))
    print(temp['feels_like'])
    print(temp['humidity'])
    print(json_dt['name'])
    iconT = ''
    if temp['temp']-273.15 < 0:
        iconT = '🥶'
    elif temp['temp']-273.15 > 0:
        iconT = '🥵'

    iconV = ''
    if temp['feels_like']-273.15 <0:
        iconV = '🥶'
    else:
        iconV = "🥵"
        
    txtw += json_dt['name']+ ' ' + f'{country["country"]}' + '\n' + f"{weath[0]['description']}" + '\n'  +f"Швидкість вітру {wind['speed']} м/с 🌬" + "\n" + f'Температура повітря {float(("{0:.1f}").format(temp["temp"]-273.15))} ºC '+ iconT + '\n' + f'Відчувається як {float(("{0:.1f}").format(temp["feels_like"]-273.15))} ºC'+ iconV + '\n' + f'Вологість повітря {temp["humidity"]}%'
    bot.send_message(message.chat.id,txtw)
    




bot.polling(non_stop=True)
