import streamlit as st
import pandas as pd
import numpy as np
from st_pages import show_pages_from_config
import os
import talib as tal

# Edit this part for adding more indicators
# -----------------------------------------------------
indicators=['MA','STD','RSI','EMA','MACD','SMA','SAR','WPR','CCI','ADX','KD','M_DI','P_DI','ADXR','MFI','OBV','RVI']

def add_ind_params(ind):
    st.write(f'**{ind}**')

    # 移动平均和移动标准差
    if ind=='MA':
        global _params_ma_windowsize
        _params_ma_windowsize=int(st.text_input('windowsize',50,key='_params_ma_windowsize'))
    elif ind=='STD':
        global _params_std_windowsize
        _params_std_windowsize=int(st.text_input('windowsize',50,key='_params_std_windowsize'))

    elif ind=='EMA':
        global _params_ema_days
        _params_ema_days = int(st.text_input('days',6))
    elif ind=='RSI':
        global _params_rsi_days
        _params_rsi_days = int(st.text_input('days',14))
    elif ind=='MACD':
        global _params_macd_fastperiod,_params_macd_slowperiod,_params_macd_signalperiod
        _params_macd_fastperiod = int(st.text_input('fastperiod',10))
        _params_macd_slowperiod = int(st.text_input('slowperiod',20))
        _params_macd_signalperiod = int(st.text_input('signalperiod',9))
    elif ind=='SMA':
        global _params_sma_days
        _params_sma_days = int(st.text_input('days',10))

    elif ind=='SAR':
        global _params_sar_accelaration,_params_sar_maximum
        _params_sar_accelaration = int(st.text_input('accelaration',0.02))
        _params_sar_maximum = int(st.text_input('maximum',0.2))
    elif ind=='WPR':
        global _params_wpr_days
        _params_wpr_days = int(st.text_input('days',14))
    elif ind=='CCI':
        global _params_cci_days
        _params_cci_days = int(st.text_input('days',20))
    elif ind=='ADX':
        pass
    # i.e. Stock
    elif ind=='KD':
        global _params_kd_fastkperiod,_params_kd_slowkperiod,_params_kd_slowkmatype,_params_kd_slowdperiod,_params_kd_slowdmatype
        _params_kd_fastkperiod = int(st.text_input('fast_k_period',5))
        _params_kd_slowkperiod = int(st.text_input('slow_k_period',3))
        _params_kd_slowkmatype = int(st.text_input('slow_k_matype',0))
        _params_kd_slowdperiod = int(st.text_input('slow_d_period',3))
        _params_kd_slowdmatype = int(st.text_input('slow_d_matype',0))
    elif ind=='M_DI':
        global _params_mdi_days
        _params_mdi_days = int(st.text_input('days',14))
    elif ind=='P_DI':
        global _params_pdi_days
        _params_pdi_days = int(st.text_input('days',14))
    elif ind=='ADXR':
        global _params_adxr_days
        _params_adxr_days = int(st.text_input('days',14))
    elif ind=='MFI':
        global _params_mfi_days
        _params_mfi_days = int(st.text_input('days',14))
    elif ind=='OBV':
        pass
    elif ind=='OBV':
        global _params_rvi_days
        _params_rvi_days = int(st.text_input('days',10))

