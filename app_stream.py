import streamlit as st
from PIL import Image
import io
from bot.src_data.economic_indicators import EconomicIndicators
from bot.src_data.stock_indicators import StockIndicators
from bot.src_data.commodity_indicators import CommodityIndicators
from bot.src_data.fx_indicators import FxIndicators
from bot.src_data.multpl import MultplIndicators

def display_indicators():
    # Sidebar for choosing indicator type
    indicator_type = st.sidebar.selectbox(
        "Select Indicator Type", 
        ["Stock Indicators", "Economic Indicators", "Commodity Indicators", "FX Indicators", "Multpl Indicators"]
    )
    
    # Initialize the appropriate class based on the selected indicator type
    if indicator_type == "Stock Indicators":
        indicator_class = StockIndicators()
    elif indicator_type == "Economic Indicators":
        indicator_class = EconomicIndicators()
    elif indicator_type == "Commodity Indicators":
        indicator_class = CommodityIndicators()
    elif indicator_type == "FX Indicators":
        indicator_class = FxIndicators()
    elif indicator_type == "Multpl Indicators":
        indicator_class = MultplIndicators()
    
    # Get the keys for the selected indicator type
    indicator_keys = indicator_class.dict_indicators.keys()
    
    # Sidebar for selecting specific indicator
    selected_indicator = st.sidebar.selectbox("Select an Indicator", indicator_keys)
    
    st.title(f"{indicator_type} > {selected_indicator}")
    
    if selected_indicator:
        # Convert generator to list
        if selected_indicator == "Economic Indicators":
            start='2000-01-01'
        else: 
            start= None
        image_data_list = list(indicator_class.requests(selected_indicator, start=start))
        
        # Calculate number of columns needed
        num_columns = 3
        num_images = len(image_data_list)
        num_rows = (num_images + num_columns - 1) // num_columns  # Calculate rows needed
        
        # Create a grid layout with 3 columns
        for row in range(num_rows):
            cols = st.columns(num_columns)
            for col in range(num_columns):
                index = row * num_columns + col
                if index < num_images:
                    image_data = image_data_list[index]
                    image = Image.open(io.BytesIO(image_data))
                    with cols[col]:
                        st.image(image, use_column_width=True)
                else:
                    with cols[col]:
                        st.write("")  # Empty space if no image to show

if __name__ == "__main__":
    display_indicators()
