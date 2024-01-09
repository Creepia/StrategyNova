import streamlit as st
import pandas as pd
from st_pages import show_pages_from_config
import os

for folder in ['source/default_set','applied_indicators/default_set','signals/default_set','testback/default_set','result/default_set']:
    if not os.path.exists(folder):
        os.makedirs(folder)

# Show pages
show_pages_from_config()

'**This is an experimental ui for strategy research**'
'**Find different pages on the sidebar \:D**'
'---'

current_view = st.selectbox('Stock Set', tuple(os.listdir('source')),placeholder='default_set')
list_source = os.listdir(f'source/{current_view}')
view_data = pd.DataFrame({
    'stock_file':list_source,
    'shape':[pd.read_csv(f'source/{current_view}/{file}').shape for file in list_source]
                          })
st.dataframe(view_data,use_container_width=True)
