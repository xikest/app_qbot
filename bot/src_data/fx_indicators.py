from pandas import Series
from typing import BinaryIO
import yfinance as yf
from ._abstract_indicators import Indicators
from ._tools import validate_date, index_to_datetime, Plot


class FxIndicators(Indicators):
    def __init__(self):
        super().__init__(indicators_file="fx.json")

    @Plot(mode_binary=True, plot_type='line')
    @index_to_datetime
    @validate_date
    def _request(self, key: str = 'USD/KRW', name: str = None,
                 start: str = None, end: str = None, *args, **kwargs) -> Series | BinaryIO:
        ds = yf.Ticker(key).history(start=start, end=end).Close.round(1)
        ds.name = name
        return ds