def add_ind_to_df(ind,df):
    if(df.shape[0]==0):
        return
    elif ind=='MA':
        if('收盘' in df):
            df['MA'] = df['收盘'].rolling(window=_params_ma_windowsize).mean()
        else:
            st.error(f'Indicator {ind} needs "收盘" column')
    elif ind=='STD':
        if('收盘' in df):
            df['STD'] = df['收盘'].rolling(window=_params_std_windowsize).std()
        else:
            st.error(f'Indicator {ind} needs "收盘" column')

    elif ind=='EMA':
        if('收盘' in df):
            df['EMA']=tal.EMA(df['收盘'],_params_ema_days)
        else:
            st.error(f'Indicator {ind} needs "收盘" column')
    elif ind=='RSI':
        if('收盘' in df):
            df['RSI']=tal.RSI(df['收盘'],_params_rsi_days)
        else:
            st.error(f'Indicator {ind} needs "收盘" column')
    elif ind=='MACD':
        if('收盘' in df):
            _, _, df["MACD"] = tal.MACD(df['收盘'], _params_macd_fastperiod, _params_macd_slowperiod, _params_macd_signalperiod)
        else:
            st.error(f'Indicator {ind} needs "收盘" column')
    elif ind=='SMA':
        if('收盘' in df):
            df["SMA10"]=tal.SMA(df["收盘"],timeperiod=_params_sma_days)
        else:
            st.error(f'Indicator {ind} needs "收盘" column')
    
    elif ind=='SAR':
        if('最高' in df and '最低' in df):
            df["SAR"] = tal.SAR(df["最高"], df["最低"], _params_sar_accelaration, _params_sar_maximum)
        else:
            st.error(f'Indicator {ind} needs "最高" and "最低" columns')
    elif ind=='WPR':
        if('收盘' in df and '最高' in df and '最低' in df):
            def get_WPR(High, Low, Close, n):
                H_n = High.rolling(n).max()
                L_n = Low.rolling(n).min()
                return (H_n-Close)/(H_n-L_n) * 100
            df["WPR"] = get_WPR(df["最高"], df["最低"], df["收盘"], _params_wpr_days)
        else:
            st.error(f'Indicator {ind} needs "收盘" and "最高" and "最低" columns')
    elif ind=='CCI':
        if('收盘' in df and '最高' in df and '最低' in df):
            df["WPR"] = tal.CCI(df["最高"], df["最低"], df["收盘"], _params_cci_days)
        else:
            st.error(f'Indicator {ind} needs "收盘" and "最高" and "最低" columns')
    elif ind=='ADX':
        if('收盘' in df and '最高' in df and '最低' in df):
            df["ADX"] = tal.ADX(df["最高"], df["最低"], df["收盘"])
        else:
            st.error(f'Indicator {ind} needs "收盘" and "最高" and "最低" columns')
    elif ind=='KD':
        if('收盘' in df and '最高' in df and '最低' in df):
            df['SlowK'],df['SlowD'] = tal.STOCH(df['最高'],df['最低'],df['收盘'],_params_kd_fastkperiod,_params_kd_slowkperiod,_params_kd_slowkmatype,_params_kd_slowdperiod,_params_kd_slowdmatype)
        else:
            st.error(f'Indicator {ind} needs "收盘" and "最高" and "最低" columns')
    elif ind=='M_DI':
        if('收盘' in df and '最高' in df and '最低' in df):
            df["M_DI"]=tal.MINUS_DI(df["收盘"],timeperiod=_params_sma_days)
        else:
            st.error(f'Indicator {ind} needs "收盘" column')
    elif ind=='P_DI':
        if('收盘' in df):
            df["SMA10"]=tal.SMA(df["收盘"],timeperiod=_params_sma_days)
        else:
            st.error(f'Indicator {ind} needs "收盘" column')
    elif ind=='ADXR':
        if('收盘' in df):
            df["SMA10"]=tal.SMA(df["收盘"],timeperiod=_params_sma_days)
        else:
            st.error(f'Indicator {ind} needs "收盘" column')
    elif ind=='MFI':
        if('收盘' in df):
            df["SMA10"]=tal.SMA(df["收盘"],timeperiod=_params_sma_days)
        else:
            st.error(f'Indicator {ind} needs "收盘" column')
    elif ind=='OBV':
        if('收盘' in df):
            df["SMA10"]=tal.SMA(df["收盘"],timeperiod=_params_sma_days)
        else:
            st.error(f'Indicator {ind} needs "收盘" column')
    elif ind=='RVI':
        if('收盘' in df):
            df["SMA10"]=tal.SMA(df["收盘"],timeperiod=_params_sma_days)
        else:
            st.error(f'Indicator {ind} needs "收盘" column')
            
# -----------------------------------------------------

# Show pages
show_pages_from_config()

'#### Indicators'

source_stock_set = st.selectbox('Source Stock Set', tuple(os.listdir('source')))


selected_indicators = st.multiselect('selected indicators',indicators,[])
if 'STD' not in selected_indicators:
    st.warning('You must need to choose "STD" when you want to testback!')

preview_df = pd.read_csv(f'source/{source_stock_set}/' + os.listdir(f'source/{source_stock_set}')[0]) if os.listdir(f'source/{source_stock_set}') else None

with st.sidebar:
    for ind in selected_indicators:
        add_ind_params(ind)
        

btn_preview_for_one_stock = st.button('Preview for one stock')
if btn_preview_for_one_stock:
    selected_indicators
    # list_params={k[8:]:v for k,v in globals().items() if k.startswith('_params_')}
    for ind in selected_indicators:
        add_ind_to_df(ind,preview_df)

'#### Preview for one stock in the set'
st.dataframe(preview_df)

if st.button('Apply Indicators',type='primary',disabled=not btn_preview_for_one_stock):
    prg_applying_indicators = st.progress(0.0, text='Checking folder existency...')
    if not os.path.exists(f'applied_indicators/{source_stock_set}'):
        os.makedirs(f'applied_indicators/{source_stock_set}')
    #  To every file, applied all the indicators
    i=0.0
    for file in os.listdir(f'source/{source_stock_set}'):
        i += 1
        prg = i / len(os.listdir(f'source/{source_stock_set}'))
        print(prg)
        prg_applying_indicators.progress(prg,'Applying Indicators...')
        source_path = f'source/{source_stock_set}/{file}'
        target_path = f'applied_indicators/{source_stock_set}/{file}'
        data=pd.read_csv(source_path)
        for ind in selected_indicators:
            add_ind_to_df(ind,data)
        data.to_csv(target_path,index=False)
    prg_applying_indicators.progress(1.0,f'All indicators you choose have been added to stock set "{source_stock_set}". You may go to signals page to decide the buy or sell strategies.')