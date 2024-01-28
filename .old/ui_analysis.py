import streamlit as st
import pandas as pd
from st_pages import show_pages_from_config
import os

# Show pages
show_pages_from_config()

'#### Analysis'

stock_set_name = st.selectbox('Stock Set', tuple(os.listdir(f'users/{st.session_state["username"]}/summary')),placeholder='default_set')

signal_set_name = st.selectbox('Signal Set', tuple(os.listdir(f'users/{st.session_state["username"]}/summary/{stock_set_name}')),placeholder='')

summary_file=pd.read_csv(f'users/{st.session_state["username"]}/summary/{stock_set_name}/{signal_set_name}')
st.dataframe(summary_file,use_container_width=True)
