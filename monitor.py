from st_pages import show_pages_from_config
from analysis import ALL_STRATEGIES
import streamlit as st
import pandas as pd
import talib as tal
from self_tools import *
from streamlit.components.v1 import html






@st.cache_data
def getDataFrame_monitor(market: str, stock: str, strategy: str, stop_loss: int, take_profit: int, date_interval: tuple[str, str]) ->  pd.DataFrame:
    """
    getDataFrame在monitor页面的实现（带有缓存修饰器）
    """
    return getDataframe(market, stock, strategy, float(stop_loss), float(take_profit), date_interval,doTestback=False).tail(1)











def showMonitorPage():
    """
    显示Monitor页面.
    """
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
        from_day = st.text_input('From day', value="2000-01-01", key='monitor_from_day')
        to_day = st.text_input('To day', value="2024-01-30", key='monitor_to_day')
        date_interval = (from_day, to_day)

        stop_loss = st.text_input(
            'stop loss(Standard Deviation)', "1", key='monitor_stop_loss')
        take_profit = st.text_input(
            'take profit(Standard Deviation)', "2", key='monitor_take_profit')

        dfs=[]
        if st.button("start",type="primary"):
            for strategy in ALL_STRATEGIES:
                RES = map(lambda s: getDataFrame_monitor(market, s, strategy, float(stop_loss), float(take_profit), date_interval), stocks)
                dfs.append(pd.concat(RES,ignore_index=True))

    # 主页面
    tab_Dataframes, tab_Others = st.tabs(['Dataframe', 'Others'])
    with tab_Dataframes:
        for i in range(len(dfs)):
            st.write(ALL_STRATEGIES[i])
            st.dataframe(dfs[i])



page=NewPage(showMonitorPage,"monitor")