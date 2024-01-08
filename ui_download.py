import os
import efinance as ef
import streamlit as st
from st_pages import show_pages_from_config

# Show pages
show_pages_from_config()

'#### Download'

set_name = st.text_input('set_name', 'default_set')

with st.expander('Choose saved sets'):
    current_stock_set = st.selectbox('Change your stock set', tuple(os.listdir('.stock_sets')))
with open(f'.stock_sets/{current_stock_set}') as f:
    stocks = st.text_area('stocks',f.read())

col_begin_date, col_end_date = st.columns(2)
with col_begin_date:
    begin_date = st.text_input('begin_date', '20000101')
with col_end_date:
    end_date = st.text_input('end_date', '20240101')

if st.button('Download Online Data'):
    if not os.path.exists(f'source/{set_name}'):
        os.makedirs(f'source/{set_name}')
    stocks=stocks.split(',')
    prg_download_online_data = st.progress(0, text='Downloading...')
    data = ef.stock.get_quote_history(stocks,begin_date,end_date,klt=101)
    prg_download_online_data.progress(50,'Saving...')
    for k,v in data.items():
        v.to_csv(f'source/{set_name}/{k}.csv',index=False)
    prg_download_online_data.progress(100,'Finished')