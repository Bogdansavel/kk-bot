import telebot
from telebot import types

bot = telebot.TeleBot('7144526471:AAG2XsY2tw9lJUVbx_x4z2Rhssiuk6IAaCg')


@bot.message_handler(commands=['margulis'])
def main(message):
    caption = "КиноКлуб <a href='https://www.instagram.com/abf_in_poland/'>АБФ</a> в Кракове!\n\nСмотрим, обсуждаем, рассуждаем и делимся своими впечатлениями о фильме \"Ворон\". В кругу людей, любящих кино.\n\nВоскресенье.\n31 марта. 17:00.\nКраков, Św. Krzyża 11.\n\nРегистрация по кнопке снизу.\n<a href='https://docs.google.com/forms/d/e/1FAIpQLSc1JLQ1Oxcgy7730NoAsJrUI5JhjgXTSUOKnm2bUE-cH6Nm1Q/viewform'>Если кнопка не работает</a>"
    image = open(r'KKposter.png', 'rb')
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("Регистрация", login_url=types.LoginUrl(url="https://kk-backend-vzw2bewdaa-ew.a.run.app/main")))
    bot.send_photo("-1001747954263", photo=image, caption=caption, reply_markup=markup, parse_mode='HTML')


#@bot.callback_query_handler(func=lambda callback: True)
#def callback_to_link(callback):
#    if callback.data == "to_link":
#        bot.answer_callback_query(callback.id, "https://docs.google.com/forms/d/e/1FAIpQLSc1JLQ1Oxcgy7730NoAsJrUI5JhjgXTSUOKnm2bUE-cH6Nm1Q/viewform?usp=pp_url&entry.518733161=@" + callback.from_user.username, True)


bot.polling(none_stop=True)
