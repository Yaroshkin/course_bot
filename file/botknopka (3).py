# -*- coding: utf-8 -*-
import time
import telebot
import requests
import json
from bs4 import BeautifulSoup
from telebot import *
from file.api import TOKEN, API_KEY

bot = telebot.TeleBot(TOKEN)
URL = 'https://api.openweathermap.org/data/2.5/weather'
SELECT_CITY = "?q={0}&appid={1}"

@bot.message_handler(commands=['start'])
def start(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row('Погода 🌦', 'Курс 💲')
    bot.send_message(message.chat.id, text="Привіт, {0.first_name}! Обери, що тобі показати".format(message.from_user), reply_markup=markup)


@bot.message_handler(content_types=['text'])
def text(message):
    if message.text == 'Погода 🌦':
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        markup.row('Dnipro')
        markup.row('Назад')
        bot.send_message(message.chat.id, text="Обери, погоду якого міста показати".format(message.from_user), reply_markup=markup)
    elif message.text == 'Dnipro':
        response = requests.get(URL + SELECT_CITY.format('Dnipro', API_KEY))
        json_dt = json.loads(response.text)
        print(json_dt)
        for weath in json_dt['weather']:
            print(weath['description'])
        bot.send_message(message.chat.id,json_dt)
    elif message.text == 'Назад':
        start(message)
    elif message.text == 'Курс 💲':
        response = requests.get('https://api.privatbank.ua/p24api/pubinfo?json&exchange&coursid=5')
        json_data = json.loads(response.text)
        emoji ={'USD': '$', 'EUR': '€', 'BTC': '₿'}
        textmg=''
        for babki in json_data:
            textmg += emoji[babki["ccy"]]+' '+babki["ccy"]+'   '+babki["buy"]+'  '+babki["sale"]+'\n'
        bot.send_message(message.chat.id, textmg)




bot.polling(non_stop=True)
