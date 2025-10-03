import json

import requests
from aiogram import Bot, Dispatcher, types, Router, F
from aiogram.types import CallbackQuery, FSInputFile, InputMediaPhoto, URLInputFile
from aiogram.types.web_app_info import WebAppInfo
from aiogram.client.default import DefaultBotProperties
from aiogram.filters import Command, CommandObject
from aiogram.enums import ParseMode
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.filters.callback_data import CallbackData
from dotenv import load_dotenv
import os

import asyncio
import logging

from aiogram.utils.media_group import MediaGroupBuilder
from requests import Response

load_dotenv()
dp = Dispatcher()
router = Router(name=__name__)
dp.include_router(router)
token = os.environ['BOT_TOKEN']
bot = Bot(token, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
baseUrl = os.environ['BACKEND_URL']
group_chat_id = "-1002499953530"
channel_chat_id = "@kkkrakow"
rate_chat_id = 173


class CallBackMethod(CallbackData, prefix="method-name"):
    string: str
    event_id: str


ikb = InlineKeyboardBuilder()
ikb.button(text='Смогу', callback_data=CallBackMethod(string='ready', event_id="0").pack())
ikb.button(text='Не смогу', callback_data=CallBackMethod(string='notReady', event_id="0").pack())
ikb.adjust(2)

kb = InlineKeyboardBuilder()
kb.button(text='Кто идет?', web_app=WebAppInfo(url='https://bogdansavel.github.io/kk-bot-front/#/members'))

caption = "<b>Киноклуб в Кракове!</b>\n\nСмотрим, обсуждаем, рассуждаем и делимся своими впечатлениями о фильме \"Догвиль\"! В кругу людей, любящих кино.\n\nВоскресенье.\n19 января. 17:00.\nКраков, Łobzowska 15/15.\n\nЯзык: русская озвучка\nСтоимость: 10зл.\nОграничение количества учаcтников нестрогое."
max = 15


@dp.message(Command("start"))
async def start(message: types.Message, command: CommandObject):
    arg = command.args
    if arg == "ready":
        url = baseUrl + '/round/setReady'
        body = {"telegramId": message.from_user.id, "isReady": True}
        response = requests.post(url, json=body)
        text = update_round_message(response)
        await bot.edit_message_text(chat_id=response.json()['message']['chatId'],
                              message_id=response.json()['message']['messageId'],
                              text=text)
        await message.answer("Отлично! Спасибо что уведомили.")
    elif arg == "notReady":
        url = baseUrl + '/round/setReady'
        body = {"telegramId": message.from_user.id, "isReady": False}
        response = requests.post(url, json=body)
        text = update_round_message(response)
        await bot.edit_message_text(chat_id=response.json()['message']['chatId'],
                                    message_id=response.json()['message']['messageId'],
                                    text=text)
        await message.answer("Жаль. Спасибо что уведомили!")
    else:
        url = baseUrl + '/movie/' + arg
        response = requests.get(url)
        kbrate = InlineKeyboardBuilder()
        kbrate.button(text='Оценить', web_app=WebAppInfo(
            url=("https://bogdansavel.github.io/kk-bot-front/#/rate/" + command.args)))
        kbrate.button(text='Посмотреть оценки', web_app=WebAppInfo(
            url=("https://bogdansavel.github.io/kk-bot-front/#/rates/" + command.args)))
        kbrate.adjust(1,1)
        await bot.send_photo(chat_id=message.chat.id, photo=URLInputFile(url=response.json()["ratePhotoName"]),
                             reply_markup=kbrate.as_markup())


@dp.message(Command("rate"))
async def rate(message: types.Message):
    url = baseUrl + '/event'
    response = requests.get(url)
    movie_id = response.json()["movieId"]

    url = baseUrl + '/movie/' + movie_id
    response = requests.get(url)
    movie_json = response.json()
    await bot.send_photo(chat_id=group_chat_id, message_thread_id=rate_chat_id, parse_mode="HTML",
                         photo=URLInputFile(url=movie_json["ratePhotoName"]),
                         caption="<a href='http://t.me/kk_krakow_bot?start={}'>Оценить фильм</a>".format(movie_json["id"]))


@dp.message(Command("poll"))
async def start(message: types.Message):
    poll_question = "Что смотрим в ближайшее воскресенье?"
    options = []

    if message.from_user.username == "fanboyDan":
        url = baseUrl + '/movie/ready'
        response = requests.get(url)
        if response.ok:
            media_group = MediaGroupBuilder()
            for movie in response.json():
                json_movie = json.loads(movie["kinopoiskData"])
                name = json_movie["name"]
                year = json_movie["year"]
                hours = json_movie["movieLength"] // 60
                minutes = json_movie["movieLength"] % 60
                director = "неизвестно"
                language_id = movie["language"]
                language = ""
                for person in json_movie["persons"]:
                    profession = person["profession"]
                    if profession == "режиссеры":
                        director = person["name"]
                        break

                if language_id is 1:
                    language = "русская озвучка"
                if language_id is 2:
                    language = "русские субтитры"
                if language_id is 4:
                    language = "беларуская агучка"
                if language_id is 3:
                    options.append(f"{name} ({year}, {director}, {hours}ч {minutes}м, русская озвучка)")
                    options.append(f"{name} ({year}, {director}, {hours}ч {minutes}м, русские субтитры)")
                else:
                    options.append(f"{name} ({year}, {director}, {hours}ч {minutes}м, {language})")

                media_group.add_photo(type='photo', media=URLInputFile(url=json_movie["poster"]["url"]))
            await bot.send_media_group(media=media_group.build(), chat_id=group_chat_id)
            await bot.send_poll(question=poll_question,
                                options=options,
                                is_anonymous=False,
                                allows_multiple_answers=True,
                                chat_id=group_chat_id)
        else:
            text = "Что-то пошло не так!"
            await message.answer(text=text, show_alert=True)


@dp.message(Command("areyouready"))
async def start(message: types.Message):
    if message.from_user.username == "fanboyDan":
        url = baseUrl + '/round'
        response = requests.get(url)
        if response.ok:
            text = update_round_message(response)
            message = await bot.send_message(chat_id=group_chat_id, text=text, parse_mode="HTML",reply_markup=ikb.as_markup())
            url = baseUrl + '/telegram-message/round'
            body = {'messageId': message.message_id, 'chatId': message.chat.id, 'roundId': response.json()["id"]}
            requests.post(url, json=body)
        else:
            text = "Что-то пошло не так!"
            await message.answer(text=text, show_alert=True)


def update_round_message(response: Response) -> str:
    user_movie_dict = {}
    for movie in response.json()["movies"]:
        movie_name = "\"" + movie["name"] + "\""
        if movie["member"]["username"] not in user_movie_dict:
            user_movie_dict[movie["member"]["username"]] = movie_name
        else:
            user_movie_dict[movie["member"]["username"]] = (user_movie_dict[movie["member"]["username"]] + ", "
                                                            + movie_name)

    text = "\n*бип-боп* я неодушевленный кусок кода\n\nБогдан мне сказал уточнить у вас, можете ли вы принести свои фильмы в это воскресенье? Нажмити внизу на соответствующую кнопку если можете или не можете.\n\nЕсли вы предложили фильм, а я вас тут не отметил - напишите пожалуйтса здесь или моему создателю в личку. Спасибо!"

    for member in user_movie_dict.keys():
        char = "❔"
        for movie in response.json()["movies"]:
            if movie["member"]["username"] == member and movie["isReady"]:
                char = "✅"
            elif movie["member"]["username"] == member and movie["isReady"] is False:
                char = "❌"
        text = char + " @" + member + " " + user_movie_dict[member] + "\n" + text
    return text


@dp.message(Command("health"))
async def start(message: types.Message):
    await message.answer(text="Alive!")


@dp.message(Command("sendRateMessage"))
async def test(message: types.Message):
    if message.from_user.username == "fanboyDan":
        await bot.send_photo("-1002499953530", photo=FSInputFile(path='TaxiDriverRate.png'), message_thread_id=173, caption="<a href='t.me/kk_krakow_bot?start=bcfbb67f-a005-4c24-92c8-2eb3de65b293""'>Оценить</a>", parse_mode="HTML")


@dp.message(Command("event"))
async def event(message: types.Message, command: CommandObject):
    if message.from_user.username == "fanboyDan":
        url = baseUrl + '/event'
        if command.args is not None:
            url += '/date/' + command.args
        response = requests.get(url)
        event_id = response.json()["id"]
        kb3 = InlineKeyboardBuilder()
        kb3.button(text='Приду', callback_data=CallBackMethod(string='register', event_id=event_id).pack())
        kb3.button(text='Не приду', callback_data=CallBackMethod(string='unregister', event_id=event_id).pack())
        kb3.adjust(2)
        if response.ok:
            message = await bot.send_photo(channel_chat_id, photo=URLInputFile(url=response.json()["posterUrl"]),
                                           caption=response.json()["description"],
                                           parse_mode="HTML",
                                           reply_markup=kb3.as_markup())
            url = baseUrl + '/telegram-message'
            body = {'messageId': message.message_id, 'chatId': message.chat.id, 'eventId':event_id}
            requests.post(url, json=body)

            message = await bot.send_photo("-1002499953530", photo=URLInputFile(url=response.json()["posterUrl"]),
                                           caption=response.json()["description"],
                                           parse_mode="HTML",
                                           reply_markup=kb3.as_markup())
            url = baseUrl + '/telegram-message'
            body = {'messageId': message.message_id, 'chatId': "-1002499953530", 'eventId':event_id}
            requests.post(url, json=body)
        else:
            text = "Что-то пошло не так!"
            await message.answer(text=text, show_alert=True)


@dp.message(Command("киноклуб"))
async def latest(message: types.Message):
    await bot.send_photo(message.chat.id, photo=FSInputFile(path='KKposter.png'), reply_markup=kb.as_markup())


@dp.message(Command("photo"))
async def photo(message: types.Message):
    url = baseUrl + '/member/all/id'
    response = requests.get(url)
    # photo = message.from_user.get_profile_photos()
    if response.ok:
        photos = []
        ids = response.json()
        photos = await bot.get_user_profile_photos(user_id=message.from_user.id, limit=1)
        if photos.photos:
            highest_res_photo = photos.photos[0][-1]
            file_info = await bot.get_file(highest_res_photo.file_id)
            file_path = file_info.file_path

            test = 'test'
    else:
        text = "Что-то пошло не так!"
        await message.answer(text=text, show_alert=True)


@dp.message(Command("stop"))
async def stop_event(message: types.Message, command: CommandObject):
    if message.from_user.username == "fanboyDan":
        url = baseUrl + '/event'
        if command.args is not None:
            url += '/date/' + command.args
        response1 = requests.get(url)

        url = baseUrl + '/event/stop/' + response1.json()["id"]
        response2 = requests.put(url)

        if not response1.ok or not response2.ok:
            text = "Что-то пошло не так!"
            await message.answer(text=text, show_alert=True)

        for message in response1.json()["messages"]:
            await bot.edit_message_caption(message_id=message["messageId"],
                                        chat_id=message["chatId"],
                                        caption=response1.json()["description"])

@dp.message(Command("updatePhoto"))
async def stop_event(message: types.Message, command: CommandObject):
    if message.from_user.username == "fanboyDan":
        url = baseUrl + '/event'
        if command.args is not None:
            url += '/date/' + command.args
        response = requests.get(url)
        event_id = response.json()["id"]
        kb3 = InlineKeyboardBuilder()
        kb3.button(text='Приду', callback_data=CallBackMethod(string='register', event_id=event_id).pack())
        kb3.button(text='Не приду', callback_data=CallBackMethod(string='unregister', event_id=event_id).pack())
        kb3.adjust(2)
        for message in response.json()["messages"]:
            await bot.edit_message_media(message_id=message["messageId"],
                                        chat_id=message["chatId"],
                                        media=InputMediaPhoto(
                                            media=URLInputFile(
                                                url=response.json()["posterUrl"]),
                                                caption=response.json()["description"]),
                                         reply_markup=kb3.as_markup())


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


@dp.message(Command("stopPoll"))
async def stop_poll(message: types.Message):
    if message.from_user.username == "fanboyDan":
        url = baseUrl + '/round'
        response = requests.get(url)
        if response.ok:
            json_response = response.json()
            await bot.stop_poll(chat_id=json_response["pollMessage"]["chatId"], message_id=json_response["pollMessage"]["messageId"])
        else:
            await message.answer("Somthing went wrong")


@router.callback_query(CallBackMethod.filter(F.string == 'ready'))
async def ready(callback_query: CallbackQuery):
    url = baseUrl + '/round/setReady'
    body = {"telegramId": callback_query.from_user.id, "isReady": True}
    response = requests.post(url, json=body)
    if response.ok:
        text = update_round_message(response)
        await bot.edit_message_text(chat_id=response.json()['message']['chatId'],
                                message_id=response.json()['message']['messageId'],
                                text=text, reply_markup=ikb.as_markup())
        await callback_query.answer(text="Отлично! Спасибо что уведомили.", show_alert=True)
    else:
        await callback_query.answer(text="Что-то пошло не так!", show_alert=True)


@router.callback_query(CallBackMethod.filter(F.string == 'notReady'))
async def notReady(callback_query: CallbackQuery):
    url = baseUrl + '/round/setReady'
    body = {"telegramId": callback_query.from_user.id, "isReady": False}
    response = requests.post(url, json=body)
    if response.ok:
        text = update_round_message(response)
        await bot.edit_message_text(chat_id=response.json()['message']['chatId'],
                                message_id=response.json()['message']['messageId'],
                                text=text, reply_markup=ikb.as_markup())
        await callback_query.answer(text="Жаль! Ждем вас в другой раз.", show_alert=True)
    else:
        await callback_query.answer(text="Что-то пошло не так!", show_alert=True)


@router.callback_query(CallBackMethod.filter(F.string == 'register'))
async def register(callback_query: CallbackQuery, callback_data: CallBackMethod):
    url = baseUrl + '/event/' + callback_data.event_id
    event_response = requests.get(url)
    text = "Что-то пошло не так!"
    if event_response.ok:
        url = baseUrl + '/register'
        # photo = callback_query.from_user.get_profile_photos()
        body = {'telegramId': callback_query.from_user.id, 'username': callback_query.from_user.username, 'firstName': callback_query.from_user.first_name, 'eventId': callback_data.event_id}
        response = requests.post(url, json=body)
        kb3 = InlineKeyboardBuilder()
        kb3.button(text='Приду', callback_data=CallBackMethod(string='register', event_id=callback_data.event_id).pack())
        kb3.button(text='Не приду', callback_data=CallBackMethod(string='unregister', event_id=callback_data.event_id).pack())
        kb3.adjust(2)
        if response.ok:
            if response.json()["isAlreadyRegistered"] == True:
                text = "Вы уже зарегестрированы на это мероприятие или такое же в другой день. Чтобы зарегестрироваться сначала отмените предыдущую регистрацию."
            elif response.json()["limitIsExceeded"] == True:
                text = "Извините, мест для регистрации больше нет."
            else:
                text = f"Cпасибо за регистрацию!\n\nЕсли у вас изменятся планы, не забудьте вернуться сюда, и нажать кнопку \"Не приду\"."
                await update_event_message(response, event_response, kb3)
    await callback_query.answer(text=text, show_alert=True)


@router.callback_query(CallBackMethod.filter(F.string == 'unregister'))
async def unregister(callback_query: CallbackQuery, callback_data: CallBackMethod):
    url = baseUrl + '/event/' + callback_data.event_id
    event_response = requests.get(url)
    text = "Что-то пошло не так!"
    if event_response.ok:
        url = baseUrl + '/unregister'
        body = {'telegramId': callback_query.from_user.id, 'username': callback_query.from_user.username, 'firstName': callback_query.from_user.first_name, "eventId": callback_data.event_id}
        response = requests.post(url, json=body)
        kb3 = InlineKeyboardBuilder()
        kb3.button(text='Приду', callback_data=CallBackMethod(string='register', event_id=callback_data.event_id).pack())
        kb3.button(text='Не приду', callback_data=CallBackMethod(string='unregister', event_id=callback_data.event_id).pack())
        kb3.adjust(2)
        if response.ok:
            text = "Регистрация отменена.\nCпасибо что уведомили!"
            await update_event_message(response, event_response, kb3)
        elif response.status_code == 404:
            text = "Cпасибо что уведомили!"
    await callback_query.answer(text=text, show_alert=True)


async def update_event_message(response: Response, event_response: Response, kb1: InlineKeyboardBuilder):
    usernames = list(map(lambda m: generate_name(m), response.json()['members']))
    for message in response.json()["messages"]:
        final_caption = event_response.json()["description"] + f"\n\n{response.json()['membersCount']}/16 зарегистрировано"
        if message["chatId"] == "-1002499953530":
            final_caption = final_caption + "\n" + "\n".join(usernames)
        await bot.edit_message_caption(message_id=message["messageId"],
                                       chat_id=message["chatId"],
                                       caption=final_caption,
                                       reply_markup=kb1.as_markup())


@dp.message(Command("test"))
async def test(message: types.Message):
    url = baseUrl + "/event"
    response = requests.get(url)
    if response.ok:
        usernames = list(map(lambda m: generate_name(m), response.json()['members']))


def generate_name(m):
    name = m["username"] if is_empty_string(m["firstName"]) else m["firstName"]
    name = name if m["username"] is None else "<a href=\'https://t.me/" + m["username"] + "\'>" + name + "</a>"
    return name + " впервые!" if m["freshBlood"] is True else name


def is_empty_string(s):
    return s is None or len(s) == 0


async def main() -> None:
    logging.basicConfig(level=logging.DEBUG)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
