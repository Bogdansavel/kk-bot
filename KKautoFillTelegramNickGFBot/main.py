import telebot
import requests
import os
from telebot import types
from fastapi import FastAPI
from aiogram import types, Dispatcher, Bot

app = FastAPI()
WEBHOOK_PATH = f"/bot/{os.environ['TELEGRAM_BOT_TOKEN']}"
WEBHOOK_URL = f"{os.environ['SERVER_URL']}{WEBHOOK_PATH}"
bot = telebot.TeleBot('7144526471:AAG2XsY2tw9lJUVbx_x4z2Rhssiuk6IAaCg')
dp = Dispatcher(bot)
last_message_id = 0


@app.on_event("startup")
async def on_startup():
    webhook_info = await bot.get_webhook_info()
    if webhook_info.url != WEBHOOK_URL:
        await bot.set_webhook(url=WEBHOOK_URL)


@app.post(WEBHOOK_PATH)
async def bot_webhook(update: dict):
    telegram_update = types.Update(**update)
    Bot.seC


@bot.message_handler(commands=['margulis'])
def main(message):
    caption = "КиноКлуб <a href='https://t.me/abf_by_pl'>АБФ</a> в Кракове!\n\nСмотрим, обсуждаем, рассуждаем и делимся своими впечатлениями о фильме \"Боль и слава\". В кругу людей, любящих кино.\n\nВоскресенье.\n25 августа. 17:00.\nКраков, Św. Krzyża 11.\n\nОзвучка: русская\n\n🚨Внимание! \nТак как АБФ на каникулах до 15 сентября, просьба приносить свои продукты (печенье, фрукты, орехи и тому подобное)!\n\nРегистрация по кнопке снизу.\n<a href='https://forms.gle/1afmadKxVvhBxua4A'>Если кнопка не работает</a>"
    image = open(r'KKposter.png', 'rb')
    markup = types.InlineKeyboardMarkup()
    registrate_btn = types.InlineKeyboardButton("Зарегистрироваться", login_url=types.LoginUrl(
        url="https://kk-backend-production.up.railway.app/main"))
    markup.row(registrate_btn)
    cancel_btn = types.InlineKeyboardButton("❌ Отменить ", callback_data="cancel")
    revert_btn = types.InlineKeyboardButton("🔃 Вернуть", callback_data="revert")
    # markup.row(cancel_btn, revert_btn)
    global last_message_id
    # last_message_id = bot.send_photo("-1001781270027", photo=image, caption=caption, reply_markup=markup, parse_mode='HTML').message_id
    # bot.send_photo("-1001747954263", photo=image, caption=caption, reply_markup=markup, parse_mode='HTML')
    bot.send_photo("@cinemaclubabf", photo=image, caption=caption, reply_markup=markup, parse_mode='HTML')


def extract_arg(arg):
    return arg.split()[1:]


@bot.message_handler(commands=['valarmargulis'])
def main(message):
    number = extract_arg(message.text)
    caption = "КиноКлуб <a href='https://www.instagram.com/abf_in_poland/'>АБФ</a> в Кракове!\n\nСмотрим, обсуждаем, рассуждаем и делимся своими впечатлениями о фильме \"Артист\". В кругу людей, любящих кино.\n\nВоскресенье.\n2 июня. 17:00.\nКраков, Św. Krzyża 11.\n\nРегистрация по кнопке снизу.\n<a href='https://forms.gle/1afmadKxVvhBxua4A'>Если кнопка не работает</a>\n\n " + number[0]
    markup = types.InlineKeyboardMarkup()
    registrate_btn = types.InlineKeyboardButton("Зарегистрироваться", login_url=types.LoginUrl(
        url="https://kk-backend-vzw2bewdaa-ew.a.run.app/main"))
    markup.row(registrate_btn)
    cancel_btn = types.InlineKeyboardButton("❌ Отменить ", callback_data="cancel")
    revert_btn = types.InlineKeyboardButton("🔃 Вернуть", callback_data="revert")
    markup.row(cancel_btn, revert_btn)
    bot.edit_message_caption(chat_id="-1001781270027", message_id=last_message_id, caption=caption, reply_markup=markup, parse_mode='HTML')


@bot.callback_query_handler(func=lambda callback: True)
def callback_message(callback):
    if callback.data == "cancel":
        url = "https://kk-backend-vzw2bewdaa-ew.a.run.app/cancel"
        body = {"username": "@" + callback.from_user.username}
        response = requests.post(url, json=body)
        response_message = "Что-то пошло не так!"
        if response.status_code == 200:
            if response.text == "true":
                response_message = "Регистрация отменена! Спасибо что уведомили нас."
            elif response.text == "false":
                response_message = "Вы не зарегестрировались или зарегестрировались не указав свой никнейм в телеграмме."
        bot.answer_callback_query(callback.id, text=response_message, show_alert=True)
    if callback.data == "revert":
        url = "https://kk-backend-vzw2bewdaa-ew.a.run.app/revert"
        body = {"username": "@" + callback.from_user.username}
        response = requests.post(url, json=body)
        response_message = "Что-то пошло не так!"
        if response.status_code == 200:
            if response.text == "true":
                response_message = "Регистрация восстановлена! До встречи на кружке!"
            elif response.text == "false":
                response_message = "Вы не зарегестрировались или зарегестрировались не указав свой никнейм в телеграмме."
        bot.answer_callback_query(callback.id, text=response_message, show_alert=True)


# @bot.callback_query_handler(func=lambda callback: True)
# def callback_to_link(callback):
#    if callback.data == "to_link":
#        bot.answer_callback_query(callback.id, "https://docs.google.com/forms/d/e/1FAIpQLSc1JLQ1Oxcgy7730NoAsJrUI5JhjgXTSUOKnm2bUE-cH6Nm1Q/viewform?usp=pp_url&entry.518733161=@" + callback.from_user.username, True)


bot.polling(none_stop=True)
