import pandas as pd
from datetime import date
from dateutil.relativedelta import relativedelta
from functools import wraps
from typing import Tuple, List, Union, Callable
from pandas import Series
from io import BytesIO
import numpy as np
import yfinance as yf
import FinanceDataReader as fdr
from datetime import timedelta
import plotly.graph_objects as go
import streamlit as st
from sqlalchemy import create_engine


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

    def __call__(self, func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs) -> List[Union[bytes, go.Figure]]:
            ds = func(*args, **kwargs)
            name = ds.name
            to_pctchange_cum = kwargs.get('to_pctchange_cum')
            try:
                title = name.split(":")[0].strip()
                suffix = name.split(":")[1].strip()
            except:
                suffix = None
            
            fig = go.Figure()
            
            
            
            if title == 'Beveridge Curve':
                fig = _add_scatter(fig=fig, ds=ds)
                title = f'{title} with {suffix}'
                
                
            else:
                if self.plot_type == "line":
                    fig.add_trace(go.Scatter(
                        x=ds.index,
                        y=ds,
                        mode='lines',
                        line=dict(color='blue', width=2, dash='solid'),
                        name='Data'
                    ))
                    
                    fig = _add_annotation(fig, ds, pos='recent', suffix=suffix)
                    fig = _add_annotation(fig, ds, pos='max', suffix=suffix)
                    fig = _add_annotation(fig, ds, pos='min', suffix=suffix)
                elif self.plot_type == "bb_band":

                    upper_band, middle_band, lower_band = bollinger_bands(ds, timeperiod=20, nbdevup=2, nbdevdn=2)
                    fig.add_trace(go.Scatter(
                        x=upper_band.index,
                        y=upper_band,
                        mode='lines',
                        line=dict(color='gray', width=0.5),
                        name='Upper Band'
                    ))
                    

                    fig.add_trace(go.Scatter(
                        x=middle_band.index,
                        y=middle_band,
                        mode='lines',
                        line=dict(color='black', width=0.6),
                        name='Middle Band'
                    ))
                    fig.add_trace(go.Scatter(
                        x=lower_band.index,
                        y=lower_band,
                        mode='lines',
                        line=dict(color='gray', width=0.5),
                        name='Lower Band'
                    ))
                elif self.plot_type == "ma":
                    _, middle_band, _ = bollinger_bands(ds, timeperiod=20, nbdevup=2, nbdevdn=2)
                    fig.add_trace(go.Scatter(
                        x=middle_band.index,
                        y=middle_band,
                        mode='lines',
                        line=dict(color='blue', width=0.8),
                        name='Moving Average'
                    ))

                if self.draw_horiz is not None:
                    for title_draw, scope in self.draw_horiz.items():
                        if title == title_draw:
                            min_label = scope.split(",")[0].strip()
                            max_label = scope.split(",")[1].strip()
                            fig = _add_horiz_min_max(fig, ds, min_label=min_label, max_label=max_label)
                
                if self.add_recession:
                    fig = _add_recession_periods(fig, ds)
                
                if self.secondary_plot == "stock_sheet":
                    fig, title = _add_stock_sheet(fig, ds)
                elif self.secondary_plot == "pct_change":
                    fig = _add_pct_change(fig, ds)


            if to_pctchange_cum:
                fig.update_layout(yaxis_title="Cumulative Return (%)")
                
            fig.update_layout(      #title
                title={
                    'text': title,
                    'x': 0.5,  # X 위치를 0.5로 설정하여 중앙 정렬
                    'xanchor': 'center',  # X 축을 중앙에 앵커링
                    'yanchor': 'top'  # Y 축을 상단에 앵커링
                }
            )
            if self.mode_binary:
                buf = BytesIO()
                fig.write_image(buf, format='png', width=1000, height=1000)
                buf.seek(0)
                return [buf.getvalue()]
            else:
                return [fig]

        return wrapper

