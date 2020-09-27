# Telegram exchange bot
Simple telegram bot which uses data from the https://exchangeratesapi.io 
web service to perform exchange actions. It Returns the latest exchange
rates list. USD is used as base currency and converts currency from the list.
# Commands
1. **/list,  /lst** - returns list of all available rates from:
https://api.exchangeratesapi.io/latest?base=USD. 
An item of the listview has two columns: the currency name and the 
latest exchange rate (with two decimal precision):
Ex.:
    * DKK: 6.74
    * HUF: 299.56

    Once the currency data is loaded from the service, it is saved in the 
    local database. Also, timestamp of the last request is saved. 
    Next time user requests anything the app you should check 
    whether 10 minutes elapsed since the last request:
    * If yes, new data is loaded from web service.
    * If no, previously saved data from the local database is used.
2. **/exchange $10 to CAD or /exchange 10 USD to CAD** - converts currency 
to the second currency with two decimal precision and return.
Ex.: $15.55

3. **/history USD/CAD** - returns an image graph chart which shows the exchange
rate graph of the selected currency for the last 7 days. The currency data for
the last 7 days is not cached.

# Execute instructions
* Use python version: 3.6.9
* Create virtual environment and execute: pip3 install -r requirements.txt
* cd into the project directory
* To run the bot execute: python main.py "<<TELEGRAM-TOKEN>>"
