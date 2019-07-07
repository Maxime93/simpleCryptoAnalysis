import requests
import pandas as pd
import datetime
import argparse
import stockstats
from sqlalchemy import create_engine

def get_filename(from_symbol, to_symbol, exchange, datetime_interval, download_date):
    return '%s_%s_%s_%s_%s.csv' % (from_symbol, to_symbol, exchange, datetime_interval, download_date)

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

def savePostgres(uname, pwd, host, port, db):
    engine = create_engine('postgresql://{user}:{pwd}@{host}:{port}/{db}'.format(user=uname, pwd=pwd, host=host, port=port, db=db))
    df.to_sql('macd', engine, if_exists='append', index=False)

if __name__ == '__main__':
    # Arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("-u", "--username", help="PSQL Username", type=str, required=True)
    parser.add_argument("-p", "--password", help="PSQL Password", type=str, required=True)

    args = parser.parse_args()
    uname = args.username)
    pwd = args.password

    # Download data
    data = download_data('BTC', 'USD', 'coinbase', 'day')
    df = convert_to_dataframe(data)
    df = filter_empty_datapoints(df)
    current_datetime = datetime.datetime.now().date().isoformat()
    filename = get_filename('BTC', 'USD', 'coinbase', 'day', current_datetime)
    # print('Saving data to %s' % filename)
    # df.to_csv("data/{}".format(filename), index=False)

    # MACD
    df = stockstats.StockDataFrame.retype(df)
    df['macd'] = df.get('macd')
    print(df)

    # Save DataFrame
    host = '51.38.38.106'
    db = 'crypto'
    port = 5432
    savePostgres(uname, pwd, host, port, db)

    