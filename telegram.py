import telebot
from telebot import types
from telebot import formatting

import config
import database
import server
import crypto_price
import paypal

index = int()
results = []

bot = telebot.TeleBot(config.TELEGRAM_API)
server.main()


@bot.message_handler(commands=["start"])
def start(message):
    user_id = message.chat.id
    markup = types.InlineKeyboardMarkup(row_width=2)
    database.user_wallet(user_id, server.request(user_id))

    accounts = types.InlineKeyboardButton("Accounts", callback_data="accounts")
    balance = types.InlineKeyboardButton("Balance", callback_data="balance")

    markup.add(accounts, balance)

    bot.send_message(message.chat.id, config.WELCOME_MESSAGE, reply_markup=markup)


@bot.message_handler(commands=["balance"])
def check_balance(message):
    markup = types.InlineKeyboardMarkup(row_width=2)
    user_id = message.chat.id
    balance = database.find_users_balance(user_id)
    balance = str(balance)
    balance = balance.replace(".", "\.")
    back = types.InlineKeyboardButton("Back", callback_data="back_main")
    markup.add(back)
    bot.send_message(
        message.chat.id,
        f"Your current balance is: {balance}$\nLTC Address for top\-up: ```{server.request(user_id)}```",
        parse_mode="MarkdownV2",
        reply_markup=markup,
    )


@bot.message_handler(commands=["paypal"])
def paypal_receive(message):
    bot.send_message(message.chat.id, f"This method is currently not working.")
    # paypal10 = types.InlineKeyboardButton("10$", callback_data="paypal10")
    # paypal25 = types.InlineKeyboardButton("25$", callback_data="paypal25")
    # paypal50 = types.InlineKeyboardButton("50$", callback_data="paypal50")
    # markup = types.InlineKeyboardMarkup(row_width=2)

    # markup.add(paypal10, paypal25, paypal50)
    # bot.send_message(message.chat.id, f"Select top-up amount: ", reply_markup=markup)


@bot.callback_query_handler(func=lambda call: True)
def account_selection(callback):
    user_id = callback.message.chat.id
    data = database.get_accounts()
    markup = types.InlineKeyboardMarkup(row_width=2)

    back = types.InlineKeyboardButton("Back", callback_data="back_main")
    back_accounts = types.InlineKeyboardButton("Back", callback_data="back_accounts")
    check_payment = types.InlineKeyboardButton(
        "Check payment", callback_data="check_payment"
    )

    message_id = callback.message.message_id

    if callback.data == "accounts":
        for account in range(len(data)):
            select_account = types.InlineKeyboardButton(
                data[account][0], callback_data=data[account][0]
            )
            markup.add(select_account)
        markup.add(back)

        bot.edit_message_text(
            config.purchase_message,
            callback.message.chat.id,
            message_id,
            reply_markup=markup,
        )

    for i in range(len(data)):
        markup_photo = types.InlineKeyboardMarkup(row_width=2)
        markup_photo.add(back_accounts)
        buy_account = types.InlineKeyboardButton("Buy", callback_data=data[i][2])
        markup_photo.add(buy_account)
        if callback.data == data[i][0]:
            bot.send_photo(
                callback.message.chat.id,
                data[i][2],
                f"{data[i][5]}\nPrice: {data[i][1]}$\nLTC: {int(data[i][1])/crypto_price.get_price()+0.002}",
                reply_markup=markup_photo,
            )
        if callback.data == data[i][2]:
            if float(database.find_users_balance(user_id)) >= float(data[i][1]):
                bot.send_message(
                    callback.message.chat.id,
                    f"SUCCESS✅\nlogin = {data[i][3]}\npassword = {data[i][4]}",
                )
                database.sub_balance(server.request(user_id), float(data[i][1]))
                print(data[i][2])
                database.delete_bought_item(img=data[i][2])

            else:
                bot.send_message(
                    callback.message.chat.id,
                    f"FAIL: NOT ENOUGH BALANCE",
                )

    if callback.data == "back_main":
        markup = types.InlineKeyboardMarkup(row_width=2)
        accounts = types.InlineKeyboardButton("Accounts", callback_data="accounts")
        balance = types.InlineKeyboardButton("Balance", callback_data="balance")

        markup.add(accounts, balance)
        bot.edit_message_text(
            config.WELCOME_MESSAGE,
            callback.message.chat.id,
            message_id,
            reply_markup=markup,
        )
    if callback.data == "back_accounts":
        markup = types.InlineKeyboardMarkup(row_width=2)
        for account in range(len(data)):
            select_account = types.InlineKeyboardButton(
                data[account][0], callback_data=data[account][0]
            )
            markup.add(select_account)
        markup.add(back)

        bot.send_message(
            callback.message.chat.id,
            config.purchase_message,
            reply_markup=markup,
        )

    if callback.data == "balance":
        markup = types.InlineKeyboardMarkup(row_width=2)
        user_id = callback.message.chat.id
        balance = database.find_users_balance(user_id)
        balance = str(balance)
        balance = balance.replace(".", "\.")
        markup.add(back)
        bot.send_message(
            callback.message.chat.id,
            f"Your current balance is: {balance}$\nLTC Address for top\-up: ```{server.request(user_id)}```\nOr use /paypal for paypal top\-up",
            parse_mode="MarkdownV2",
            reply_markup=markup,
        )

    if callback.data == "paypal10":
        markup = types.InlineKeyboardMarkup(row_width=2)
        paypal_receive_info = paypal.create_invoice(amount=10)
        top_up_link = paypal_receive_info[0]
        order_id = paypal_receive_info[1]
        markup.add(check_payment)
        bot.edit_message_text(
            f"Top up for 10$\nOrder ID: {order_id}\nTop-up link: {top_up_link}",
            callback.message.chat.id,
            message_id,
            reply_markup=markup,
        )
        database.add_payment_paypal(user_id, order_id, amount=10)
    if callback.data == "paypal25":
        paypal_receive_info = paypal.create_invoice(amount=25)
        top_up_link = paypal_receive_info[0]
        order_id = paypal_receive_info[1]
        markup.add(check_payment)
        bot.edit_message_text(
            f"Top up for 25$\nOrder ID: {order_id}\nTop-up link: {top_up_link}",
            callback.message.chat.id,
            message_id,
            reply_markup=markup,
        )
        database.add_payment_paypal(user_id, order_id, amount=25)
    if callback.data == "paypal50":
        paypal_receive_info = paypal.create_invoice(amount=50)
        top_up_link = paypal_receive_info[0]
        order_id = paypal_receive_info[1]
        markup.add(check_payment)
        bot.edit_message_text(
            f"Top up for 50$\nOrder ID: {order_id}\nTop-up link: {top_up_link}",
            callback.message.chat.id,
            message_id,
            reply_markup=markup,
        )
        database.add_payment_paypal(user_id, order_id, amount=50)

    if callback.data == "check_payment":
        user_id = callback.message.chat.id
        bot.send_message(
            callback.message.chat.id,
            paypal.check_paypal_payment(
                user_id,
                database.select_latest_attempt(user_id),
                database.select_latest_attempt_amount(
                    database.select_latest_attempt(user_id)
                ),
            ),
        )


bot.polling(non_stop=True)
