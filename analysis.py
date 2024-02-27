from st_pages import show_pages_from_config
import streamlit as st
import pandas as pd
import talib as tal
import os
from self_tools import *
from streamlit.components.v1 import html



# Strategies added here will be able to be selected
ALL_STRATEGIES = ['SMA', 'MACD','AROON', 'RSI', 'BOLLING','KDJ','MACD KDJ']
def apply_stragy(strategy, df):
    if strategy == 'MACD':
        _, df["MACD_SIG"], df["MACD_HIST"] = tal.MACD(df['收盘'], 12, 26, 9)
        # 买入条件：MACD线向上穿过MACD信号线
        # 卖出条件：MACD线向下穿过MACD信号线
        exp = Expression(
            'MACD_HIST crossup MACD_SIG | MACD_HIST crossdown MACD_SIG', df)
    elif strategy == 'SMA':
        df["SMA10"] = tal.SMA(df["收盘"], 10)
        df["SMA20"] = tal.SMA(df["收盘"], 20)
        df["SMA50"] = tal.SMA(df["收盘"], 50)
        # 买入条件：(SMA10向上穿过SMA20 且 SMA20>=SMA50) 或 (SMA20向上穿过SMA50 且 SMA10>=SMA20)
        # 卖出条件：(SMA10向上穿过SMA20 且 SMA20>=SMA50) 或 (SMA20向上穿过SMA50 且 SMA10>=SMA20)
        exp = Expression(
            'SMA10 crossup SMA20 AND SMA20 >= SMA50 or SMA20 crossup SMA50 AND SMA10 >= SMA20 | SMA10 crossdown SMA20 AND SMA20 <= SMA50 or SMA20 crossdown SMA50 AND SMA10 <= SMA20', df)
    elif strategy=='AROON':
        Aroon(df)
        exp = Expression('Aroon_Up > 70 and Aroon_Down < 30 | Aroon_Up < 30 and Aroon_Down > 70', df)
    elif strategy=='RSI':
        df["RSI"] = tal.RSI(df['收盘'], timeperiod=14)
        #买入条件：RSI小于30
        #卖出：大于70
        exp = Expression('RSI < 30 | RSI >70',df)
    elif strategy=='BOLLING':
        df['upper_band'], df['middle_band'], df['lower_band'] = tal.BBANDS(df['收盘'], timeperiod=14, nbdevup=2, nbdevdn=2)
        # 如果收盘价上穿 BOLL 上轨，则买入 ; 如果收盘价下穿 BOLL 下轨，则开盘卖掉
        exp = Expression('收盘 crossup upper_band | 收盘 crossdown lower_band', df)
    elif strategy=='KDJ':
        df['KLine'], df['DLine'] = tal.STOCH(df["最高"], df["最低"], df["收盘"], fastk_period=9, slowk_period=5, slowk_matype=1, slowd_period=5, slowd_matype=1)
        df['JLine'] = 3 * df['KLine'] - 2 * df['DLine']
        # 买入条件：K线向上穿过D线
        # 卖出条件：K线向下穿过D线
        exp = Expression('KLine crossup DLine | KLine crossdown DLine', df)
    return exp






























@st.cache_data
def getDataFrame_analysis(market: str, stock: str, strategy: str, stop_loss: int, take_profit: int, date_interval: tuple[str, str]) ->  pd.DataFrame:
    """
    getDataFrame在analysis页面的实现...（带有缓存修饰器）
    ## Parameters
    - market: 市场
    - stock: 股票
    - strategy: 策略
    - stop_loss: 止损倍率
    - take_profit: 止盈倍率
    - date_interval: 时间段
    """
    return getDataframe(market, stock, strategy, float(stop_loss), float(take_profit), date_interval)











def showAnalysisPage():

    # Show pages
    show_pages_from_config(".streamlit/pages.toml")
    
    # 侧边栏
    with st.sidebar:
        # 页面标题：单股分析
        st.title("Single Stock Analysis")

        # 第一个选项：选择市场
        sources = os.listdir('public_source')
        market = st.selectbox("Market", sources)

        # 第二个选项：股票
        single_stocks = os.listdir(f'public_source/{market}')
        stock = st.selectbox("Stock", single_stocks+['ALL'],key="analysis_stock")

        # 日期区间
        from_day = st.text_input('From day', value="2000-01-01", key='from_day')
        to_day = st.text_input('To day', value="2024-01-30", key='to_day')
        date_interval = (from_day, to_day)

        # 策略
        strategy = st.selectbox("Strategy", ALL_STRATEGIES)

        # 控制最大持有天数、最小持有天数、止盈点、止损点
        # 目前最大持有天数和最小持有天数还没定
        max_hold_day = st.text_input('max hold day', key='max_hold_day')
        min_hold_day = st.text_input('min hold day', key='min_hold_day')
        stop_loss = st.text_input(
            'stop loss(Standard Deviation)', "1", key='stop_loss')
        take_profit = st.text_input(
            'take profit(Standard Deviation)', "2", key='take_profit')


    # 主界面
    

    tab_Dataframe, tab_Chart = st.tabs(['Dataframe', 'Chart'])

    with tab_Dataframe:
        if (stock != 'ALL'):
            col_left, col_right = st.columns([0.6, 0.4])
            df, res = getDataFrame_analysis(market, stock, strategy, float(
                stop_loss), float(take_profit), date_interval)
            with col_left:
                st.dataframe(df, use_container_width=True)
            with col_right:
                res_show = pd.DataFrame({
                    'ID': res['ID'].iloc[0],
                    'alldays': res['alldays'].iloc[0],
                    'times': res['times'].iloc[0],
                    'win_rate': str(round(res['win_rate'].iloc[0]*100, 2))+"%",
                    'total_returns': str(round(res['total_returns'].iloc[0]*100, 2))+"%",
                    'annual_returns': str(round(res['annual_returns'].iloc[0]*100, 2))+"%",
                    'total_return_premium': str(round(res['total_return_premium'].iloc[0] * 100, 2)) + "%",
                    'annual_return_premium': str(round(res['annual_return_premium'].iloc[0] * 100, 2)) + "%"},
                    dtype='str', index=['result'])
                st.dataframe(res_show.T, use_container_width=True)
        else:
            RES = map(lambda s: getDataFrame_analysis(market, s, strategy, float(
                stop_loss), float(take_profit), date_interval)[1], single_stocks)
            res = pd.DataFrame(
                columns=['ID', 'alldays', 'times', 'win_rate', 'total_returns', 'annual_returns'])
            for r in RES:
                # concat(res,r)
                res = res.copy() if r.empty else r.copy(
                ) if res.empty else pd.concat([res, r])
            res_mean = res.mean()
            st.dataframe(res, use_container_width=True)
            st.dataframe(res_mean, use_container_width=True)

    with tab_Chart:
        if (stock != 'ALL'):
            # 示例数据
            df['日期'] = pd.to_datetime(df['日期'])
            # 在Streamlit页面上显示图表
            st.title('Buy and Sell Points Visualization')
            plot_buy_sell_points(df)

            # 在 Streamlit 页面上显示图表
            st.title('Price and Value Over Time')
            plot_value_over_time(df)







page=NewPage(showAnalysisPage,"analysis")
