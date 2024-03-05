import streamlit as st
import pandas as pd
import os

from streamlit_echarts import st_pyecharts
from self_tools import *

st.set_page_config(
    page_title="Analysis",
    page_icon="📊"
)

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
    """
    显示Analysis页面.
    """

    st.write('<style>div.block-container{padding:1% 1%;max-width:95%}</style>', unsafe_allow_html=True)
    
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
        from_day = st.text_input('From day', value="2000-01-01", key='analysis_from_day')
        to_day = st.text_input('To day', value="2024-01-30", key='analysis_to_day')
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
            col_left, col_right = st.columns([0.66, 0.34])
            df, res = getDataFrame_analysis(market, stock, strategy, float(
                stop_loss), float(take_profit), date_interval)
            with col_left:
                st.dataframe(df,height=500,use_container_width=True,hide_index=True)
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
            # 在Streamlit页面上显示图表
            # f'{df.iloc[0,0]}'
            st.write(f'''<h3 style="text-align:center;padding:0;">Buy and Sell Points Visualization</h3>''', unsafe_allow_html=True)

            buy_sell_points_graph=graph_buy_sell_points(df)
            st_pyecharts(buy_sell_points_graph, width='95%', height='450%')

            # 在 Streamlit 页面上显示图表
            st.write(f'''<h3 style="text-align:center;padding:0;">Price and Value Over Time</h3>''', unsafe_allow_html=True)

            price_over_time_graph=graph_value_over_time(df)
            st_pyecharts(price_over_time_graph,width = '95%', height='450%')







page=NewPage(showAnalysisPage,"analysis")
