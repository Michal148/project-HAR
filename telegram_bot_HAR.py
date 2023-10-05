import logging

from telegram import Update

from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext

# Ustaw poziom logowania

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# Tworzenie updatera z tokenem bota

updater = Updater(token="private token from telegram", use_context=True)

dispatcher = updater.dispatcher

# Zmienna globalna na przechowywanie ostatniej wprowadzonej cyfry

last_digit = None

# Obsługa komendy /start


def start(update: Update, context: CallbackContext) -> None:
    update.message.reply_text('Cześć! Wprowadzaj cyfry, a ja będę śledzić ostatnią wprowadzoną.')


# Obsługa wiadomości tekstowych

def handle_text(update: Update, context: CallbackContext) -> None:
    global last_digit

    text = update.message.text

    try:

        digit = int(text)

        if last_digit is None or digit != last_digit:
            last_digit = digit

            update.message.reply_text(f'Ostatni wynik to: {digit}')

    except ValueError:

        pass


# Dodaj obsługę komendy /start

start_handler = CommandHandler('start', start)

dispatcher.add_handler(start_handler)

# Dodaj obsługę wiadomości tekstowych

text_handler = MessageHandler(Filters.text & ~Filters.command, handle_text)

dispatcher.add_handler(text_handler)

# Rozpocznij nasłuchiwanie na aktualizacje

updater.start_polling()

updater.idle()