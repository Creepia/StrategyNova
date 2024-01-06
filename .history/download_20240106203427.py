import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import os
#import efinance as ef
import streamlit as st
from st_pages import show_pages_from_config, add_page_title

# Show pages
show_pages_from_config()

st.write("""# Download""")

set_name = st.text_input('set_name', 'default_set')

stocks = st.text_area('stocks','')

col_begin_date, col_end_date = st.columns(2)
begin_date = col_begin_date.text_input('begin_date', '20000101')
end_date = col_end_date.text_input('end_date', '20240101')

btn_download_online_data = st.button('Download Online Data')
"""if btn_download_online_data:
    if not os.path.exists(set_name):
        os.makedirs(f'source/{set_name}')
    data = ef.stock.get_quote_history(stocks,begin_date,end_date,klt=101)
    st.write(data)"""