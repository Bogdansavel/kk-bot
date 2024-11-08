import requests
from aiogram import Bot, Dispatcher, types, Router, F
from aiogram.types import CallbackQuery, FSInputFile, InputMediaPhoto
from aiogram.types.web_app_info import WebAppInfo
from aiogram.client.default import DefaultBotProperties
from aiogram.filters import CommandStart, Command
from aiogram.enums import ParseMode
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.filters.callback_data import CallbackData

import asyncio
import logging

from requests import Response

dp = Dispatcher()
router = Router(name=__name__)
dp.include_router(router)
token = "7284814693:AAEQ2YLnQ2ukjFprZ5tE42lvTZNR7No3t1I"
tokenTest = "7869224203:AAGzt9yufaPGqYEk5DQcyVbFJ5t6BSiZ5_A"
bot = Bot(token, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
# baseUrl = "https://kk-backend-619198175847.europe-central2.run.app"
baseUrl = "http://localhost:8080"


class CallBackMethod(CallbackData, prefix="method-name"):
    string: str


kb = InlineKeyboardBuilder()
kb.button(text='Кто идет?', web_app=WebAppInfo(url='https://bogdansavel.github.io/kk-bot-front/#/members'))

kbrate = InlineKeyboardBuilder()
kbrate.button(text='Оценить', web_app=WebAppInfo(url='https://bogdansavel.github.io/kk-bot-front/#/rates/13acceca-3ccd-40b4-aec7-1d05e78746ef'))

kb2 = InlineKeyboardBuilder()
kb2.button(text='Приду', callback_data=CallBackMethod(string='register').pack())
kb2.button(text='Не приду', callback_data=CallBackMethod(string='unregister').pack())
kb2.adjust(2)
caption = "<b>Хэллоуинский спешл Киноклуба в Кракове!</b>\n\nСмотрим, обсуждаем, рассуждаем и делимся своими впечатлениями о фильме \"Солнцестояние\". В кругу людей, любящих кино.\n\nВоскресенье.\n3 ноября. 17:00.\nКраков, Św. Krzyża 11.\n\nХэллоуинские маски, наряды, свечи и украшения приветствуются!"
max = 15


@dp.message(Command("start"))
async def start(message: types.Message):
    await bot.send_photo(chat_id=message.chat.id, photo=FSInputFile(path='RateMidsommar.png'), reply_markup=kbrate.as_markup())


@dp.message(Command("test"))
async def test(message: types.Message):
    if message.from_user.username == "fanboyDan":
        message = await bot.send_photo(message.chat.id, photo=FSInputFile(path='KKposter.png'),
                                       caption=caption + "\n\n0/15 человек",
                                       parse_mode="HTML",
                                       reply_markup=kb2.as_markup())
        url = baseUrl + '/telegram-message'
        body = {'messageId': message.message_id, 'chatId': message.chat.id}
        requests.post(url, json=body)


@dp.message(Command("event"))
async def event(message: types.Message):
    if message.from_user.username == "fanboyDan":
        message = await bot.send_photo("@kkkrakow", photo=FSInputFile(path='KKposter.png'),
                                       caption=caption + "\n\n0/15 человек",
                                       parse_mode="HTML",
                                       reply_markup=kb2.as_markup())
        url = baseUrl + '/telegram-message'
        body = {'messageId': message.message_id, 'chatId': "@kkkrakow"}
        requests.post(url, json=body)

        message = await bot.send_photo("-1002499953530", photo=FSInputFile(path='KKposter.png'),
                                       caption=caption + "\n\n0/15 человек",
                                       parse_mode="HTML",
                                       reply_markup=kb2.as_markup())
        url = baseUrl + '/telegram-message'
        body = {'messageId': message.message_id, 'chatId': "-1002499953530"}
        requests.post(url, json=body)


@dp.message(Command("киноклуб"))
async def latest(message: types.Message):
    await bot.send_photo(message.chat.id, photo=FSInputFile(path='KKposter.png'), reply_markup=kb.as_markup())


@dp.message(Command("stop"))
async def stop_event(message: types.Message):
    if message.from_user.username == "fanboyDan":
        url = baseUrl + '/event'
        response = requests.get(url)
        for message in response.json()["messages"]:
            await bot.edit_message_caption(message_id=message["messageId"],
                                        chat_id=message["chatId"],
                                        caption=caption)


@dp.message(Command("rate"))
async def rate(message: types.Message):
    if message.from_user.username == "fanboyDan":
        await message.answer(photo=FSInputFile(path='KKposter.png'), reply_markup=kbrate.as_markup(), text="rate")


@dp.message(Command("startEvent"))
async def start_event(message: types.Message):
    if message.from_user.username == "fanboyDan":
        url = baseUrl + '/event'
        response = requests.get(url)
        for message in response.json()["messages"]:
            await bot.edit_message_caption(message_id=message["messageId"],
                                               chat_id=message["chatId"],
                                               caption=caption,
                                               reply_markup=kb2.as_markup())


@dp.message(Command("update"))
async def update_event_info(message: types.Message):
    if message.from_user.username == "fanboyDan":
        url = baseUrl + '/message/current'
        response = requests.get(url)
        if response.ok:
            for m in response.json():
                await bot.edit_message_media(media=InputMediaPhoto(media=FSInputFile(path='KKposter.png'),
                                                                   caption=caption),
                                             message_id=m["messageId"], chat_id=m["chatId"])
                await message.answer("Update has been done successfully")
        else:
            await message.answer("Somthing went wrong")


@router.callback_query(CallBackMethod.filter(F.string == 'register'))
async def register(callback_query: CallbackQuery):
    url = baseUrl + '/register'
    body = {'username': callback_query.from_user.username}
    response = requests.post(url, json=body)
    if response.ok:
        if response.json()["isAlreadyRegistered"] == True:
            text = "Вы уже зарегестрированны на этот киноклуб."
        else:
            text = f"Cпасибо за регистрацию!\n\n Если у вас изменятся планы, не забудьте вернуться сюда, и нажать кнопку \"Не приду\"."
            await update_event_message(response)
    else:
        text = "Что-то пошло не так!"
    await callback_query.answer(text=text, show_alert=True)


@router.callback_query(CallBackMethod.filter(F.string == 'unregister'))
async def unregister(callback_query: CallbackQuery):
    url = baseUrl + '/unregister'
    body = {'username': callback_query.from_user.username}
    response = requests.post(url, json=body)
    if response.ok:
        text = "Регистрация отменена.\nCпасибо что уведомили!"
        for message in response.json()["messages"]:
            await update_event_message(response)
    elif response.status_code == 404:
        text = "Вы еще не зарегестрированны на этот киноклуб"
    else:
        text = "Что-то пошло не так!"
    await callback_query.answer(text=text, show_alert=True)


async def update_event_message(response: Response):
    usernames = list(map(lambda m: "@" + m["username"], response.json()['members']))
    for message in response.json()["messages"]:
        final_caption = caption + f"\n\n{response.json()['membersCount']}/{max} человек"
        if message["chatId"] == "-1002499953530":
            final_caption = final_caption + "\n\n" + "\n\n".join(usernames)
        await bot.edit_message_caption(message_id=message["messageId"],
                                       chat_id=message["chatId"],
                                       caption=final_caption,
                                       reply_markup=kb2.as_markup())


async def main() -> None:
    logging.basicConfig(level=logging.DEBUG)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
