import logging
import exchange
import storage
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from datetime import datetime, timedelta
import traceback
import sys
import os
import seaborn as sns
import pandas as pd
sns.set()

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)

error_message = 'Your request could not be processed, try /help command for more information'


def help_command(update, context):
    """Send a message when the command /help is issued."""
    help_text = "Привет Алла!" \
                "/help - returns commands description\n" \
                "/list, /lst - returns list of all available rates\n" \
                "/exchange - converts currency to the second currency (e.g. /exchange $10 to CAD or " \
                "/exchange 10 USD to CAD)\n" \
                "/history - returns an image graph of the exchange rate for the last 7 day (e.g. /history USD/CAD)"
    update.message.reply_text(help_text)


def no_command(update, context):
    """No command specified"""
    update.message.reply_text('Error, no command was recognized, use /help command to see options')


def get_and_update_rates(currency_name):
    old_rates, update_time = storage.get_exchange_rates()
    if update_time is not None and (datetime.now() - update_time).total_seconds()/60 < 10:
        rates = old_rates
        is_updated = False
    else:
        rates = exchange.get_exchange_rates(currency_name)
        storage.save_exchange_rates(rates)
        is_updated = True

    return rates, is_updated


def list_rates_command(update, context):
    """List exchange rated"""

    # noinspection PyBroadException
    try:
        rates, is_updated = get_and_update_rates('USD')
        print(f'list_rates_command() using new rates: {is_updated}')
        formatted = '\n'.join(['{}: {:.2f}'.format(name, value) for name, value in rates])
        update.message.reply_text(formatted)

    except Exception as e:
        exc_info = sys.exc_info()
        traceback.print_exception(*exc_info)

        update.message.reply_text(error_message)


def exchange_command(update, context):
    """Exchange input currency, currently works and adapted for $"""

    format_detected = False
    to_coin_name, from_coin_value = None, None

    print("exchange()", context.args)
    rates, is_updated = get_and_update_rates('USD')
    print(f'exchange_command() using new rates: {is_updated}')
    print('rates:', rates)
    rates = dict(rates)

    # noinspection PyBroadException
    try:
        # First case: /exchange $10 to CAD
        if len(context.args) == 3:
            from_coin_value = context.args[0]
            action = context.args[1]
            to_coin_name = context.args[2]

            # check format
            if from_coin_value[0] == '$' and from_coin_value[1:].isdigit() and action == 'to' and to_coin_name.isalpha():
                from_coin_value = float(from_coin_value[1:])
                format_detected = True

        # Second case: /exchange 10 USD to CAD
        elif len(context.args) == 4:
            from_coin_value = context.args[0]
            from_coin_name = context.args[1]
            action = context.args[2]
            to_coin_name = context.args[3]

            # check format
            if from_coin_value.isdigit() and from_coin_name == 'USD' and action == 'to' and to_coin_name.isalpha():
                from_coin_value = float(from_coin_value)
                format_detected = True

        # Convert currencies
        if format_detected:
            if to_coin_name in rates:
                result = rates[to_coin_name] * from_coin_value
                formatted = '{:.2f}{}'.format(result, to_coin_name)
            else:
                formatted = f'Currency {to_coin_name} is not supported'
        else:
            formatted = error_message

        update.message.reply_text(formatted)

    except Exception as e:
        exc_info = sys.exc_info()
        traceback.print_exception(*exc_info)

        update.message.reply_text(error_message)


def create_history_figure(path, data, from_coin, to_coin):
    data = pd.DataFrame(data, columns=['date', 'currency'])

    # Draw figure
    ax = sns.lineplot(x="date", y="currency", data=data)
    ax.set_title(f'Currency history between {from_coin} and {to_coin}')
    ax.set(xlabel="Dates", ylabel="Currency value")
    ax.get_figure().autofmt_xdate()

    # Save figure
    ax.get_figure().savefig(path)
    ax.get_figure().clf()


# Format: /history USD/CAD
def history_command(update, context):
    """Last 7 days"""

    # noinspection PyBroadException
    try:
        if len(context.args) == 1:
            inputs = context.args[0].split('/')
            from_coin = inputs[0]
            to_coin = inputs[1]

            seven_days = timedelta(7)
            now = datetime.now()
            from_ = now - seven_days

            data = exchange.get_history_exchange_rates(from_coin, to_coin, from_, now)
            if len(data) > 0:
                path = f'fig_{str(datetime.now())}.png'
                create_history_figure(path, data, from_coin, to_coin)
                update.message.reply_photo(photo=open(path, 'rb'))
                os.remove(path)
            else:
                update.message.reply_text('No exchange rate data is available for the selected currency')

    except Exception as e:
        exc_info = sys.exc_info()
        traceback.print_exception(*exc_info)

        update.message.reply_text(error_message)


def run_bot(token):
    storage.init_db()

    """Start the bot."""
    # Create the Updater and pass it your bot's token.
    # Make sure to set use_context=True to use the new context based callbacks
    # Post version 12 this will no longer be necessary
    updater = Updater(token, use_context=True)

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    # on different commands - answer in Telegram
    dp.add_handler(CommandHandler('help', help_command))
    dp.add_handler(CommandHandler(['list', 'lst'], list_rates_command))
    dp.add_handler(CommandHandler('exchange', exchange_command))
    dp.add_handler(CommandHandler('history', history_command))

    # wrong input
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, no_command))

    # Start the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()