def bollinger_bands(ds: pd.Series, timeperiod: int = 20, nbdevup: int = 2, nbdevdn: int = 2) -> Tuple[
    pd.Series, pd.Series, pd.Series]:
    middle_band = ds.rolling(window=timeperiod).mean()
    std_dev = ds.rolling(window=timeperiod).std()

    upper_band = middle_band + (nbdevup * std_dev)
    lower_band = middle_band - (nbdevdn * std_dev)

    return upper_band, middle_band, lower_band

def _add_recession_periods(fig: go.Figure, ds: pd.Series) -> go.Figure:
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
    
    # Define the visible range of data
    min_date = ds.index.min()
    max_date = ds.index.max()
    
    # Filter recession periods within the visible range
    df_recession_periods = df_recession_periods[
        (df_recession_periods['end'] >= min_date) & (df_recession_periods['start'] <= max_date)
    ]

    # Adjust y-axis range to fit the recession periods
    y_min, y_max = ds.min(), ds.max()
    
    for _, row in df_recession_periods.iterrows():
        fig.add_shape(
            go.layout.Shape(
                type='rect',
                x0=row['start'],
                x1=row['end'],
                y0=y_min,
                y1=y_max,
                fillcolor='lightgray',
                opacity=0.3,
                layer='below',
                line=dict(width=0)
            )
        )
    
    return fig


def _add_annotation(fig: go.Figure, ds: pd.Series, pos: str = "recent", suffix: str = None, fontsize: int = 12, color='black', alpha=0.3, visible_index: bool = True) -> go.Figure:
    # 주석을 추가할 위치 선택
    if pos == 'min':
        x = ds.idxmin()
    elif pos == 'max':
        x = ds.idxmax()
    elif pos == 'recent':
        x = ds.index[-1]  # 최근 데이터
    elif pos == 'first':
        x = ds.index[0]  # 첫 번째 데이터
    elif pos == 'middle':
        x = ds.index[int(len(ds) / 2)]  # 중간 데이터

    # y값은 선택된 위치의 값
    y = ds[x]

    # 주석 텍스트 포맷
    if suffix is None:
        text = f"{x.strftime('%y-%m')}, {np.round(y, 1)}" if visible_index else f"{np.round(y, 1)}"
    else:
        text = f"{np.round(y, 1)}{suffix}, {x.strftime('%y-%m')}" if visible_index else f"{np.round(y, 1)}{suffix}"

    # Plotly에 주석 추가
    fig.add_annotation(
        x=x,  # x 좌표 (날짜)
        y=y,  # y 좌표 (값)
        text=text,  # 주석 내용
        showarrow=True,  # 화살표 표시 여부
        arrowhead=2,  # 화살표 스타일
        ax=0, ay=-30,  # 화살표 끝 위치
        font=dict(size=fontsize, color=color),  # 폰트 스타일
        bgcolor=f"rgba(255, 255, 255, {alpha})",  # 배경색
    )
    
    return fig


def _add_horiz_min_max(fig: go.Figure, ds: pd.Series, min_label: str = "CAPE:26", max_label: str = "CAPE:32"):
    min_pos = int(min_label.split(":")[-1])
    max_pos = int(max_label.split(":")[-1])
    mid_point = ds.index[int(len(ds.index) / 2)]

    # 최소, 최대 위치에 수평선을 추가
    fig.add_hline(y=min_pos, line_dash="dash", line_color="lightblue", annotation_text=min_label,
                  annotation_position="bottom right")
    fig.add_hline(y=max_pos, line_dash="dash", line_color="lightblue", annotation_text=max_label,
                  annotation_position="bottom right")

    return fig

