import requests
import sys
import pandas as pd
import datetime
import argparse
import stockstats
import psycopg2
from sqlalchemy import create_engine

def download_data(from_symbol, to_symbol, exchange, datetime_interval):
    supported_intervals = {'minute', 'hour', 'day'}
    assert datetime_interval in supported_intervals,\
        'datetime_interval should be one of %s' % supported_intervals
    print('Downloading %s trading data for %s %s from %s' %
          (datetime_interval, from_symbol, to_symbol, exchange))
    base_url = 'https://min-api.cryptocompare.com/data/histo'
    url = '%s%s' % (base_url, datetime_interval)
    params = {'fsym': from_symbol, 'tsym': to_symbol,
              'limit': 2000, 'aggregate': 1,
              'e': exchange}
    request = requests.get(url, params=params)
    data = request.json()
    return data

def convert_to_dataframe(data):
    df = pd.io.json.json_normalize(data, ['Data'])
    df['datetime'] = pd.to_datetime(df.time, unit='s')
    df = df[['datetime', 'low', 'high', 'open',
             'close', 'volumefrom', 'volumeto']]
    return df

def filter_empty_datapoints(df):
    indices = df[df.sum(axis=1) == 0].index
    print('Filtering %d empty datapoints' % indices.shape[0])
    df = df.drop(indices)
    return df

def queryPostgres(sql, conn):
    cur = conn.cursor()
    cur.execute(sql)
    dates = cur.fetchall()
    d = []
    for i in dates:
        d.append(i[0])
    return d

def savePostgres(df, table, uname, pwd, host, port, db):
    engine = create_engine('postgresql://{user}:{pwd}@{host}:{port}/{db}'.format(user=uname, pwd=pwd, host=host, port=port, db=db))
    df.to_sql(table, engine, if_exists='append', index=False)

if __name__ == '__main__':
    # Arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("-u", "--username", help="PSQL Username", type=str, required=True)
    parser.add_argument("-p", "--password", help="PSQL Password", type=str, required=True)

    args = parser.parse_args()
    uname = args.username
    pwd = args.password

    # Download data
    # ###### PARAMS ######
    from_symbol, to_symbol = 'BTC', 'USD'
    exchange = 'coinbase'
    period = 'day' # day / hour / minute
    table = 'macd_{from_symbol}_{to_symbol}_{exchange}_{period}'.format(from_symbol=from_symbol.lower(), to_symbol=to_symbol.lower(), exchange=exchange, period=period)
    # ###### ######

    data = download_data(from_symbol, to_symbol, exchange, period)
    df = convert_to_dataframe(data)
    df = filter_empty_datapoints(df)
    current_datetime = datetime.datetime.now().date().isoformat()

    # MACD
    df = stockstats.StockDataFrame.retype(df)
    df['macd'] = df.get('macd')

    # PSQL 
    host = '51.38.38.106'
    db = 'crypto'
    port = 5432

    # Get days
    sql = "SELECT DISTINCT datetime FROM {table};".format(table=table)
    conn = psycopg2.connect(host=host, user=uname, password=pwd, dbname=db, port=port)
    dates = queryPostgres(sql, conn)
    conn.close()

    # New DataFrame with new data
    df = df[~df['datetime'].isin(dates)]
    rows = len(df)
    print("{} new rows to insert in DB.".format(rows))

    # Save DataFrame
    if rows == 0:
        print("Not inserting anything in DF. 0 new rows.")
    elif rows > 0:
        print("Saving {} new rows..".format(rows))
        savePostgres(df, table, uname, pwd, host, port, db)
        print("Saved {} new rows!".format(rows))

    