import streamlit as st
import plotly.graph_objects as go
from bot.src_data.economic_indicators import EconomicIndicators
from bot.src_data.stock_indicators import StockIndicators
from bot.src_data.commodity_indicators import CommodityIndicators
from bot.src_data.fx_indicators import FxIndicators
from bot.src_data.multpl import MultplIndicators

@st.cache_data
def loading_cash(_indicator_class, selected_indicators, start=None, periods=None,to_pctchange_cum =False):
    fig_list = []
    for indicator in selected_indicators:
        fig_list.extend(_indicator_class.requests(indicator, start=start, periods=periods, to_pctchange_cum = to_pctchange_cum ))
    return fig_list

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
    
    # Get the keys for the selected indicator type
    indicator_keys = list(indicator_class.dict_indicators.keys())
    
    # Sidebar for selecting specific indicators using checkboxes
    selected_indicators = st.sidebar.multiselect("Select Indicators", indicator_keys)
    
    st.title(f"{indicator_type} ▶ {', '.join(selected_indicators)}")
    
    if selected_indicators:
        try:
            start = '2000-01-01' if indicator_type == "Economic Indicators" else None
            if indicator_type != "Economic Indicators":
                periods = 10 
                to_pctchange_cum = True 
            fig_list = loading_cash(indicator_class, selected_indicators, start=start, periods=periods, to_pctchange_cum=  to_pctchange_cum) 
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
