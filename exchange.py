import requests


def get_exchange_rates(base_currency):
    result = requests.get(f'https://api.exchangeratesapi.io/latest?base={base_currency}')
    return list(result.json()['rates'].items())


def get_history_exchange_rates(base_currency, to_currency, from_date, to_date):
    from_date = from_date.strftime("%Y-%m-%d")
    to_date = to_date.strftime("%Y-%m-%d")

    result = requests.get(f'https://api.exchangeratesapi.io/history?start_at={from_date}&end_at={to_date}&base='
                          f'{base_currency}&symbols={to_currency}')

    return sorted([(date, v[to_currency]) for date, v in result.json()['rates'].items()], key=lambda v: v[0])
