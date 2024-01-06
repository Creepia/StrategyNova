import streamlit as st
from st_pages import show_pages_from_config, add_page_title
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# Show pages
show_pages_from_config()

"""# Download"""

set_name = st.text_input('set_name', 'default_set')

stocks = st.text_area('stocks','')

col_begin_date, col_end_date = st.columns(2)
begin_date = col_begin_date.text_input('begin_date', '20000101')
end_date = col_end_date.text_input('begin_date', '20240101')