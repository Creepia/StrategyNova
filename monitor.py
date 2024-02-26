from st_pages import show_pages_from_config
from analysis import getDataframe,ALL_STRATEGIES
import streamlit as st
import pandas as pd
import talib as tal
from self_tools import *
from streamlit.components.v1 import html



def showMonitorPage():

    # Show pages
    show_pages_from_config(".streamlit/pages.toml")

    # 侧边栏
    with st.sidebar:

        # 第一个选项：选择市场
        sources = os.listdir('public_source')
        market = st.selectbox("Market", sources,key='monitor_market')

        # 第二个选项：股票
        single_stocks = os.listdir(f'public_source/{market}')
        stocks = st.multiselect("Stocks", single_stocks,key='monitor_stocks')

        # 日期区间
        from_day = "2000-01-01"
        to_day = "2024-01-30"
        from_day = st.text_input('From day', value=from_day, key='monitor_from_day')
        to_day = st.text_input('To day', value=to_day, key='monitor_to_day')
        date_interval = (from_day, to_day)

        stop_loss = st.text_input(
            'stop loss(Standard Deviation)', "1", key='monitor_stop_loss')
        take_profit = st.text_input(
            'take profit(Standard Deviation)', "2", key='monitor_take_profit')

        dfs=[]
        if st.button("start",type="primary"):
            for strategy in ALL_STRATEGIES:
                RES = map(lambda s: (getDataframe(market, s, strategy, float(stop_loss), float(take_profit), date_interval)[0].tail(1)), stocks)
                dfs.append(pd.concat(RES,ignore_index=True))

    # 主页面
    tab_Dataframes, tab_Others = st.tabs(['Dataframe', 'Others'])
    with tab_Dataframes:
        for df in dfs:
            st.dataframe(df)



page=NewPage(showMonitorPage,"monitor")