def _add_pct_change(fig: go.Figure, ds: pd.Series) -> go.Figure:
    ds_pct_change = ds.pct_change() * 100

    # 변화율 그래프 추가
    fig.add_trace(go.Scatter(x=ds_pct_change.index, y=ds_pct_change,
                             mode='lines', fill='tozeroy', fillcolor='rgba(255, 0, 0, 0.1)',
                             line=dict(color='red'),
                             name='% Change'))

    num = int(len(ds_pct_change) * 0.1)
    top = ds_pct_change.nlargest(num).iloc[-1] * 2
    bottom = ds_pct_change.nsmallest(num).iloc[-1] * 2
    if bottom > 0: 
        bottom = 0

    fig.update_yaxes(range=[bottom, top], visible=False, secondary_y=True)
    
    return fig


def _add_scatter(fig: go.Figure, ds: pd.Series, y: dict = {'UNRATE':'Unemployment Rate'}, x: dict = {'JTSJOR':'Job Openings Rate'}) -> go.Figure:

    start = ds.index[0]
    end = ds.index[-1]
    col_name = ds.name.split(':')[-1]
    y_name = list(y.values())[0]
    x_name = list(x.values())[0]

   
    
    # FRED에서 실업률, 구인율 데이터 가져오기
    unemployment_rate = fdr.DataReader(f'FRED:{list(y.keys())[0]}', start=start, end=end).iloc[:,0]
    job_opening_rate = fdr.DataReader(f'FRED:{list(x.keys())[0]}', start=start, end=end).iloc[:,0]

    ref_treasury = ds

    # 데이터 통합
    data = pd.concat([unemployment_rate, job_opening_rate, ref_treasury], axis=1)
    data.columns = [y_name, x_name, col_name]

    # 결측값 처리
    data = data.ffill().resample('ME').last().dropna()

    # 최근 2년 데이터 필터링
    two_years_ago = (end - timedelta(days=365 * 2)).strftime('%Y-%m-%d')
    recent_data = data.loc[two_years_ago:].copy()

    # 3개월 이동평균 계산
    recent_data[f'{y_name} MA'] = recent_data[y_name].rolling(window=6).mean()
    recent_data[f'{x_name} MA'] = recent_data[x_name].rolling(window=6).mean()

    # 최근 데이터 선택 (마지막 데이터 포인트)
    latest_data = data.tail(1)

    # 산점도 추가
    fig.add_trace(go.Scatter(
        x=data[y_name],
        y=data[x_name],
        mode='markers',
        marker=dict(
            size=data[col_name] * 5,  # 점의 크기를 10년 금리로 설정
            color=data[col_name],  # 색상으로 10년 금리 사용
            colorscale='Cividis',  # Cividis 컬러맵 적용
            showscale=True,
            opacity=0.8
        ),
        name='Scatter'
    ))

    # 최근 5년 데이터에 3개월 이동평균 추세선 추가
    fig.add_trace(go.Scatter(
        x=recent_data[f'{y_name} MA'],
        y=recent_data[f'{x_name} MA'],
        mode='lines',
        line=dict(color='red', width=1),
        name='3-Month Moving Average'
    ))

    # 최근 데이터 레이블 추가
    fig.add_trace(go.Scatter(
        x=latest_data[y_name],
        y=latest_data[x_name],
        mode='markers+text',
        text=[f'{col_name}: {latest_data[col_name].values[0]:.2f}%'],
        textposition='top center',
        marker=dict(size=latest_data[col_name].values[0] * 2, color='red', line=dict(color='red', width=2)),
        name=f'Latest {col_name}'
    ))

    # 그래프 레이아웃 설정
    fig.update_layout(
        xaxis_title="Unemployment Rate (%)",
        yaxis_title="Job Openings Rate (%)",
        legend=dict(font=dict(size=8), title_font=dict(size=10)),
        margin=dict(l=40, r=40, t=40, b=40),
        plot_bgcolor='white'
    )

    return fig
