import os
# efiniance data seems from https://fund.eastmoney.com/
import efinance as ef
import streamlit as st
import pandas as pd
from st_pages import show_pages_from_config

# Show pages
show_pages_from_config()

set_name = st.text_input('set_name', 'default_set',key='set_name')

tab_upload,tab_download= st.tabs(['Upload', 'Download'])

with tab_upload:
    '#### Upload Files'
    uploaded_files = st.file_uploader('Choose csv files', accept_multiple_files=True,type='csv')
    
    if st.button('Upload Data') and uploaded_files is not None:
        if not os.path.exists(f'users/{st.session_state["username"]}/source/{set_name}'):
            os.makedirs(f'users/{st.session_state["username"]}/source/{set_name}')

        i=0.0
        prg_uploading_data = st.progress(i,'Ready for uploading data...')
        for f in uploaded_files:
            i += 1
            prg = i / len(uploaded_files)
            prg_uploading_data.progress(prg,'Uploading...')
            data=pd.read_csv(f)
            data.to_csv(f'users/{st.session_state["username"]}/source/{set_name}/{f.name}',index=False)
        prg_uploading_data.progress(1.0,'Finished')

with tab_download:
    '#### Download from web'

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
        if not os.path.exists(f'users/{st.session_state["username"]}/source/{set_name}'):
            os.makedirs(f'users/{st.session_state["username"]}/source/{set_name}')
        stocks=stocks.split(',')
        prg_download_online_data = st.progress(0, text='Downloading...')
        data = ef.stock.get_quote_history(stocks,begin_date,end_date,klt=101)
        prg_download_online_data.progress(50,'Saving...')
        for k,v in data.items():
            v.to_csv(f'users/{st.session_state["username"]}/source/{set_name}/{k}.csv',index=False)
        prg_download_online_data.progress(100,'Download finished! You may go to indicator page for adding indicators for the stock set.')