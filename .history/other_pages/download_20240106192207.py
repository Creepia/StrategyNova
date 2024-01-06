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

begin_date = st.date_input('begin_date', '2000-01-01',format='YYYY-MM-DD')