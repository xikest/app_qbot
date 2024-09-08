import pandas as pd
from datetime import date
from dateutil.relativedelta import relativedelta
import matplotlib.pyplot as plt
from functools import wraps
from typing import Hashable, Tuple, List, Union
from matplotlib.figure import Figure

from pandas import Series
from matplotlib.dates import DateFormatter
import matplotlib.dates as mdates
import seaborn as sns
from io import BytesIO
import numpy as np
import yfinance as yf
from fredapi import Fred
from datetime import timedelta

def validate_date(func):
    @wraps(func)
    def wrapper(self, key: str, *args, **kwargs):
        start = kwargs.get('start')
        end = kwargs.get('end')
        periods = kwargs.get('periods')

        if periods is None:
            periods = 3

        if isinstance(start, str):
            start = pd.to_datetime(start)
        if isinstance(end, str):
            end = pd.to_datetime(end)

        if start is None and end is None:
            end = date.today()
            start = end - relativedelta(years=periods)
        elif start is None:
            start = end - relativedelta(years=periods)
        elif end is None:
            end = date.today()

        start = start.strftime('%Y-%m-%d')
        end = end.strftime('%Y-%m-%d')

        kwargs['start'] = start
        kwargs['end'] = end

        return func(self, key, *args, **kwargs)

    return wrapper


