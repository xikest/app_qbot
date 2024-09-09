from pandas import Series
import yfinance as yf
from ._abstract_indicators import Indicators
from ._tools import validate_date, index_to_datetime, Plot


class CommodityIndicators(Indicators):
    def __init__(self):
        super().__init__(indicators_file="commodity.json")

    @Plot(mode_binary=False, plot_type='bb_band')
    @index_to_datetime
    @validate_date
    def _request(self, key: str = 'GC=F', name: str = None,
                 start: str = None, end: str = None, *args, **kwargs) -> Series:
        ds = yf.Ticker(key).history(start=start, end=end).Close.round(1)
        ds.name = name
        return ds