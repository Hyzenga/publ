import asyncio
from aiogram import Bot, Dispatcher, types, F
import aiohttp
from aiogram.client.session.aiohttp import AiohttpSession

# можно переместить токены в отдельный файл для безопасности,
# но т.к. этот проект не будет рекламироваться и будет пользоваться спросом только у наших знакомых, я не стала 
BOT_TOKEN = '8381867482:AAGHXw20DPts6hg-KYX1P-BF7X9N-kOJnjs'
WEATHER_API_TOKEN = 'f1c1ac116ae46845e84a4278e8d211ca'

# настройка прокси для PythonAnywhere
session = AiohttpSession(proxy="http://proxy.server:3128")
weatherlen_bot = Bot(token=BOT_TOKEN, session=session)

dp = Dispatcher()

async def get_weather(city: str):
    import datetime
    async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(ssl=False)) as session:
        async with session.get(
            url="https://api.openweathermap.org/data/2.5/forecast",
            params={
                'q': city,
                'appid': WEATHER_API_TOKEN,
                'units': 'metric',
                'lang': 'ru',
            },
            proxy="http://proxy.server:3128"
        ) as response:
            if response.status != 200:
                return "Неизвестный город"

            data = await response.json()
            try:
                # 1. данные на текущий момент
                current = data['list'][0]
                # округляем температуру до целых чисел с помощью int()
                temp = int(current['main']['temp'])
                feels_like = int(current['main']['feels_like'])

                description = current['weather'][0]['description']
                wind_speed = current['wind']['speed']
                humidity = current['main']['humidity']
                pressure_mm = int(current['main']['pressure'] * 0.750064)
                visibility = current.get('visibility', 0) / 1000

                # время солнца
                sunrise = datetime.datetime.fromtimestamp(data['city']['sunrise']).strftime('%H:%M')
                sunset = datetime.datetime.fromtimestamp(data['city']['sunset']).strftime('%H:%M')

                # 2. прогноз (тоже округляем до целых)
                tomorrow_temp = int(data['list'][8]['main']['temp'])
                tomorrow_desc = data['list'][8]['weather'][0]['description']

                day_after_temp = int(data['list'][16]['main']['temp'])
                day_after_desc = data['list'][16]['weather'][0]['description']

                res = (f"СЕЙЧАС В ГОРОДЕ {city.upper()}:\n"
                       f"Температура: {temp}°C (ощущается как {feels_like}°C)\n"
                       f"Осадки: {description}\n"
                       f"Ветер: {wind_speed} м/с\n"
                       f"Влажность: {humidity}%\n"
                       f"Давление: {pressure_mm} мм рт. ст.\n"
                       f"Видимость: {visibility} км\n"
                       f"Восход: {sunrise} | Закат: {sunset}\n\n"
                       f"ПРОГНОЗ:\n"
                       f"Завтра: {tomorrow_temp}°C, {tomorrow_desc}\n"
                       f"Послезавтра: {day_after_temp}°C, {day_after_desc}")
                return res
            except (KeyError, IndexError, Exception):
                return "Ошибка при обработке данных погоды"


@dp.message(F.text)
async def start_handler(message: types.Message):
    weather_location = message.text.strip()
    weather = await get_weather(city=weather_location)
    await message.answer(f'Погода в {weather_location}:\n\n{weather}')

if __name__ == '__main__':
    asyncio.run(dp.start_polling(weatherlen_bot))
