import yfinance as yf
import pandas as pd
import FinanceDataReader as fdr
from ._abstract_indicators import Indicators
from ._tools import validate_date, index_to_datetime, Plot

import streamlit as st
class StockIndicators(Indicators):
    def __init__(self):
        super().__init__(indicators_file="stock.json")
    @Plot(mode_binary=False, plot_type='bb_band',secondary_plot="stock_sheet")
    @index_to_datetime
    @validate_date
    def _request(self, key: str = 'AAPL', name: str = None,
                 start: str = None, end: str = None, *args, **kwargs) -> pd.Series:
        ds = yf.Ticker(ticker=key).history(start=start, end=end).Close.round(1)
        cpi = fdr.DataReader(f'FRED:CPIAUCSL', start=start, end=end).iloc[:,0]
        ds.index = pd.to_datetime(ds.index.strftime('%Y-%m-%d'))

        df = pd.DataFrame(index = pd.date_range(start=start, end=end))
        cpi = pd.merge(left=df, right=cpi, left_index=True, right_index=True, how='left').ffill()
        ds = ds / cpi.iloc[:,0]
        ds.name = key
        to_pctchange_cum = kwargs.get('to_pctchange_cum')   
        if to_pctchange_cum:           
            ds=ds.pct_change().add(1).cumprod().sub(1).mul(100)           
        return ds