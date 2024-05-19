from pandas import Series
from ._abstract_indicators import Indicators
from ._tools import validate_date, index_to_datetime, Plot
import pandas as pd
import numpy as np
import re


class MultplIndicators(Indicators):
    def __init__(self):
        super().__init__(indicators_file="multpl.json")

    @Plot(mode_binary=True, plot_type="line", draw_horiz={"Shiller PE Ratio by Month": "CAPE:26, CAPE:32"})
    @index_to_datetime
    @validate_date
    def _request(self, url: str = "https://www.multpl.com/shiller-pe/table/by-month", name: str = None,
                 start: str = "2020-01-01", end: str = None, *args, **kwargs) -> Series:
        df = pd.read_html(url)[0]
        df['Date'] = pd.to_datetime(df['Date'], format='%b %d, %Y')
        df = df.set_index('Date')
        df = df[start < df.index]  # start 이후 데이터만 사용
        df["Value"] = df["Value"].map(lambda x: str(x)).map(lambda text: re.findall(r"-?[0-9]+\.?[0-9]*", text)[0]).map(
            lambda text: np.float64(text))
        ds = df.iloc[:, 0].round(1)
        ds.name = name
        return ds

