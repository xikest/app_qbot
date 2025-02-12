from pandas import Series
# import FinanceDataReader as fdr
from bot.src_data.FinanceDataReader_mdify import data as fdr
from ._abstract_indicators import Indicators
from ._tools import validate_date, index_to_datetime, Plot
import streamlit as st

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

        # to_pctchange_cum = kwargs.get('to_pctchange_cum')   
        # if to_pctchange_cum:           
        #     ds=ds.pct_change(12).mul(100)              
        return ds
    
