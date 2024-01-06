import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from st_pages import show_pages_from_config
import os
import talib as tal

class Indicator:
    def __init__(self,name:str,need:list[str]):
        self.name=name
        self.need=need
    def calculate(self):
        raise PermissionError('Indicator is a raw class type')
    
class RSI(Indicator):
    def __init__(self,name:str):
        self.name=name
        self.need=['收盘']
    def calculate(self,day):
        return 

class RANDOM(Indicator):
    def __init__(self,name:str,need:list[str]):
        self.name=name
        self.need=['收盘']

# Show pages
show_pages_from_config()

'#### Indicators'

source_stock_set = st.selectbox('Source Stock Set', tuple(os.listdir('source')))

indicators=['RSI','EMA','MACD']
selected_indicators = st.multiselect('selected indicators',indicators,[])

preview_df = pd.read_csv(f'source/{source_stock_set}/' + os.listdir(f'source/{source_stock_set}')[0]) if os.listdir(f'source/{source_stock_set}') else None

with st.sidebar:
    for ind in selected_indicators:
        if ind=='EMA':
            '**EMA**'
            _params_ema_days = int(st.text_input('days',6))
        elif ind=='RSI':
            '**RSI**'
            _params_rsi_days = int(st.text_input('days',14))
        elif ind=='MACD':
            '**MACD**'
            _params_macd_fastperiod = int(st.text_input('fastperiod',10))
            _params_macd_slowperiod = int(st.text_input('slowperiod',20))
            _params_macd_signalperiod = int(st.text_input('signalperiod',9))

btn_preview_for_one_stock = st.button('Preview for one stock')
if btn_preview_for_one_stock:
    selected_indicators
    # list_params={k[8:]:v for k,v in globals().items() if k.startswith('_params_')}
    for ind in selected_indicators:
        if(preview_df.shape[0]==0):
            continue
        if ind=='EMA':
            if('收盘' in preview_df):
                preview_df['EMA']=tal.EMA(preview_df['收盘'],_params_ema_days)
            else:
                st.error(f'Indicator {ind} needs "收盘" column')
            continue
        if ind=='RSI':
            if('收盘' in preview_df):
                preview_df['RSI']=tal.RSI(preview_df['收盘'],_params_rsi_days)
            else:
                st.error(f'Indicator {ind} needs "收盘" column')
            continue
        if ind=='MACD':
            if('收盘' in preview_df):
                _, _, preview_df["MACD"] = tal.MACD(preview_df['收盘'], _params_macd_fastperiod, _params_macd_slowperiod, _params_macd_signalperiod)
            else:
                st.error(f'Indicator {ind} needs "收盘" column')
            continue

'#### Preview for one stock in the set'
st.dataframe(preview_df)

if st.button('Apply Indicators',type='primary',disabled=not btn_preview_for_one_stock):
    prg_applying_indicators = st.progress(0, text='Applying Indicators...')
    if not os.path.exists(f'applied_indicators/{source_stock_set}'):
        os.makedirs(f'applied_indicators/{source_stock_set}')
    prg_applying_indicators.progress(10,'Applying Indicators...')
    #  To every file, applied all the indicators
    for file in os.listdir(f'source/{source_stock_set}'):
        source_path = f'source/{source_stock_set}/{file}'
        target_path = f'applied_indicators/{source_stock_set}/{file}'
        data=pd.read_csv(source_path)
        if(data.shape[0]==0):
            continue
        for ind in selected_indicators:
            if ind=='EMA':
                if('收盘' in data):
                    data['EMA']=tal.EMA(data['收盘'],_params_ema_days)
                else:
                    st.error(f'Indicator {ind} needs "收盘" column')
                continue
            if ind=='RSI':
                if('收盘' in data):
                    data['RSI']=tal.RSI(data['收盘'],_params_rsi_days)
                else:
                    st.error(f'Indicator {ind} needs "收盘" column')
                continue
            if ind=='MACD':
                if('收盘' in data):
                    _, _, data["MACD"] = tal.MACD(data['收盘'], _params_macd_fastperiod, _params_macd_slowperiod, _params_macd_signalperiod)
                else:
                    st.error(f'Indicator {ind} needs "收盘" column')
                continue
        data.to_csv(target_path,index=False)
    prg_applying_indicators.progress(100,'Finished')
