import requests
from aiogram import Bot, Dispatcher, types, Router, F
from aiogram.types import CallbackQuery
from aiogram.types.web_app_info import WebAppInfo
from aiogram.client.default import DefaultBotProperties
from aiogram.filters import CommandStart, Command
from aiogram.enums import ParseMode
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.filters.callback_data import CallbackData

import asyncio
import logging

dp = Dispatcher()
router = Router(name=__name__)
dp.include_router(router)
bot = Bot('7144526471:AAG2XsY2tw9lJUVbx_x4z2Rhssiuk6IAaCg', default=DefaultBotProperties(parse_mode=ParseMode.HTML))


class CallBackMethod(CallbackData, prefix="method-name"):
    string: str


kb = InlineKeyboardBuilder()
kb.button(text='Приду', callback_data=CallBackMethod(string='register').pack())
kb.button(text='Не приду', callback_data=CallBackMethod(string='unregister').pack())
kb.button(text='Кто идет?', web_app=WebAppInfo(url='https://bogdansavel.github.io/kk-bot-front/#/members'))


@dp.message(Command("event"))
async def start(message: types.Message):
    message = await message.answer("Run", reply_markup=kb.as_markup())
    url = 'http://localhost:8080/telegram-message'
    body = {'messageId': message.message_id, 'chatId': message.chat.id}
    requests.post(url, json=body)
    message = await bot.send_message(chat_id="-1781270027", text="start", reply_markup=kb.as_markup())


@dp.message(Command("stop"))
async def stop_event(message: types.Message):
    url = 'http://localhost:8080/event'
    response = requests.get(url)
    for message in response.json()["messages"]:
        await bot.edit_message_text(message_id=message["messageId"],
                                    chat_id=message["chatId"],
                                    text="stop")


@router.callback_query(CallBackMethod.filter(F.string == 'register'))
async def register(callback_query: CallbackQuery):
    text = ""
    url = 'http://localhost:8080/register'
    body = {'username': callback_query.from_user.username}
    response = requests.post(url, json=body)
    if response.ok:
        if response.json()["isAlreadyRegistered"] == True:
            text = "Вы уже зарегестрированны на этот киноклуб."
        else:
            text = f"Cпасибо за регистрацию!\n\n Всего зарегалоcь {response.json()["membersCount"]} человек. Если у вас изменятся планы, не забудьте вернуться сюда, и нажать кнопку \"Не приду\"."
            for message in response.json()["messages"]:
                await bot.edit_message_text(message_id=message["messageId"],
                                            chat_id=message["chatId"],
                                            text=f"{response.json()["membersCount"]}/15",
                                            reply_markup=kb.as_markup())
    else:
        text = "Что-то пошло не так!"

    await callback_query.answer(text=text, show_alert=True)


@router.callback_query(CallBackMethod.filter(F.string == 'unregister'))
async def unregister(callback_query: CallbackQuery):
    text = ""
    url = 'http://localhost:8080/unregister'
    body = {'username': callback_query.from_user.username}
    response = requests.post(url, json=body)
    if response.ok:
        text = "Регистрация отменена.\nCпасибо что уведомили!"
        for message in response.json()["messages"]:
            await bot.edit_message_text(message_id=message["messageId"],
                                    chat_id=message["chatId"],
                                    text=f"{response.json()["membersCount"]}/15",
                                    reply_markup=kb.as_markup())
    elif response.status_code == 404:
        text = "Вы еще не зарегестрированны на этот киноклуб"
    else:
        text = "Что-то пошло не так!"
    await callback_query.answer(text=text, show_alert=True)


async def main() -> None:
    logging.basicConfig(level=logging.DEBUG)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
