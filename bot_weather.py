import logging
import requests
import json
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor
import os
import asyncio

load_dotenv()

API_TOKEN = os.getenv('TOKEN')
API_KEY = os.getenv('API_KEY')

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

URL = 'https://api.openweathermap.org/data/2.5/weather'
SELECT_CITY = "?q={0}&appid={1}"

# Логирование для отладки
logging.basicConfig(level=logging.INFO)

# Словарь для городов
cities = ['Днепр', 'Киев', 'Запорожье', 'Кривой рог', 'Одесса', 'Львов', 'Харьков', 'Донецк','Луцк']

# Кэширование курса валют
cached_currency = None

@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row('Погода 🌦', 'Курс 💲')
    await message.answer(f"Привет, {message.from_user.first_name}! Обери, что тебе показать", reply_markup=markup)

@dp.message_handler(content_types=['text'])
async def text(message: types.Message):
    global cached_currency
    if message.text == 'Погода 🌦':
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        
        for i in range(0, len(cities), 4):
            markup.row(*cities[i:i+4])
        markup.row('Назад ⬅')

        await message.answer("Выбери, погоду какого города показать", reply_markup=markup)
    elif message.text in cities:
        await ent(message)
    elif message.text == 'Назад ⬅':
        await start(message)
    elif message.text == 'Курс 💲':
        if not cached_currency:
            await update_currency_cache()
        await message.answer(cached_currency)

async def update_currency_cache():
    global cached_currency
    try:
        response = requests.get('https://api.privatbank.ua/p24api/pubinfo?json&exchange&coursid=5')
        response.raise_for_status()
        json_data = json.loads(response.text)
        emoji = {'USD': '$', 'EUR': '€', 'BTC': '₿'}
        textmg = ''
        for babki in json_data:
            textmg += emoji.get(babki["ccy"], '') + ' ' + babki["ccy"] + '   ' + babki["buy"] + '  ' + babki["sale"] + '\n'
        cached_currency = textmg
    except requests.exceptions.RequestException as e:
        cached_currency = "Не удалось получить курс валют. Попробуйте позже."
        logging.error(f"Error fetching currency data: {e}")

async def ent(message: types.Message):
    try:
        response = requests.get(URL + SELECT_CITY.format(message.text, API_KEY))
        response.raise_for_status()
        json_dt = json.loads(response.text)
        
        txtw = ''
        weath = json_dt.get('weather')
        if weath:
            if weath[0]['description'] == 'overcast clouds':
                weath[0]['description'] = 'Облачно ☁'
            elif weath[0]['description'] == 'light rain':
                weath[0]['description'] = 'Легкий дождь ☔'
            elif weath[0]['description'] == 'clear sky':
                weath[0]['description'] = 'Ясно 🌤'
            elif weath[0]['description'] == 'moderate rain':
                weath[0]['description'] = 'Легкий дождь 🌦'
            elif weath[0]['description'] == 'scattered clouds':
                weath[0]['description'] = 'Рассеянные облака ⛅'
            elif weath[0]['description'] == 'few clouds':
                weath[0]['description'] = 'Немного облачно ⛅'
            
            wind = json_dt.get('wind')
            temp = json_dt.get('main')
            country = json_dt.get('sys')
            if country and country.get('country') == 'UA':
                country['country'] += '🇺🇦'
            
            iconT = '🥶' if temp['temp'] - 273.15 < 10 else '🥵' if temp['temp'] - 273.15 > 10 else ''
            iconV = '🥶' if temp['feels_like'] - 273.15 < 10 else '🥵'
            
            txtw += json_dt['name'] + ' ' + f'{country["country"]}' + '\n' + f"{weath[0]['description']}" + '\n' + \
                    f"Скорость ветра {wind['speed']} м/с 🌬" + "\n" + \
                    f'Температура воздуха {float(("{0:.1f}").format(temp["temp"] - 273.15))} ºC ' + iconT + '\n' + \
                    f'Ощущается как {float(("{0:.1f}").format(temp["feels_like"] - 273.15))} ºC' + iconV + '\n' + \
                    f'Влажность воздуха {temp["humidity"]}%'
            await message.answer(txtw)
        else:
            await message.answer("Не удалось получить данные о погоде. Попробуйте снова.")
    except requests.exceptions.RequestException as e:
        await message.answer("Ошибка при запросе погоды. Попробуйте позже.")
        logging.error(f"Error fetching weather data for {message.text}: {e}")

if __name__ == '__main__':
    from aiogram import executor
    executor.start_polling(dp, skip_updates=True)
