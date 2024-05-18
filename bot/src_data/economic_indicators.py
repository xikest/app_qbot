from pandas import Series
from fredapi import Fred
import os
from ._abstract_indicators import Indicators
from ._tools import validate_date, index_to_datetime, Plot


class EconomicIndicators(Indicators):

    def __init__(self, api_key: str = None):
        super().__init__(indicators_file="economic.json")
        if api_key is None:
            self.api_key = os.getenv("fred_api_key")

    @Plot(mode_binary=True, plot_type='line', secondary_plot='pct_change')
    @index_to_datetime
    @validate_date
    def _request(self, key: str = 'CPIAUCSL', name: str = None,
                 start: str = None, end: str = None, *args, **kwargs) -> Series:
        ds = Fred(api_key=self.api_key).get_series(key, observation_start=start, observation_end=end)
        ds.name = name
        return ds
