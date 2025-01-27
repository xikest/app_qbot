import streamlit as st
from datetime import datetime
from bot.src_data.economic_indicators import EconomicIndicators
from bot.src_data.stock_indicators import StockIndicators
from bot.src_data.commodity_indicators import CommodityIndicators
from bot.src_data.fx_indicators import FxIndicators
from bot.src_data.multpl import MultplIndicators

@st.cache_data
def loading_data(_indicator_class, selected_indicators, start=None, end=None, periods=None, to_pctchange_cum=False):
    fig_list = []
    for indicator in selected_indicators:
        fig_list.extend(_indicator_class.requests(indicator, start=start, end=end, periods=periods, to_pctchange_cum=to_pctchange_cum))
    return fig_list

def add_ticker():
    # This function will be called when the user presses Enter in the text_input field
    new_ticker = st.session_state.new_ticker
    if new_ticker and new_ticker not in st.session_state.selected_tickers:
        st.session_state.selected_tickers.add(new_ticker)  # 티커를 세트로 추가
        st.session_state.new_ticker = ""  # 입력 필드를 초기화
        
def select_date_sidebar():
    start_year, end_year = st.sidebar.slider(
        "Select Year Range",
        min_value=2000,
        max_value=2025,
        value=(2020, 2025),  # Default range
        step=1
    )
    
    # Convert selected years to strings in 'YYYY-MM-DD' format
    start = f"{start_year}-01-01"
    current_year = datetime.today().strftime('%Y')
    if end_year == current_year:
        end = datetime.today().strftime('%Y-%m-%d')
    else:
        end = f"{end_year}-12-31"
    
    return start, end
        
def display_indicators():
    st.set_page_config(layout="wide")
    
    # Sidebar for choosing indicator type
    indicator_type = st.sidebar.selectbox(
        "Select Indicator Type", 
        ["Stock Indicators", "Economic Indicators", "Commodity Indicators", "FX Indicators", "Multpl Indicators"],
        index=0  # Default value
    )
    
    # Initialize the appropriate class based on the selected indicator type
    indicator_class = {
        "Stock Indicators": StockIndicators,
        "Economic Indicators": EconomicIndicators,
        "Commodity Indicators": CommodityIndicators,
        "FX Indicators": FxIndicators,
        "Multpl Indicators": MultplIndicators
    }.get(indicator_type)()

    # Default empty values
    selected_indicators = []
    start = end = None

    if indicator_type == "Stock Indicators":
        # Use a radio button to switch between Select Indicators and Search ticker in the sidebar
        selected_view = st.sidebar.radio("Options", ["Select Indicators", "Search ticker"])
        
        start, end = select_date_sidebar()
        
        
        if selected_view == "Select Indicators":
            # Get the keys for the selected indicator type
            indicator_keys = list(indicator_class.dict_indicators.keys())
            
            # Sidebar for selecting specific indicators using checkboxes
            selected_indicators = st.sidebar.multiselect("Select Indicators", indicator_keys)
            
            
        elif selected_view == "Search ticker":
            st.sidebar.write("Search for a specific ticker.")
            
            # List to store selected tickers as a set
            if 'selected_tickers' not in st.session_state:
                st.session_state['selected_tickers'] = set()  # 세트로 변경

            st.sidebar.text_input(
                "Enter ticker symbol and press Enter",
                key="new_ticker",
                on_change=add_ticker
            )
            # Display selected tickers with the option to remove
            st.sidebar.write("Selected Tickers:")
            tickers_to_remove = set()
            for ticker in st.session_state.selected_tickers:
                col1, col2 = st.sidebar.columns([0.8, 0.2])
                with col1:
                    st.write(ticker)
                with col2:
                    if st.button("X", key=f"remove_{ticker}"):
                        tickers_to_remove.add(ticker)

            # Remove selected tickers
            if tickers_to_remove:
                st.session_state.selected_tickers -= tickers_to_remove

            # Use selected tickers as indicators
            selected_tickers = list(st.session_state.selected_tickers)
            
            # st.write("Selected indicators: ", selected_indicators)
            selected_indicators.append({ticker: ticker for _, ticker in enumerate(selected_tickers)})

    else:
        # For other indicator types, show standard layout without the radio button
        indicator_keys = list(indicator_class.dict_indicators.keys())
        
        # Sidebar for selecting specific indicators using checkboxes
        selected_indicators = st.sidebar.multiselect("Select Indicators", indicator_keys)
        
        start, end = select_date_sidebar()


    if selected_indicators:
        try:
            periods = 10 if indicator_type != "Economic Indicators" else None
            
            if indicator_type != "Economic Indicators":
                to_pctchange_cum = True 
            else:
                to_pctchange_cum = False 
            if indicator_type == "Stock Indicators":
                st.title(f"{indicator_type} (CPI adjusted)")

            fig_list = loading_data(indicator_class, selected_indicators, start=start, end=end, periods=periods, to_pctchange_cum=to_pctchange_cum) 
            
            # Calculate number of columns needed
            num_columns = 4
            num_figs = len(fig_list)
            num_rows = (num_figs + num_columns - 1) // num_columns  # Calculate rows needed
            
            # Create a grid layout with columns
            for row in range(num_rows):
                cols = st.columns(num_columns)
                for col in range(num_columns):
                    index = row * num_columns + col
                    if index < num_figs:
                        fig = fig_list[index]
                        
                        # Update layout for thumbnails
                        fig.update_layout(
                            title=dict(text=fig.layout.title.text, x=0.5, y=0.95),
                            margin=dict(t=100, b=30, l=30, r=30),
                            width=500,  # Width for thumbnails
                            height=500,  # Height for thumbnails
                            legend=dict(visible=False)  # Hide legend for thumbnails
                        )
                        
                        with cols[col]:
                            st.plotly_chart(fig, use_container_width=True)
                    else:
                        with cols[col]:
                            st.write("")  # Empty space if no figure to show

        except Exception as e:
            st.error(f"An error occurred: {e}")

if __name__ == "__main__":
    display_indicators()
