import requests
from aiogram import Bot, Dispatcher, types, Router, F
from aiogram.types import CallbackQuery, FSInputFile
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
baseUrl = "https://kk-backend-619198175847.europe-central2.run.app"


class CallBackMethod(CallbackData, prefix="method-name"):
    string: str


kb = InlineKeyboardBuilder()
kb.button(text='Приду', callback_data=CallBackMethod(string='register').pack())
kb.button(text='Не приду', callback_data=CallBackMethod(string='unregister').pack())
kb.button(text='Кто идет?', web_app=WebAppInfo(url='https://bogdansavel.github.io/kk-bot-front/#/members'))
kb.adjust(2, 1)


@dp.message(Command("event"))
async def start(message: types.Message):
    message = await bot.send_photo("449566309", photo=FSInputFile(path='KKposter.png'),
                                   caption="Test",
                                   reply_markup=kb.as_markup())
    url = baseUrl + '/telegram-message'
    body = {'messageId': message.message_id, 'chatId': message.chat.id}
    requests.post(url, json=body)
    # message = await bot.send_message(chat_id="-1781270027", text="start", reply_markup=kb.as_markup())


@dp.message(Command("stop"))
async def stop_event(message: types.Message):
    url = baseUrl + '/event'
    response = requests.get(url)
    for message in response.json()["messages"]:
        await bot.edit_message_caption(message_id=message["messageId"],
                                    chat_id=message["chatId"],
                                    caption="stop")


@router.callback_query(CallBackMethod.filter(F.string == 'register'))
async def register(callback_query: CallbackQuery):
    text = ""
    url = baseUrl + '/register'
    body = {'username': callback_query.from_user.username}
    response = requests.post(url, json=body)
    if response.ok:
        if response.json()["isAlreadyRegistered"] == True:
            text = "Вы уже зарегестрированны на этот киноклуб."
        else:
            text = f"Cпасибо за регистрацию!\n\n Если у вас изменятся планы, не забудьте вернуться сюда, и нажать кнопку \"Не приду\"."
            for message in response.json()["messages"]:
                await bot.edit_message_caption(message_id=message["messageId"],
                                            chat_id=message["chatId"],
                                            caption=f"{response.json()["membersCount"]}/15",
                                            reply_markup=kb.as_markup())
    else:
        text = "Что-то пошло не так!"

    await callback_query.answer(text=text, show_alert=True)


@router.callback_query(CallBackMethod.filter(F.string == 'unregister'))
async def unregister(callback_query: CallbackQuery):
    text = ""
    url = baseUrl + '/unregister'
    body = {'username': callback_query.from_user.username}
    response = requests.post(url, json=body)
    if response.ok:
        text = "Регистрация отменена.\nCпасибо что уведомили!"
        for message in response.json()["messages"]:
            await bot.edit_message_caption(message_id=message["messageId"],
                                    chat_id=message["chatId"],
                                    caption=f"{response.json()["membersCount"]}/15",
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
