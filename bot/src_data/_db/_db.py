import pandas as pd
from sqlalchemy import create_engine
import streamlit as st

def get_close_prices_from_db(ticker, start, end):
    engine = create_engine('sqlite:///bot/src_data/_db/q_bot_prices.db')  # SQLite 데이터베이스 생성
    query = f"SELECT * FROM close_prices WHERE ticker = '{ticker}'"
    df_close = pd.read_sql(query, con=engine)
    ds = df_close.set_index('date').loc[start:end,'close']
    ds.name = ticker
    ds.index = pd.to_datetime(ds.index)
    return ds




def get_dividends_from_db(ticker):
    engine = create_engine('sqlite:///q_bot_dividend.db')  # SQLite 데이터베이스 생성
    query = f"SELECT * FROM dividends WHERE ticker = '{ticker}'"
    df_dividends = pd.read_sql(query, con=engine)
    ds = df_dividends.set_index('date')['dividend']
    ds.name = ticker
    return ds
