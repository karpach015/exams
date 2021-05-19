import config
import asyncio
import requests
from bs4 import BeautifulSoup as Bs
from aiogram import Bot, Dispatcher, executor, types
from datetime import datetime

bot = Bot(token=config.API_TOKEN)
dp = Dispatcher(bot)

first_time = None


async def main_loop(wait_time: int):
    while True:
        await asyncio.sleep(wait_time)
        await parse()


async def parse():
    url = "https://eteenindus.mnt.ee/public/vabadSoidueksamiajad.xhtml"
    response = requests.get(url)
    html = Bs(response.content, 'html.parser')

    try:
        times = {elem.select(".eksam-ajad-byroo span")[0].text: elem.select(".eksam-ajad-aeg")[0].text for elem in html.select("table tbody")[0]}
    except IndexError:
        return None

    times = {'Tallinn': times.get('Tallinn')}
    sorted_times = sorted(times.items(), key=lambda x: datetime.strptime(x[1], "%d.%m.%Y %H:%M"))

    text = "\n".join([f"{time[0]}: {time[1]}" for time in sorted_times])

    global first_time
    if first_time is None or sorted_times[0] < first_time:
        first_time = sorted_times[0]
        await bot.send_message("466455737", "Новое время")
        await bot.send_message("466455737", text)
    elif first_time < sorted_times[0]:
        await bot.send_message("466455737", "Время пропало")
        first_time = sorted_times[0]
        await bot.send_message("466455737", text)


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.create_task(main_loop(30))
    executor.start_polling(dp, skip_updates=True)