def index_to_datetime(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        data = func(*args, **kwargs)
        if isinstance(data, Series):
            # Ensure the index is datetime type, convert if it's object type
            if pd.api.types.is_object_dtype(data.index.dtype):
                data.index = pd.to_datetime(data.index)
            # ds index to 'YYYY-MM-DD' if it's already datetime
            elif pd.api.types.is_datetime64_any_dtype(data.index.dtype):
                data.index = pd.to_datetime(data.index.strftime('%Y-%m-%d'))
            return data
        else:
            return data

    return wrapper


def retry(func=None, *, try_cnt=2):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            data = None
            for _ in range(try_cnt):
                try:
                    data = func(*args, **kwargs)
                except Exception as e:
                    # print(f"error: {e}")
                    pass
            return data

        return wrapper

    if func is None:
        return decorator
    else:
        return decorator(func)


class Plot:
    def __init__(self, mode_binary: bool = False, plot_type: str = "bb_band", add_recession: bool = True,
                 draw_horiz: dict = None, secondary_plot: str = ""):
        self.mode_binary = mode_binary
        self.draw_horiz = draw_horiz
        self.add_recession = add_recession
        self.secondary_plot = secondary_plot
        self.plot_type = plot_type

    def __call__(self, func):
        @wraps(func)
        def wrapper(*args, **kwargs) -> List[Union[bytes, Figure]]:
            ds = func(*args, **kwargs)
            fig, ax = plt.subplots(figsize=(5, 5))  # 크기를 좀 더 크게 조정

            title = ds.name

            try:
                suffix = title.split(":")[-1].strip()
                title = title.split(":")[0].strip()
            except:
                suffix = None
                
            if title == 'Beveridge Curve':
                fig, ax = _add_beveridge(fig=fig, ax=ax, ds=ds)
                title = f'{title} with {suffix}'
            elif title == 'Hope Curve':
                fig, ax = _add_beveridge(fig=fig, ax=ax, ds=ds, y={'HOUST':'Housing Starts'}, x={'IR14280':'New Orders'})
                title = f'{title} with {suffix}'
                

                
            else:
                if self.plot_type == "line":
                    ax.plot(ds.index, ds, label='Data', color='Blue', alpha=0.5, linestyle='-')
                    ax = _add_annotation(ax, ds, pos='recent', suffix=suffix)
                    ax = _add_annotation(ax, ds, pos='max', suffix=suffix)
                    ax = _add_annotation(ax, ds, pos='min', suffix=suffix)
                    
                elif self.plot_type == "bb_band":
                    upper_band, middle_band, lower_band = bollinger_bands(ds, timeperiod=20, nbdevup=2, nbdevdn=2)
                    ax.plot(upper_band.index, upper_band, label='Upper',
                            color='gray', alpha=0.5, linewidth=0.5, linestyle='-')
                    ax.plot(middle_band.index, middle_band, label='Middle',
                            color='Black', alpha=0.6, linewidth=0.6, linestyle='-')
                    ax.plot(lower_band.index, lower_band, label='Lower',
                            color='gray', alpha=0.5, linewidth=0.5, linestyle='-')
                elif self.plot_type == "ma":
                    _, middle_band, _ = bollinger_bands(ds, timeperiod=20, nbdevup=2, nbdevdn=2)
                    ax.plot(middle_band.index, middle_band, label='Middle', color='Blue',
                            alpha=0.8, linewidth=0.8, linestyle='-')
                # 주석 추가

                if self.draw_horiz is not None:
                    for title_draw, scope in self.draw_horiz.items():
                        if title == title_draw:
                            min_label = scope.split(",")[0].strip()
                            max_label = scope.split(",")[1].strip()
                            ax = _add_horiz_min_max(ax, ds, min_label=min_label, max_label=max_label)

                if self.add_recession:
                    ax = _add_recession_periods(ax, ds)

                if self.secondary_plot == "stock_sheet":
                    fig, ax = _add_stock_sheet(fig, ax, ds)
                elif self.secondary_plot == "pct_change":
                    fig, ax = _add_pct_change(fig, ax, ds)
                

                # y축 범위 조정
                buffer = (ds.max() - ds.min()) * 0.1  # 데이터 범위의 10%를 버퍼로 추가
                ax.set_ylim(ds.min() - buffer, ds.max() + buffer)
                ax.yaxis.set_visible(False)
                ax.grid(True, which='both', linestyle='-', linewidth=0.1, color='dimgray')
                ax.xaxis.set_major_formatter(DateFormatter('%y-%m'))
                ax.xaxis.set_tick_params(rotation=90)
                
            fig.suptitle(title)    
            plt.subplots_adjust(top=0.95)  # 상단 여백 조정
            plt.tight_layout()
            sns.despine()

            if self.mode_binary:
                buf = BytesIO()
                plt.savefig(buf, format='png', dpi=300)
                plt.close(fig)
                buf.seek(0)
                return [buf.getvalue()]
            else:
                plt.show()
                return [fig]

        return wrapper


def bollinger_bands(ds: pd.Series, timeperiod: int = 20, nbdevup: int = 2, nbdevdn: int = 2) -> Tuple[
    pd.Series, pd.Series, pd.Series]:
    middle_band = ds.rolling(window=timeperiod).mean()
    std_dev = ds.rolling(window=timeperiod).std()

    upper_band = middle_band + (nbdevup * std_dev)
    lower_band = middle_band - (nbdevdn * std_dev)

    return upper_band, middle_band, lower_band


def _add_recession_periods(ax: plt.Axes, ds: Series) -> plt.Axes:
    def _data_recession_periods() -> pd.DataFrame:
        url = 'https://en.wikipedia.org/wiki/List_of_recessions_in_the_United_States'
        df_recession = pd.read_html(url)[2]
        df_recession.set_index('Name', inplace=True)
        df_recession["Period Range"] = df_recession["Period Range"].map(lambda x: x.split("–"))
        df_recession = df_recession.assign(
            start=df_recession["Period Range"].map(lambda x: pd.to_datetime(x[0].strip(), format='%B %Y')))
        df_recession = df_recession.assign(
            end=df_recession["Period Range"].map(lambda x: pd.to_datetime(x[1].split("[")[0].strip(), format='%B %Y')))
        df_recession["GDP decline (peak to trough)"] = df_recession["GDP decline (peak to trough)"].map(
            lambda x: np.float64(x.split("%")[0].replace("−", "")))
        df_recession = df_recession.rename(columns={"GDP decline (peak to trough)": "GDP decline (-)"})
        col = ['start', 'end']
        df_recession = df_recession[col]
        return df_recession

    df_recession_periods = _data_recession_periods()
    idx = ds.sort_index().first_valid_index() <= df_recession_periods.start
    for index, row in df_recession_periods[idx].iterrows():
        # print(index, row)
        ax.axvspan(row['start'], row['end'], color="lightgray", alpha=0.3)
    return ax


def _add_annotation(ax: plt.Axes, ds: Series, pos: str = "recent", suffix: str = None, fontsize: int = 5, color='black',
                    alpha=0.3,
                    visible_index: bool = True) -> plt.Axes:
    x: Hashable
    if pos == 'min':
        x = ds.idxmin()
    elif pos == 'max':
        x = ds.idxmax()
    elif pos == 'recent':
        x = ds.sort_index().last_valid_index()
    elif pos == 'first':
        x = ds.sort_index().first_valid_index()
    elif pos == 'middle':
        middle_index = ds.index[int(len(ds) / 2)]
        x = middle_index
    y = ds[x]
    if suffix is None:
        x: pd.Timestamp
        if visible_index:
            text = f"{x.strftime('%y-%m')}, {np.round(y, 1)}"
        else:
            text = f"{np.round(y, 1)}"
    else:
        x: pd.Timestamp
        if visible_index:
            text = f"{np.round(y, 1)}{suffix}, {x.strftime('%y-%m')}"
        else:
            text = f"{np.round(y, 1)}{suffix}"
    ax.annotate(text,
                (mdates.date2num(x), y),
                textcoords="offset points",
                xytext=(0, 5), ha='left', fontsize=fontsize, color=color, alpha=alpha)

    return ax


def _add_horiz_min_max(ax: plt.axes, ds: Series, min_label: str = "CAPE:26", max_label: str = "CAPE:32"):
    min_pos = int(min_label.split(":")[-1])
    max_pos = int(max_label.split(":")[-1])
    mid_point = ds.index[int(len(ds.index) / 2)]
    ax.axhline(y=min_pos, color='lightBlue', alpha=1, linestyle='--', linewidth=0.5, label=f'{min_label}')
    ax.text(mid_point, min_pos * 1.02, f'{min_label}', verticalalignment='center', horizontalalignment='center',
            color='gray')  # 배경색 추가, 중앙 정렬로 수정
    ax.axhline(y=max_pos, color='lightBlue', alpha=1, linestyle='--', linewidth=0.5, label=f'{max_label}')
    ax.text(mid_point, max_pos * 1.02, f'{max_label}', verticalalignment='center', horizontalalignment='center',
            color='gray')
    return ax


def _add_pct_change(fig: plt.Figure, ax: plt.axes, ds: pd.Series) -> Tuple[plt.Figure, plt.Axes]:
    def _draw_pct_change(ax: plt.Axes, ds_pct_change: pd.Series, color='blue',
                         suffix: str = "%") -> plt.Axes:
        ax.fill_between(ds_pct_change.index, ds_pct_change, color=color, alpha=0.1)  # 색을 채우는 부분
        _add_annotation(ax, ds_pct_change, pos="first", suffix=suffix, visible_index=False)
        return ax

    ds_pct_change = ds.pct_change() * 100

    ax2 = ax.twinx()
    ax2 = _draw_pct_change(ax2, ds_pct_change, color='red', suffix="%")

    num = int(len(ds_pct_change) * 0.1)
    top = ds_pct_change.nlargest(num).iloc[-1] * 2
    bottom = ds_pct_change.nsmallest(num).iloc[-1] * 2
    if bottom > 0: bottom = 0
    ax2.set_ylim(bottom=bottom, top=top)
    ax2.yaxis.set_visible(False)
    return fig, ax


def _add_beveridge(fig: plt.Figure, ax: plt.Axes, ds: pd.Series) -> Tuple[plt.Figure, plt.Axes]:

    start = ds.index[0]
    end = ds.index[-1]
    col_name = ds.name.split(':')[-1]
    x_name = 'Unemployment Rate'
    y_name = 'Job Openings Rate'
    api_key = "1afc3162f75a055edf1d1a95529096cf"
    # FRED에서 실업률, 구인율, 10년 금리 데이터 가져오기
    unemployment_rate = Fred(api_key=api_key).get_series('UNRATE', observation_start=start, observation_end=end)
    job_opening_rate = Fred(api_key=api_key).get_series('JTSJOR', observation_start=start, observation_end=end)
    ref_treasury = ds


    data = pd.concat([unemployment_rate, job_opening_rate, ref_treasury], axis=1)
    data.columns = [x_name, y_name, col_name]

    # 결측값 제거
    data = data.ffill().resample('ME').last().dropna()

    # 최근 연간 데이터 필터링
    two_years_ago = (end - timedelta(days=365 * 2)).strftime('%Y-%m-%d')
    recent_data = data.loc[two_years_ago:].copy()  # 복사본 생성

    # 최근 데이터에서 3개월 이동평균 계산
    recent_data[f'{y_name} MA'] = recent_data[y_name].rolling(window=6).mean()
    recent_data[f'{x_name} MA'] = recent_data[x_name].rolling(window=6).mean()

    # 최근 데이터 선택 (마지막 1개의 데이터 포인트)
    latest_data = data.tail(1)

    # 산점도 추가
    scatter = ax.scatter(
        data[x_name],
        data[y_name],
        s=data[col_name] * 50,  # 점의 크기로 10년 금리 사용
        c=data[col_name],  # 색상으로 10년 금리 사용
        cmap='cividis',  # 색상맵 설정
        alpha=0.8,  # 투명도 설정
        edgecolor='none'  # 외곽선 제거
    )

    # 색상 바 추가
    cbar = plt.colorbar(scatter, ax=ax)
    cbar.set_label(col_name)

    # 최근 5년 데이터에 3개월 이동평균 추세선 추가
    ax.plot(
        recent_data[f'{x_name} MA'],
        recent_data[f'{y_name} MA'],
        color='red',
        linewidth=1,
        label='3-Month Moving Average'
    )

    # 최근 데이터 레이블 추가
    ax.scatter(
        latest_data[x_name],
        latest_data[y_name],
        s=latest_data[col_name], 
        edgecolor='red',  # 마커 외곽선 색상 설정
        facecolor='red',  # 마커 안쪽을 비움
        label=f'Latest {col_name}'
    )
    for i, txt in enumerate(latest_data[col_name]):
        ax.annotate(f'{txt:.2f}%', (latest_data[x_name].values[i], latest_data[y_name].values[i]),
                    textcoords="offset points", xytext=(0,10), ha='center')

    # 그래프 레이아웃 업데이트
    ax.set_xlabel("Unemployment Rate (%)", fontsize=10,  color='gray')
    ax.set_ylabel("Job Openings Rate (%)", fontsize=10, color='gray')

    plt.legend(fontsize=8, loc='best', frameon=False, shadow=False, edgecolor='gray')
    return fig, ax


def _add_stock_sheet(fig: plt.Figure, ax: plt.axes, ds: pd.Series) -> Tuple[plt.Figure, plt.Axes]:
    key = str(ds.name)
    cf = CashFlow(symbol=key)

    def _adjust_index(ds1: pd.Series, ds2: pd.Series) -> pd.Series:
        ds1 = ds1.apply(lambda x: np.nan)
        ds1_month = ds1.index.strftime('%Y-%m')

        for date, value in ds2.items():
            year_month = pd.to_datetime(date).strftime('%Y-%m')
            ds1.loc[ds1_month == year_month] = value
        ds1 = ds1.ffill()
        return ds1

    def _draw_cashflow(ax: plt.Axes, ds_cash_flow: pd.Series, ds_exp: pd.Series, color='blue',
                       suffix: str = "% exp") -> plt.Axes:
        ax.fill_between(ds_cash_flow.index, ds_cash_flow, color=color, alpha=0.1)  # 색을 채우는 부분
        ax.plot(ds_exp.index, ds_exp, color=color, alpha=0.1)
        _add_annotation(ax, ds_exp, pos="min", suffix=suffix, visible_index=False, color=color)
        return ax

    def _add_stock_info(fig: plt.Figure, ax: plt.Axes, dict_info: dict) -> Tuple[plt.Figure, plt.Axes]:
        long_name = dict_info.get("long name")
        if long_name is not None:
            fig.suptitle(f"{long_name}\n")
        else:
            fig.suptitle(dict_info.get("symbol"))
        try:
            enterprise_value = int(dict_info.get('enterprise value'))
            market_cap = int(dict_info.get('market cap'))
            if isinstance(enterprise_value, (int, float)):
                if enterprise_value >= 1000000000000:
                    enterprise_value = f"{round(enterprise_value / 1000000000000, 2)}T"
                    market_cap = f"{round(market_cap / 1000000000000, 2)}T"
                elif enterprise_value >= 1000000000:
                    enterprise_value = f"{round(enterprise_value / 1000000000, 2)}B"
                    market_cap = f"{round(market_cap / 1000000000, 2)}B"
                elif enterprise_value >= 1000000:
                    enterprise_value = f"{round(enterprise_value / 1000000, 2)}M"
                    market_cap = f"{round(market_cap / 1000000, 2)}M"
                elif enterprise_value >= 1000:
                    enterprise_value = f"{round(enterprise_value / 1000, 2)}K"
                    market_cap = f"{round(market_cap / 1000, 2)}K"
                else:
                    enterprise_value = f"{round(enterprise_value, 2)}"
                    market_cap = f"{round(market_cap, 2)}"
            else:
                enterprise_value = ""

            ax.set_title(
                f"Trailing PE: {dict_info.get('trailing PE')}, Forward PE: {dict_info.get('forward PE')}\n"
                f"Overall Risk: {int(dict_info.get('overall risk'))}, Short Ratio: {dict_info.get('short ratio')}\n"
                f"Enterprise Value: {enterprise_value}, Market Cap: {market_cap}",
                fontsize=6
            )
        except:
            pass
        return fig, ax

    dict_cashflow_q = {"Cash Flow from Operations(%)": cf.ratio_income_div_operating("quarterly"),
                       "Cash Flow from Assets(%)": cf.ratio_income_div_assetes("quarterly")}
    dict_cashflow_y = {"Cash Flow from Operations(%)": cf.ratio_income_div_operating("yearly"),  # using recent 2year
                       "Cash Flow from Assets(%)": cf.ratio_income_div_assetes("yearly")}
    if all(v is not None for v in dict_cashflow_q.values()) and all(v is not None for v in dict_cashflow_y.values()):
        dict_cashflow_q_adjusted = {k: _adjust_index(ds, v) for k, v in dict_cashflow_q.items()}
        # for k, v in dict_cashflow_q_adjusted.items(): print(pd.DataFrame(v.sort_index(ascending=False)))

        dict_cashflow_y_adjusted = {k: _adjust_index(ds, v.sort_index(ascending=False)[:2]) for k, v in
                                    dict_cashflow_y.items()}  # 최근 2년 데이터만 사용
        # for k, v in dict_cashflow_y.items(): print(pd.DataFrame(v.sort_index(ascending=False)[:2])) #최근 2년 데이터 체크용
        # for k, v in dict_cashflow_y.items(): print(pd.DataFrame(v.sort_index(ascending=False)[:2]))  # 최근 2년 데이터 체크용
        dict_cashflow_expectation = {k: v.apply(lambda x: v.mean()) for k, v in dict_cashflow_y_adjusted.items()}

        ds_cash_flow_operations = dict_cashflow_q_adjusted.get("Cash Flow from Operations(%)")
        ds_expectation_operations = dict_cashflow_expectation.get("Cash Flow from Operations(%)").fillna(0)
        ds_cash_flow_assets = dict_cashflow_q_adjusted.get("Cash Flow from Assets(%)")
        ds_expectation_assets = dict_cashflow_expectation.get("Cash Flow from Assets(%)").fillna(0)
        # print("ds_cash_flow_operations")
        # print(ds_cash_flow_operations)
        # print("ds_expectation_operations")
        # print(ds_expectation_operations)
        # print("ds_cash_flow_assets")
        # print(ds_cash_flow_assets)
        # print("ds_expectation_assets")
        # print(ds_expectation_assets)

        ax2 = ax.twinx()
        ax2 = _draw_cashflow(ax2, ds_cash_flow_operations, ds_expectation_operations, color='red', suffix="% from Operations")
        ax2 = _draw_cashflow(ax2, ds_cash_flow_assets, ds_expectation_assets, color='blue', suffix="% from Assets")

        def bottom_value(*args):
            return min(*args, 0)

        def top_value(*args):
            return max(*args, 100)

        bottom = bottom_value(ds_expectation_assets.min(), ds_expectation_operations.min(),
                              ds_cash_flow_operations.min(), ds_cash_flow_assets.min())
        top = top_value(ds_expectation_assets.max(), ds_expectation_operations.max(),
                        ds_cash_flow_operations.max(), ds_cash_flow_assets.max())

        _add_annotation(ax2, ds_cash_flow_operations, pos='max', suffix='%', color='red', visible_index=False)
        _add_annotation(ax2, ds_cash_flow_operations, pos='min', suffix='%', color='red', visible_index=True)
        ax2.set_ylim(bottom=bottom, top=top * 3)
        ax2.yaxis.set_visible(False)

    fig, ax = _add_stock_info(fig, ax, cf.get_info())
    return fig, ax





class CashFlow:

    def __init__(self, symbol: str):
        self._stock_data = yf.Ticker(symbol)
        self._info: dict = {"symbol": symbol}
        pass

    @retry
    def get_info(self) -> dict:
        try:
            self._info['long name'] = self._stock_data.info.get("longName")
            self._info['overall risk'] = round(float(self._stock_data.info.get("overallRisk")), 1)
            self._info['short ratio'] = round(float(self._stock_data.info.get("shortRatio")), 1)
            self._info['trailing PE'] = round(float(self._stock_data.info.get("trailingPE")), 1)
            self._info['forward PE'] = round(float(self._stock_data.info.get("forwardPE")), 1)
            self._info['enterprise value'] = round(float(self._stock_data.info.get("enterpriseValue")), 1)
            self._info['market cap'] = round(float(self._stock_data.info.get("marketCap")), 1)
        except:
            pass
        return self._info

    @index_to_datetime
    def ratio_income_div_operating(self, period: str = 'quarterly') -> pd.Series or None:
        try:
            net_income = self._net_income_from_cashflow('Net Income From Continuing Operations', period)
            operating_cashflow = self._net_income_from_cashflow('Cash Flow From Continuing Operating Activities',
                                                                period)
            return (net_income / operating_cashflow).rename('영업 활동으로 발생하는 현금 흐름 (Income/Operating)') * 100
        except Exception as e:
            return None

    @index_to_datetime
    def ratio_income_div_assetes(self, period='quarterly') -> pd.Series or None:
        try:
            net_income = self._net_income_from_cashflow('Net Income From Continuing Operations', period)
            total_assets = self._total_assets_from_balance_sheet('Total Assets', period)

            return (net_income / total_assets).rename('자산 대비 수익 창출 능력 (Income/Assets)') * 100
        except Exception as e:
            return None

    @retry
    def _net_income_from_cashflow(self, key='Net Income From Continuing Operations',
                                  period: str = 'quarterly'):  # ->pd.DataFrame | None:

        if period == 'quarterly':
            return self._stock_data.quarterly_cashflow.loc[key, :]
        elif 'yearly':
            return self._stock_data.cashflow.loc[key, :]

    @retry
    def _total_assets_from_balance_sheet(self, key='Total Assets', period: str = 'quarterly'):  # ->pd.DataFrame | None:

        if period == 'quarterly':
            return self._stock_data.quarterly_balance_sheet.loc[key, :]
        elif 'yearly':
            return self._stock_data.balance_sheet.loc[key, :]
