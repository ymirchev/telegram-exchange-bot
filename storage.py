import sqlite3
from datetime import datetime
import pickle


# Connect to database
_conn = sqlite3.connect('telegram.db', detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES,
                        check_same_thread=False)


def init_db():
    # Create table
    _conn.cursor().execute('''CREATE TABLE IF NOT EXISTS exchange_rates(id int, update_date timestamp, rates binary,
    PRIMARY KEY (id))''')

    # Save the changes
    _conn.commit()


def save_exchange_rates(exchange_rates):
    # Insert a row of data
    values = (0, datetime.now(), pickle.dumps(exchange_rates))
    _conn.cursor().execute("REPLACE INTO exchange_rates VALUES(?, ?, ?)", values)

    # Save the changes
    _conn.commit()


def get_exchange_rates():
    update_time, rates = None, None

    # Retrieve a row
    result = _conn.cursor().execute('SELECT * FROM exchange_rates')
    result = result.fetchone()
    if result is not None:
        update_time, rates = result[1], pickle.loads(result[2])

    return rates, update_time