def _add_stock_sheet(fig: go.Figure, ds: pd.Series) -> go.Figure:
    key = str(ds.name)

          
    cf = CashFlow(symbol=key)
    
    def _add_shares(fig, ds: pd.Series):
        key = ds.name
        
        @index_to_datetime
        def _request_shares(ticker: str = 'AAPL', key:str ='shares'):
            stock = yf.Ticker(ticker)
            if key == 'shares':
                shares = stock.get_shares_full(start="2000-01-01")
                return shares
            elif key == 'splits':
                splits = stock.splits
                return splits
                
        shares = _request_shares(key, 'shares')
        splits = _request_shares(key, 'splits')

        if shares is None:
            return fig
        
        adjusted_shares = shares.copy()
        adjusted_shares = adjusted_shares.astype(float)
        
        for (date, split) in splits.items():
            adjusted_shares[adjusted_shares.index >date] = adjusted_shares[adjusted_shares.index >date] / split
            
        threshold = adjusted_shares.quantile(0.99)
        adjusted_shares =adjusted_shares.apply(lambda x: np.nan if x > threshold else x)
        adjusted_shares = adjusted_shares.ffill()
        
        adjusted_shares = adjusted_shares.pct_change().add(1).cumprod().sub(1).mul(100).rolling(90).mean().round(1)
        
        fig.add_trace(go.Scatter(
            x=adjusted_shares.index,
            y=adjusted_shares,
            mode='lines',
            line=dict(color='blue', width=2, dash='solid'),
            name='shares',
            hovertemplate='%{x}<br>%{y:.2f}%'  # y 값을 %로 표시하고 x 값도 함께 표시
        ))
        return fig
        
    def _add_dividends(fig, ds: pd.Series):
        
        @index_to_datetime
        def _request_dividends(key: str = 'AAPL', select_col = 'Dividends' ,start: str = None, end: str = None) -> pd.Series:
            df = yf.Ticker(ticker=key).history(start=start, end=end)
            df = df[select_col].round(1)
            df.name = key
            return df
        
        ds = ds.sort_index()
        idx = ds.index
        start = idx[0]
        end = idx[-1]  
        
        dividends = _request_dividends(key=ds.name, select_col='Dividends',start=start, end=end)
        dividends = dividends[dividends>0]
        close = _request_dividends(key=ds.name, select_col='Close',start=start, end=end)
        
        df = pd.merge(dividends, close, left_index=True, right_index=True)
        df = pd.merge(df, ds, left_index=True, right_index=True)
        df.columns = ['Dividends', 'Close_price', 'Close']
        df['dividend_ratio'] = (df['Dividends'] / df['Close_price']) * 100
        df['dividend_ratio'] = df['dividend_ratio'].round(2)
        
        # Dividends 값을 0과 1 사이로 정규화
        min_dividends = df['Dividends'].min()
        max_dividends = df['Dividends'].max()
        # 정규화된 Dividends 값 계산

        if max_dividends == min_dividends:
            size = pd.Series(data=[0.5] *len(df), index=df.index)
            
        else:
            size = ((df['Dividends'] - min_dividends) / (max_dividends - min_dividends))

        hover_text = df.apply(lambda row: f"Date: {row.name.date()}<br>Dividend: {row['Dividends']}, {row['dividend_ratio']}%", axis=1)

        fig.add_trace(
            go.Scatter(
                x=df.index,
                y=df['Close'] + 1,
                mode='markers',
                marker=dict(
                    size=size +10,  
                    color=size,  
                    colorscale='Reds',
                    line=dict(
                    width=1,  
                    color='grey'  
                ) 
                ),
                text=hover_text,  # 호버 시 표시할 텍스트
                hoverinfo='text',  
                name='Dividends'
            )
        )

        return fig
                    
        


    def _adjust_index(ds1: pd.Series, ds2: pd.Series) -> pd.Series:
        ds1 = ds1.apply(lambda x: np.nan)
        ds1_month = ds1.index.strftime('%Y-%m')

        for date, value in ds2.items():
            year_month = pd.to_datetime(date).strftime('%Y-%m')
            ds1.loc[ds1_month == year_month] = value
        ds1 = ds1.ffill()
        return ds1



    def _draw_cashflow(fig: go.Figure, ds_cash_flow: pd.Series, ds_exp: pd.Series, yaxis='y2', color='blue', suffix: str = "% exp") -> go.Figure:
        # 색을 채우는 부분
        
        if color == 'red':
            fill_color = 'rgba(255, 0, 0, 0.1)'
        elif color == 'blue':
            fill_color = 'rgba(0, 0, 255, 0.1)'
        fig.add_trace(go.Scatter(
            x=ds_cash_flow.index,
            y=ds_cash_flow,
            mode='none',
            fill='tozeroy',
            fillcolor=fill_color,
            line=dict(color='rgba(255,255,255,0)'),
            yaxis=yaxis
        ))
        
        # 지표 선
        fig.add_trace(go.Scatter(
            x=ds_exp.index,
            y=ds_exp,
            mode='lines',
            line=dict(color=fill_color, width=2),
            name=suffix,
            yaxis=yaxis
        ))
        
        # 주석 추가
        _add_annotation(fig, ds_exp, pos="recent", yaxis=yaxis, textposition='top left', suffix=suffix, color=color, visible_index=False)

        
        return fig

    def _add_stock_info(dict_info: dict) -> str:
        long_name = dict_info.get("long name")
        title = f"{long_name}\n" if long_name else dict_info.get("symbol")
        enterprise_value = int(dict_info.get('enterprise value', 0))
        market_cap = int(dict_info.get('market cap', 0))
        
        try: 
            cap_ev = round(market_cap / enterprise_value, 2)
        except:
            cap_ev = None
        
        
        if cap_ev is not None:
            
            info_text = (
                f"<b style='font-size: 15px;'>{title}</b><br>"
                f"<span style='font-size: 13px;'>"
                f"PE(Tr/Fw): {dict_info.get('trailing PE')}/{dict_info.get('forward PE')} | Cash: {cap_ev}<br>"
                f"Payout: {int(dict_info.get('payout ratio', 0))}% | Dividend: {dict_info.get('dividend yield', 0)}% | Short: {dict_info.get('short ratio', 0)}"
                f"</span>"
            )
            
            
        else:
            info_text = (
                f"<b style='font-size: 15px;'>{title}</b><br>"
            )
            
            
        return info_text

    dict_cashflow = {"Cash Flow from Operations(%)": cf.ratio_income_div_operating(),
                       "Cash Flow from Assets(%)": cf.ratio_income_div_assetes()}

    
    if all(v is not None for v in dict_cashflow.values()):
        dict_cashflow_adjusted = {k: _adjust_index(ds, v) for k, v in dict_cashflow.items()}
        # dict_cashflow_y_adjusted = {k: _adjust_index(ds, v.sort_index(ascending=False)[:2]) for k, v in dict_cashflow_adjusted.items()}

        dict_cashflow_expectation = {k: v.apply(lambda x: v.mean()) for k, v in dict_cashflow_adjusted.items()}
    
        ds_cash_flow_operations = dict_cashflow_adjusted.get("Cash Flow from Operations(%)")
        ds_expectation_operations = dict_cashflow_expectation.get("Cash Flow from Operations(%)").fillna(0)
        ds_cash_flow_assets = dict_cashflow_adjusted.get("Cash Flow from Assets(%)")
        ds_expectation_assets = dict_cashflow_expectation.get("Cash Flow from Assets(%)").fillna(0)


        # st.write(ds_cash_flow_operations)
        fig = _draw_cashflow(fig, ds_cash_flow_operations, ds_expectation_operations, color='red', suffix="% from Operations")
        fig = _draw_cashflow(fig, ds_cash_flow_assets, ds_expectation_assets, color='blue', suffix="% from Assets")
        # st.plotly_chart(fig, use_container_width=True)
        bottom = min(ds_cash_flow_operations.min(), ds_cash_flow_assets.min())
        top = max( ds_cash_flow_operations.max(), ds_cash_flow_assets.max())
        
        
        _add_annotation(fig, ds_cash_flow_operations, pos="max", yaxis='y2', suffix='%', color='red',textposition='top right', visible_index=True)
        _add_annotation(fig, ds_cash_flow_operations, pos="min", yaxis='y2', suffix='%', color='red',textposition='top right', visible_index=True)
        fig.update_layout(
            yaxis2=dict(
                overlaying='y',
                side='right',
                range=[bottom, top * 3],
                showgrid=False,
                zeroline=False,
                showticklabels=False
            )
        )
    
    fig = _add_dividends(fig, ds=ds)
    fig = _add_shares(fig, ds=ds)
    title = _add_stock_info(cf.get_info())
    return fig, title

