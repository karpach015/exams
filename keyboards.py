from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
import config


def get_location_status(location: str):
    if config.settings[location]:
        return "✅"
    else:
        return "❌"


def get_select_location_kb():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text=f"Tallinn {get_location_status('Tallinn')}", callback_data="change_state:Tallinn"),
                InlineKeyboardButton(text=f"Pärnu {get_location_status('Pärnu')}", callback_data="change_state:Pärnu"),
                InlineKeyboardButton(text=f"Tartu {get_location_status('Tartu')}", callback_data="change_state:Tartu")
            ],
            [
                InlineKeyboardButton(text=f"Haapsalu {get_location_status('Haapsalu')}", callback_data="change_state:Haapsalu"),
                InlineKeyboardButton(text=f"Jõhvi {get_location_status('Jõhvi')}", callback_data="change_state:Jõhvi"),
                InlineKeyboardButton(text=f"Kuressaare {get_location_status('Kuressaare')}", callback_data="change_state:Kuressaare")
            ],
            [
                InlineKeyboardButton(text=f"Narva {get_location_status('Narva')}", callback_data="change_state:Narva"),
                InlineKeyboardButton(text=f"Paide {get_location_status('Paide')}", callback_data="change_state:Paide"),
                InlineKeyboardButton(text=f"Rakvere {get_location_status('Rakvere')}", callback_data="change_state:Rakvere")
            ],
            [
                InlineKeyboardButton(text=f"Rapla {get_location_status('Rapla')}", callback_data="change_state:Rapla"),
                InlineKeyboardButton(text=f"Viljandi {get_location_status('Viljandi')}", callback_data="change_state:Viljandi"),
                InlineKeyboardButton(text=f"Võru {get_location_status('Võru')}", callback_data="change_state:Võru"),
            ],
            [InlineKeyboardButton(text=f"Hide menu", callback_data="change_state:hide")],
        ],
        resize_keyboard=True,
    )
