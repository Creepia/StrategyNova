import streamlit as st
import pandas as pd
from shutil import rmtree
import talib as tal
import streamlit_authenticator as stauth
import os
import yaml
import datetime
from yaml.loader import SafeLoader
from self_tools import *
from streamlit.components.v1 import html

# 加载认证配置文件
with open('stauth.yaml') as f:
    config = yaml.load(f, Loader=SafeLoader)

# 初始化认证器
authenticator = stauth.Authenticate(
    config['credentials'],
    config['cookie']['name'],
    config['cookie']['key'],
    config['cookie']['expiry_days'],
    config['preauthorized']
)


@st.cache_data
def getDataframe(market: str, stock: str, strategy: str, stop_loss: int, take_profit: int, date_interval: tuple[str, str]) -> tuple[pd.DataFrame, pd.DataFrame]:
    """
    - 获取当前需要的Dataframe（带有缓存修饰器）.
    - 返回(df,testback_result).
    - 返回的df带有 标准差 平均值 以及选择的策略需要的指标列.
    - 返回的testback_result带有 ID alldays times win_rate total_returns annual_returns 列.
    ## Parameters
    - market: 市场
    - stock: 股票
    - strategy: 策略
    - stop_loss: 止损倍率
    - take_profit: 止盈倍率
    - date_interval: 时间段
    """
    start_date, end_date = date_interval
    start_date = pd.to_datetime(start_date)
    end_date = pd.to_datetime(end_date)

    df = pd.read_csv(f'public_source/{market}/{stock}')
    # print(start_date,end_date)
    df = df[(pd.to_datetime(df['日期']) >= start_date) & (
        pd.to_datetime(df['日期']) <= end_date)].reset_index(drop=True)
    # st.write(pd.to_datetime(df['日期']))

    df['STD'] = df['收盘'].rolling(50).std()
    df['MA'] = df['收盘'].rolling(50).mean()

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

    Signals = exp.eval()
    TestBack = testback_data(Signals,stop_loss,take_profit).iloc[:,1:]
    TestBack = TestBack.reset_index(drop=True)

    # concat(df,TestBack)
    df = df.copy() if TestBack.empty else TestBack.copy(
    ) if df.empty else pd.concat([df, TestBack], axis=1)

    testback_result = result(TestBack)

    return df, testback_result


def showIndexPage():

    # 初始化用户文件夹
    for folder in ['source', 'applied_indicators', 'signals', 'testback', 'summary']:
        if not os.path.exists(f'users/{st.session_state["username"]}/{folder}/default_set'):
            os.makedirs(
                f'users/{st.session_state["username"]}/{folder}/default_set')

    # 侧边栏
    with st.sidebar:
        # 页面标题：单股分析
        st.title("Single Stock Analysis")

        # 第一个选项：选择市场
        sources = os.listdir('public_source')
        market = st.selectbox("Market", sources)

        # 第二个选项：股票
        single_stocks = os.listdir(f'public_source/{market}')
        stock = st.selectbox("Stock", single_stocks+['ALL'])

        # 日期区间
        from_day = "2000-01-01"
        to_day = "2024-01-30"
        from_day = st.text_input('From day', value=from_day, key='from_day')
        to_day = st.text_input('To day', value=to_day, key='to_day')
        date_interval = (from_day, to_day)

        # 策略
        strategies = ['SMA', 'MACD','AROON']
        strategy = st.selectbox("Strategy", strategies)

        # 控制最大持有天数、最小持有天数、止盈点、止损点
        # 目前最大持有天数和最小持有天数还没定
        max_hold_day = st.text_input('max hold day', key='max_hold_day')
        min_hold_day = st.text_input('min hold day', key='min_hold_day')
        stop_loss = st.text_input(
            'stop loss(Standard Deviation)', "1", key='stop_loss')
        take_profit = st.text_input(
            'take profit(Standard Deviation)', "2", key='take_profit')

        # 登出部分
        authenticator.logout('Logout', 'main', key='logout_button')

    # 主界面
    f'### Welcome {st.session_state["name"]}!'

    tab_Dataframe, tab_Chart = st.tabs(['Dataframe', 'Chart'])

    with tab_Dataframe:
        if (stock != 'ALL'):
            col_left, col_right = st.columns([0.7, 0.3])
            df, res = getDataframe(market, stock, strategy, float(
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
                    'annual_returns': str(round(res['annual_returns'].iloc[0]*100, 2))+"%"},
                    dtype='str', index=['result'])
                st.dataframe(res_show.T, use_container_width=True)
        else:
            RES = map(lambda s: getDataframe(market, s, strategy, float(
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


# 渲染登录界面并处理登录逻辑
if 'authentication_status' not in st.session_state:
    st.session_state['authentication_status'] = None

if st.session_state['authentication_status'] is not True:
    authenticator.login('Login', 'main')

# 根据认证状态显示内容
if st.session_state["authentication_status"] is True:
    showIndexPage()

    # (测试中)修改默认页面布局，内嵌html
    html(
        """
    <script src="https://ajax.aspnetcdn.com/ajax/jQuery/jquery-3.7.1.min.js"></script>
    <script>
         console.log("Testing1");
        $(document).ready(function(){
         console.log("Testing2");
            $("button[kind='icon']", window.parent.document).remove();
            $(".appview-container .main .block-container").css("padding-top","1rem");
         console.log("Testing3");
        })
    </script>
    """, width=0, height=0)
    st.markdown("""
                <style>
                    .st-emotion-cache-16txtl3{{
                        padding-top: 1rem;
                    }}
                </style>
                """,unsafe_allow_html=True)
    '---'

elif st.session_state["authentication_status"] is False:
    st.error('Username/password is incorrect')
elif st.session_state["authentication_status"] is None:
    st.warning('Please enter your username and password')