def _add_annotation(fig: go.Figure, ds: pd.Series, pos: str = "recent", yaxis='y',suffix: str = None, fontsize: int = 13, color='black',
                    textposition='top center', visible_index: bool = True) -> go.Figure:
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
    else:
        raise ValueError("Invalid position. Choose from 'min', 'max', 'recent', 'first', 'middle'.")

    y = ds[x]
    
    text = ""
    if suffix is None:
        if visible_index:
            text = f"{x.strftime('%y-%m')}, {np.round(y, 1)}"
        else:
            text = f"{np.round(y, 1)}"
    else:
        if visible_index:
            text = f"{np.round(y, 1)}{suffix}, {x.strftime('%y-%m')}"
        else:
            text = f"{np.round(y, 1)}{suffix}"
    
    fig.add_trace(go.Scatter(
        x=[x],
        y=[y],
        mode='text',
        text=[text],
        textposition=textposition,
        textfont=dict(
            size=fontsize,
            color=color
        ),
        yaxis=yaxis
    ))

    return fig
    

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
            self._info['payout ratio'] = round(float(self._stock_data.info.get("payoutRatio")) *100, 1)
            self._info['dividend yield'] = round(float(self._stock_data.info.get("dividendYield")) *100, 1)
            
        except:
            pass
        return self._info

    @index_to_datetime
    def ratio_income_div_operating(self) -> pd.Series | None:
        try:
            net_income = self._from_balance_sheet('Net Income From Continuing Operations')
            operating_cashflow = self._from_balance_sheet('Cash Flow From Continuing Operating Activities')
            return (net_income / operating_cashflow).rename('영업 활동으로 발생하는 현금 흐름 (Income/Operating)') * 100
        except Exception as e:
            return None
        
    @index_to_datetime
    def ratio_income_div_assetes(self) -> pd.Series | None:
        try:
            net_income = self._from_balance_sheet('Net Income From Continuing Operations')
            total_assets = self._from_balance_sheet('Total Assets')
            return (net_income / total_assets).rename('자산 대비 수익 창출 능력 (Income/Assets)') * 100
        except Exception as e:
            return None

    @retry
    def _from_balance_sheet(self, key='Total Assets') ->pd.DataFrame | None:    
        """
        Args:
            key (str, optional): _description_. Defaults to 
            
            'Total Assets'.
            'Net Income From Continuing Operations'
            'Cash Flow From Continuing Operating Activities'

        Returns:
            pd.DataFrame | None: _description_
        """
        if 'assets' in key.lower():
            y =  self._stock_data.balance_sheet.loc[key, :]
            q= self._stock_data.quarterly_balance_sheet.loc[key, :]
        else:
            y =  self._stock_data.cashflow.loc[key, :]
            q= self._stock_data.quarterly_cashflow.loc[key, :]
            
        y = y.sort_index()
        q = q.sort_index()

        last_year = y.index[-1]
        last_q = q.index[-1]
        
        if last_year != last_year:
            y= y.shift(-1)
            y.loc[last_q] = q[q.index > str(last_year)].cumsum()[last_q]
            y = y.bfill()
        else:
            y = y.dropna()
            
        return y
