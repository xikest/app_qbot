from pandas import Series
import FinanceDataReader as fdr
from ._abstract_indicators import Indicators
from ._tools import validate_date, index_to_datetime, Plot

class EconomicIndicators(Indicators):

    def __init__(self):
        super().__init__(indicators_file="economic.json")

    @Plot(mode_binary=False, plot_type='line')
    @index_to_datetime
    @validate_date
    def _request(self, key: str = 'CPIAUCSL', name: str = None,
                 start: str = None, end: str = None, *args, **kwargs) -> Series:
        ds = fdr.DataReader(f'FRED:{key}', start=start, end=end).iloc[:,0]
        ds.name = name
        return ds
