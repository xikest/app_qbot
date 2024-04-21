import numpy as np
import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from io import BytesIO
from typing import Generator

class StockFlw():
    def __init__(self):
        self._stock_data= None
        pass

    def cash_plot(self, symbol, mode_binary:bool=True, period='quarterly'): # -> Generator[bytes | None, None, None]:
        try:
            self._stock_data = yf.Ticker(symbol)
        except:
            yield None

        dict_cashflow_q = {"Cash Flow from Operations(%) ": self._ratio_income_div_operating("quarterly"),
                         "Cash Flow from Assets(%)": self._ratio_income_div_assetes("quarterly")}
        dict_cashflow_expectation = {"Cash Flow from Operations(%)": self._ratio_income_div_operating("yearly").mean(),
                                     "Cash Flow from Assets(%)": self._ratio_income_div_assetes("yearly").mean()}

        yield from [self._plot(ds=ds, expectation=expectation.round(1), suptitle=title, mode_binary=mode_binary) for title, ds, expectation in zip(dict_cashflow_q.keys(), dict_cashflow_q.values(), dict_cashflow_expectation.values())]

    def _plot(self, ds: pd.Series, expectation:float, suptitle: str = None, mode_binary: bool = True): # -> bytes | None:
        ds = ds.sort_index()
        ds.index = ds.index.map(lambda date: date.strftime('%y-%m'))
        fig, ax = plt.subplots(figsize=(5, 5))
        bars = ax.bar(ds.index, ds, color='Blue', alpha=0.5)

        # 각 막대 위에 데이터 값 표시
        for bar in bars:
            yval = bar.get_height()
            ax.text(bar.get_x() + bar.get_width() / 2, yval, round(yval, 1), ha='center', va='bottom', color='lightgray')

        ax.axhline(y=expectation, color='gray', alpha=0.8, linestyle='-', linewidth=1)
        ax.text(0, expectation * 1.02, f'Exp:{expectation}', verticalalignment='center', horizontalalignment='center',
                color='black')  # 배경색 추가, 중앙 정렬로 수정

        sub_title=f"{self._stock_data.info['shortName']}\nPE(trailing): {int(self._stock_data.info['trailingPE'])}, PE(forward): {int(self._stock_data.info['forwardPE'])}\nROE: {int(self._stock_data.info['returnOnEquity']*100)}%, Leverage: {int(self._stock_data.info['debtToEquity'])}"
        fig.suptitle(suptitle)
        ax.set_title(sub_title,loc='right', fontsize=8, color='gray')
        ax.yaxis.set_visible(False)
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

    def _ratio_income_div_operating(self, period:str='quarterly') -> pd.Series:
        return pd.Series(
            self._call_from_cashflow('Net Income From Continuing Operations', period) / self._call_from_cashflow('Cash Flow From Continuing Operating Activities', period),
            name='영업 활동으로 발생하는 현금 흐름 (Income/Operating)')*100
    def _ratio_income_div_assetes(self, period='quarterly'):
        return pd.Series(
            self._call_from_cashflow('Net Income From Continuing Operations', period) / self._call_from_balance_sheet('Total Assets', period),
            name='자산 대비 수익 창출 능력 (Income/Assets)')*100
    def _call_from_cashflow(self, key = 'Net Income From Continuing Operations',  period:str= 'quarterly'): # ->pd.DataFrame | None:
        try:
            if period == 'quarterly' :
                return self._stock_data.quarterly_cashflow.loc[key,:]
            elif 'yearly' :
                return self._stock_data.cashflow.loc[key,:]
        except:
            return None
    def _call_from_balance_sheet(self, key='Total Assets', period: str = 'quarterly'): #->pd.DataFrame | None:
        try:
            if period == 'quarterly':
                return self._stock_data.quarterly_balance_sheet.loc[key, :]
            elif 'yearly':
                return self._stock_data.balance_sheet.loc[key, :]
        except:
            return None