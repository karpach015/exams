import config
import asyncio
import requests
from bs4 import BeautifulSoup as Bs
from aiogram import Bot, Dispatcher, executor, types
from datetime import datetime, timedelta
import callback
import keyboards

bot = Bot(token=config.API_TOKEN)
dp = Dispatcher(bot)

first_time_dict = {
    "Haapsalu": None,
    "Jõhvi": None,
    "Kuressaare": None,
    "Narva": None,
    "Paide": None,
    "Pärnu": None,
    "Rakvere": None,
    "Rapla": None,
    "Tallinn": None,
    "Tartu": None,
    "Viljandi": None,
    "Võru": None
}
# before_date = datetime.now() + timedelta(days=365)
before_date = datetime.strptime("26.06.21", "%d.%m.%y")


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


@dp.message_handler(commands="before")
async def search_date_from(msg: types.Message):
    date_str = msg.text.split("before ")[1]
    if len(date_str) == 8:
        date = datetime.strptime(date_str, "%d.%m.%y")
    elif len(date_str) == 10:
        date = datetime.strptime(date_str, "%d.%m.%Y")
    elif len(date_str) == 5:
        day_month = datetime.strptime(date_str, "%d.%m")
        date = datetime(year=datetime.today().year, month=day_month.month, day=day_month.day)

    change_before_date(date)
    await msg.answer(f"Поиск времён до {before_date.strftime('%d.%m.%Y')}")


def change_before_date(date: datetime):
    global before_date
    before_date = date


async def main_loop(wait_time: int):
    await bot.send_message("466455737", "Бот перезапустился!")
    await bot.send_message("466455737", f"Поиск времён до {before_date.strftime('%d.%m.%Y')}")
    while True:
        await asyncio.sleep(wait_time)
        await parse()


async def parse():
    url = "https://eteenindus.mnt.ee/public/vabadSoidueksamiajad.xhtml"
    response = requests.get(url)
    html = Bs(response.content, 'html.parser')

    try:
        times = {
            elem.select(".eksam-ajad-byroo span")[0].text: datetime.strptime(elem.select(".eksam-ajad-aeg")[0].text,
                                                                             "%d.%m.%Y %H:%M") for elem in
            html.select("table tbody")[0]}
    except IndexError:
        return None

    global first_time_dict
    global before_date
    for location, time in times.items():
        if location in config.settings:
            if not config.settings[location]:
                continue
        else:
            await bot.send_message("466455737", f"{location}: {time.strftime('%d.%m.%y %H:%M')}")
            continue

        first_time = first_time_dict[location]
        text = f"{location}: {time.strftime('%d.%m.%y %H:%M')}"

        if first_time is None:
            first_time_dict[location] = time
            await bot.send_message("466455737", text)
        elif before_date > time < first_time:
            first_time_dict[location] = time
            await bot.send_message("466455737", "Новое время")
            await bot.send_message("466455737", text)
        elif before_date > first_time < time:
            first_time_dict[location] = time
            await bot.send_message("466455737", "Время пропало")
            await bot.send_message("466455737", text)


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.create_task(main_loop(3))
    executor.start_polling(dp, skip_updates=True)
