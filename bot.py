import json
import os

import requests
import telegram
from telegram import Update, Bot
from telegram.ext import Updater, MessageHandler, Filters, CallbackContext, CommandHandler

import logging
import socket
from config import *

from models import *

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)

main_bot = Bot(TOKEN2)


def retrieve_chats():
    response = requests.get(SEND_LIST_URL)
    return list(map(lambda x : x['Telegram ID'], json.loads(response.text)))


def resend(update: Update, context: CallbackContext):
    if USE_SENDLIST:
        chat_ids = retrieve_chats()
    else:
        update.message.reply_text("Тестовый режим включен! Сообщения доставляются только администраторам.")
        chat_ids = ADMINS

    if update.effective_chat.id not in ADMINS:
        update.message.reply_text("Доступ запрещен!")
        logger.log(logging.INFO, f"{update.effective_chat.id} not in {ADMINS}")
        return

    messages = []

    if len(update.message.photo) > 0:
        file = update.message.photo[-1].get_file()

        filename = file.download()

        for chat_id in chat_ids:
            with open(filename, 'rb') as photo:
                try:
                    messages.append(
                        main_bot.send_photo(chat_id, photo, caption=update.message.caption, timeout=120)
                    )
                except telegram.error.TelegramError as e:
                    logger.log(logging.ERROR, e)

        os.remove(filename)
    elif update.message.video is not None:
        file = update.message.video.get_file()

        filename = file.download()

        for chat_id in chat_ids:
            with open(filename, 'rb') as video:
                try:
                    messages.append(
                        main_bot.send_video(chat_id, video, caption=update.message.caption, timeout=120)
                    )
                except telegram.error.TelegramError as e:
                    logger.log(logging.ERROR, e)

        os.remove(filename)
    elif update.message.document is not None:
        file = update.message.document.get_file()

        filename = file.download()

        for chat_id in chat_ids:
            with open(filename, 'rb') as document:
                try:
                    messages.append(
                        main_bot.send_document(chat_id, document, update.message.caption, timeout=120)
                    )
                except telegram.error.TelegramError as e:
                    logger.log(logging.ERROR, e)

        os.remove(filename)
    else:
        for chat_id in chat_ids:
            try:
                messages.append(
                    main_bot.send_message(chat_id, update.message.text)
                )
            except telegram.error.TelegramError as e:
                logger.log(logging.ERROR, e)


    main_message = MainMessage.create(message_id=update.message.message_id, chat_id=update.message.chat_id)
    for message in messages:
        SentMessage.create(main_message=main_message, message_id=message.message_id, chat_id=message.chat_id)

    update.message.reply_text("Сделано!")


def update(update: Update, context: CallbackContext):
    main_message = MainMessage.get(message_id=update.edited_message.message_id, chat_id=update.edited_message.chat_id)
    for message in main_message.sent_messages:
        if update.edited_message.text is not None:
            try:
                main_bot.edit_message_text(chat_id=message.chat_id, message_id=message.message_id, text=update.edited_message.text)
            except telegram.error.TelegramError as e:
                logger.log(logging.ERROR, e)
        elif update.edited_message.caption is not None:
            try:
                main_bot.edit_message_caption(chat_id=message.chat_id, message_id=message.message_id, caption=update.edited_message.caption)
            except telegram.error.TelegramError as e:
                logger.log(logging.ERROR, e)

    update.edited_message.reply_text("Your message was edited!")


def delete(update: Update, context: CallbackContext):
    original_message = update.message.reply_to_message
    main_message = MainMessage.get(message_id=original_message.message_id, chat_id=update.edited_message.chat_id)
    for message in main_message.sent_messages:
        try:
            main_bot.delete_message(chat_id=message.chat_id, message_id=message.message_id)
        except telegram.error.TelegramError as e:
            logger.log(logging.ERROR, e)

    update.message.reply_text("Удалено!")

if __name__ == "__main__":
    updater = Updater(TOKEN, use_context=True)

    dp = updater.dispatcher
    dp.add_handler(MessageHandler((Filters.text | Filters.photo | Filters.video | Filters.document)
                                  & (~Filters.update.edited_message), resend))
    dp.add_handler(MessageHandler(Filters.update.edited_message, update))
    dp.add_handler(CommandHandler("delete", delete))

    if USE_WEBHOOK:
        updater.start_webhook(listen="0.0.0.0",
                              port=PORT,
                              url_path=TOKEN)

        updater.bot.set_webhook(f"https://{APPLICATION_NAME}.herokuapp.com/" + TOKEN)
    else:
        updater.start_polling()
    updater.idle()