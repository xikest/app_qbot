import pandas as pd
import numpy as np
from io import BytesIO
import matplotlib.pyplot as plt
import seaborn as sns
import FinanceDataReader as fdr
from tools.time.time import Periods
from typing import Generator

class MarketPattern:
  def __init__(self):
      self.dict_market_symbols = {'XLV': 'Health Care', 'XLB': 'Materials', 'XLP': 'Consumer Staples', 'XLF': 'Financial',
                                 'XLI': 'Industrial', 'XLC': 'Communication Services', 'XLK': 'Technology',
                                 'XLU': 'Utilities', 'XLY': 'Consumer Discretionary', 'XLE': 'Energy',
                                 'VNQ': 'Real Estate',
                                 'TLT': 'Treseary',
                                 'GLD': 'Gold'}
      self.dict_periods = {"m":"month", "w":"week"}
      pass

  def sharpe_plot(self, mode_binary:bool=True): # -> Generator[bytes | None, None, None]:
      start, end = Periods.make_period(periods=1)
      df = self._prepare_dataset(symbols=self.dict_market_symbols, start=start, end=end)
      yield from [self._plot(self._calculate_sharpe_ratio(df=df, period=period),
                             mode_binary,
                             title=f'Market pattern(%) by {suffix}')
                  for period, suffix in self.dict_periods.items()]

  def _prepare_dataset(self, symbols, start, end) -> pd.DataFrame:
    dataset = pd.DataFrame({symbol:fdr.DataReader(symbol, start=start, end=end)['Adj Close'] for symbol in symbols})
    dataset = dataset.rename(columns=symbols).sort_index(ascending=False)
    return dataset

  def _calculate_sharpe_ratio(self, df:pd.DataFrame, period:str) -> pd.DataFrame:
      df = (df.pct_change(1).resample(period))
      sharpe_ratio = (df.mean() / df.std()).apply(lambda sharpe: np.round(sharpe,2))
      sharpe_ratio = sharpe_ratio.dropna()
      sharpe_ratio = sharpe_ratio.sort_index(ascending=True)
      return sharpe_ratio

  def _plot(self, df: pd.DataFrame, mode_binary: bool = True, title: str=None): # -> bytes | None:
      plt.figure(figsize=(5, 10))  # Size is given in inches in Matplotlib
      period = title.split("by")[1].strip().lower() # 추출
      if period == 'week':
          annot_data=False
          df.index = df.index.map(lambda idx: idx.strftime('%W (%y-%m)'))
          df = df.apply(lambda sharpe: np.where(sharpe > 0, 1, np.where(sharpe < 0, -1, 0)))
      else: #period is 'm':
          annot_data = (df*100).astype(int)
          df.index = df.index.map(lambda idx: idx.strftime('%y-%m'))
      max=df.max().max()*0.8 # 히트맵 스코프 80%
      ax = sns.heatmap(df, cmap="cividis", vmax=max, vmin=-max, cbar=False, annot=annot_data, fmt="")
      ax.set_title(title)
      ax.set_xticklabels(ax.get_xticklabels(), rotation=90)
      ax.set_yticklabels(ax.get_yticklabels(), rotation=0)
      ax.set_ylabel('')

      plt.tight_layout()
      if mode_binary:
          buf = BytesIO()
          plt.savefig(buf, format='png', dpi=300)  # Specify dpi for higher resolution
          plt.close()  # Correctly closes the entire figure
          buf.seek(0)
          return buf.getvalue()
      else:
          plt.show()
      return None

