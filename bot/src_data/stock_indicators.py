import yfinance as yf
import pandas as pd
from typing import BinaryIO

from ._abstract_indicators import Indicators
from ._tools import validate_date, index_to_datetime, Plot


class StockIndicators(Indicators):
    def __init__(self):
        super().__init__(indicators_file="stock.json")

    @Plot(mode_binary=True, plot_type='bb_band',secondary_plot="stock_sheet")
    @index_to_datetime
    @validate_date
    def _request(self, key: str = 'AAPL', name: str = None,
                 start: str = None, end: str = None, periods=3, *args, **kwargs) -> pd.Series:
        ds = yf.Ticker(ticker=key).history(start=start, end=end).Close.round(1)
        ds.name = key
        return ds



