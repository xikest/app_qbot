from datetime import datetime
import pandas as pd
import numpy as np
import re
import matplotlib.pyplot as plt
from matplotlib.dates import DateFormatter
import matplotlib.dates as mdates
import seaborn as sns
from io import BytesIO
from typing import Generator


class Multpl:
    def __init__(self):
        self.dict_shiller_ratio = {"Shiller PE Ratio by Month":"https://www.multpl.com/shiller-pe/table/by-month",
                                   "S&P 500 Historical Prices by Month": "https://www.multpl.com/s-p-500-historical-prices/table/by-month",
                                   "S&P 500 Earnings by Month": "https://www.multpl.com/s-p-500-earnings/table/by-month",
                                   # "S&P 500 Dividend Yield by Month : %": "https://www.multpl.com/s-p-500-dividend-yield/table/by-month",
                                   # "S&P 500 PE Ratio by Month":"https://www.multpl.com/s-p-500-pe-ratio/table/by-month",
                                   }
        self.dict_treasury = {"10 Year Treasury Rate by Month":"https://www.multpl.com/10-year-treasury-rate/table/by-month",
                              "10 Year Real Interest Rate by Month":"https://www.multpl.com/10-year-real-interest-rate/table/by-month",
                              "2 Year Treasury Rate by Month":"https://www.multpl.com/2-year-treasury-rate/table/by-month",}

        self.dict_us_index = {"US Inflation Rate by Month : %":"https://www.multpl.com/inflation/table/by-month",
                              "Consumer Price Index":"https://www.multpl.com/cpi/table/by-month",
                              "US Real GDP Per Capita by Quarter":"https://www.multpl.com/us-real-gdp-per-capita/table/by-quarter",
                              "US Real GDP Growth Rate by Quarter: %":"https://www.multpl.com/us-real-gdp-growth-rate/table/by-quartere"}


        pass

    def shiller_plots(self, mode_binary:bool=True) -> Generator[bytes | None, None, None]:
        yield from [self._plot(ds=self._data_from_multpl(url), title=title, add_recession=True, mode_binary=mode_binary)
                    for title, url in self.dict_shiller_ratio.items()]

    def treasury_plots(self, mode_binary: bool = True) -> Generator[bytes | None, None, None]:
        ds_year10 = self._data_from_multpl(self.dict_treasury.get("10 Year Treasury Rate by Month"))
        ds_year2 = self._data_from_multpl(self.dict_treasury.get("2 Year Treasury Rate by Month"))
        ds_year_10_2 = (ds_year10 - ds_year2).dropna()

        # Yield the plot for the 10-2 year difference
        yield self._plot(ds=ds_year_10_2, title="10-2 Year Treasury Rate by Month : %", add_recession=True,
                         mode_binary=mode_binary)

        # Yield additional plots for each entry in dict_treasury
        for title, url in self.dict_treasury.items():
            ds = self._data_from_multpl(url)
            yield self._plot(ds=ds, title=title, add_recession=True, mode_binary=mode_binary)

    def us_index_plots(self, mode_binary:bool=True) -> Generator[bytes | None, None, None]:
        yield from [self._plot(ds=self._data_from_multpl(url), title=title, add_recession=True, mode_binary=mode_binary)
                    for title, url in self.dict_us_index.items()]

    def _plot(self, ds: pd.Series, title: str = None, add_recession: bool = False,
              mode_binary: bool = True) -> bytes | None:
        fig, ax = plt.subplots(figsize=(5, 5))  # 크기를 좀 더 크게 조정
        ax.plot(ds.index, ds, label='Data', color='Blue', alpha=0.5, linestyle='-')
        try:
            suffix=title.split(":")[1].strip()
        except:
            suffix = None

        title = title.split(":")[0].strip()
        fig.suptitle(title)

        # 주석 추가
        self._add_annotation(ax, ds, pos='recent', suffix=suffix)
        self._add_annotation(ax, ds, pos='max', suffix=suffix)
        self._add_annotation(ax, ds, pos='min', suffix=suffix)

        # y축 범위 조정
        buffer = (ds.max() - ds.min()) * 0.1  # 데이터 범위의 10%를 버퍼로 추가
        ax.set_ylim(ds.min() - buffer, ds.max() + buffer)

        mid_point = ds.index[int(len(ds.index) / 2)]
        if title == 'Shiller PE Ratio by Month':
            min_pos = 26
            max_pos = 32
            ax.axhline(y=min_pos, color='lightBlue', alpha=1, linestyle='--', linewidth=0.5, label=f'CAPE:{min_pos}')
            ax.text(mid_point, min_pos*1.02, f'CAPE:{min_pos}', verticalalignment='center', horizontalalignment='center',
                    color='gray')  # 배경색 추가, 중앙 정렬로 수정
            ax.axhline(y=max_pos, color='lightBlue', alpha=1, linestyle='--', linewidth=0.5, label=f'CAPE:{max_pos}')
            ax.text(mid_point, max_pos*1.02, f'CAPE:{max_pos}', verticalalignment='center', horizontalalignment='center',
                    color='gray')

        if add_recession:
            df_recession_periods = self._data_recession_periods()
            idx = ds.sort_index().first_valid_index() <= df_recession_periods.start
            for index, row in df_recession_periods[idx].iterrows():
                # print(index, row)
                ax.axvspan(row['start'], row['end'], color="lightgray", alpha=0.3)

        ax.yaxis.set_visible(False)
        ax.grid(True, which='both', linestyle='-', linewidth=0.1, color='gray')
        ax.xaxis.set_major_formatter(DateFormatter('%Y'))
        plt.subplots_adjust(top=0.95)  # 상단 여백 조정
        plt.tight_layout()
        sns.despine()

        if mode_binary:
            buf = BytesIO()
            plt.savefig(buf, format='png', dpi=300)
            plt.close(fig)
            buf.seek(0)
            return buf.getvalue()
        else:
            plt.show()
        return None

    def _add_annotation(self, ax, ds: pd.Series, pos: str = "recent", suffix:str=None):
        if pos == 'min':
            x = ds.idxmin()
        elif pos == 'max':
            x = ds.idxmax()
        else:  # pos == 'recent':
            x = ds.sort_index().last_valid_index()
        y = ds[x]
        if suffix is None:
            text = f"{x.strftime('%y-%m')}, {np.round(y, 1)}"
        else:
            text = f"{x.strftime('%y-%m')}, {np.round(y,1)}{suffix}"
        ax.annotate(text,
                    (mdates.date2num(x), y),
                    textcoords="offset points",
                    xytext=(0, 10), ha='left')
    def _data_from_multpl(self, url: str) -> pd.Series:
        df = pd.read_html(url)[0]
        df.Date = pd.to_datetime(df.Date)
        df = df.set_index('Date')
        df = df["2000" < df.index]  #2000년 이후 데이터만 사용
        df.Value = df.Value.map(lambda x: str(x)).map(lambda text: re.findall(r"-?[0-9]+\.?[0-9]*", text)[0]).map(lambda text: np.float64(text))
        # df.Value = df.Value.map(lambda x: str(x)).map(lambda x: x.replace("%", "")).map(lambda x: np.float64(x))
        ds = df.iloc[:,0]
        return ds

    def _data_recession_periods(self) -> pd.DataFrame:
        url = 'https://en.wikipedia.org/wiki/List_of_recessions_in_the_United_States'
        df_recession = pd.read_html(url)[2]
        df_recession.set_index('Name', inplace=True)
        df_recession["Period Range"] = df_recession["Period Range"].map(lambda x: x.split("–"))
        df_recession = df_recession.assign(
            start=df_recession["Period Range"].map(lambda x: pd.to_datetime(x[0].strip())))
        df_recession = df_recession.assign(
            end=df_recession["Period Range"].map(lambda x: pd.to_datetime(x[1].split("[")[0].strip())))
        df_recession["GDP decline (peak to trough)"] = df_recession["GDP decline (peak to trough)"].map(
            lambda x: np.float64(x.split("%")[0].replace("−", "")))
        df_recession = df_recession.rename(columns={"GDP decline (peak to trough)": "GDP decline (-)"})
        col = ['start', 'end']
        return df_recession[col]