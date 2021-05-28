import config
import asyncio
import requests
from bs4 import BeautifulSoup as Bs
from aiogram import Bot, Dispatcher, executor, types
from datetime import datetime, timedelta
import callback, keyboards

bot = Bot(token=config.API_TOKEN)
dp = Dispatcher(bot)

first_time = None
before_date = datetime.now() + timedelta(days=365)


@dp.message_handler(commands="test")
async def test(msg):
    if config.test:
        config.test = False
    else:
        config.test = True


@dp.callback_query_handler(callback.search_settings.filter())
async def change_location_settings(call: types.CallbackQuery):
    location = call.data.split(':')[1]
    if location == "hide":
        await call.message.delete()
        return
    if config.settings[location]:
        config.settings[location] = False
        await call.message.edit_reply_markup(reply_markup=keyboards.get_select_location_kb())
    else:
        config.settings[location] = True
        await call.message.edit_reply_markup(reply_markup=keyboards.get_select_location_kb())


@dp.message_handler(commands="settings")
async def change_settings(msg: types.Message):
    await msg.answer("Выбери места для поиска", reply_markup=keyboards.get_select_location_kb())


@dp.message_handler(commands="from")
async def search_date_from(msg: types.Message):
    date_str = msg.text.split("from ")[1]
    try:
        date = datetime.strptime(date_str, "%d.%m.%Y")
    except ValueError:
        date = datetime.strptime(date_str, "%d.%m.%y")

    change_date_from(date)
    await msg.answer(f"Поиск времён начиная с {before_date}")


def change_date_from(date: datetime):
    global before_date
    before_date = date


async def main_loop(wait_time: int):
    while True:
        await asyncio.sleep(wait_time)
        await parse()


async def parse():
    url = "https://eteenindus.mnt.ee/public/vabadSoidueksamiajad.xhtml"
    response = requests.get(url)
    html = Bs(response.content, 'html.parser')

    try:
        times = {elem.select(".eksam-ajad-byroo span")[0].text: datetime.strptime(elem.select(".eksam-ajad-aeg")[0].text, "%d.%m.%Y %H:%M") for elem in html.select("table tbody")[0]}
    except IndexError:
        return None

    if config.test:
        times = {"Tallinn": datetime.strptime('31.05.2021 10:00', '%d.%m.%Y %H:%M')}

    sorted_times = sorted(times.items(), key=lambda x: x)
    sorted_times = [(x[0], x[1]) for x in sorted_times if config.settings[x[0]]]

    text = "\n".join([f"{time[0]}: {time[1].strftime('%d.%m.%Y %H:%M')}" for time in sorted_times])

    global first_time
    global before_date

    if first_time is None:
        first_time = sorted_times[0][1]
        await bot.send_message("466455737", "Бот перезапустился\nВсе фильтры сброшенны!")
        await bot.send_message("466455737", text)
    elif before_date > sorted_times[0][1] < first_time:
        first_time = sorted_times[0][1]
        await bot.send_message("466455737", "Новое время")
        await bot.send_message("466455737", text)
    elif before_date > first_time < sorted_times[0][1]:
        first_time = sorted_times[0][1]
        await bot.send_message("466455737", "Время пропало")
        await bot.send_message("466455737", text)

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.create_task(main_loop(30))
    executor.start_polling(dp, skip_updates=True)
