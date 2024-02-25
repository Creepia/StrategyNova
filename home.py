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
def getDataframe(market,stock,strategy,stop_loss,take_profit,date_interval):
    start_date, end_date = date_interval
    start_date = pd.to_datetime(start_date)
    end_date = pd.to_datetime(end_date)
    if stock!='ALL':
        df=pd.read_csv(f'public_source/{market}/{stock}')
    print(start_date,end_date)
    df=df[(pd.to_datetime(df['日期'])>=start_date) & (pd.to_datetime(df['日期'])<=end_date)].reset_index(drop=True)
    st.write(pd.to_datetime(df['日期']))
    
    df['STD'] = df['收盘'].rolling(50).std()
    df['MA'] = df['收盘'].rolling(50).mean()

    if strategy=='MACD':
        _, _, df["MACD"] = tal.MACD(df['收盘'], 10, 20, 9)
        exp=Expression('MACD < 0 | MACD > 0',df)
    elif strategy=='SMA':
        df["SMA10"]=tal.SMA(df["收盘"],10)
        df["SMA20"]=tal.SMA(df["收盘"],20)
        df["SMA50"]=tal.SMA(df["收盘"],50)
        # 买入条件：(SMA10向上穿过SMA20 且 SMA20>=SMA50) 或 (SMA20向上穿过SMA50 且 SMA10>=SMA20)
        # 卖出条件：(SMA10向上穿过SMA20 且 SMA20>=SMA50) 或 (SMA20向上穿过SMA50 且 SMA10>=SMA20)
        exp=Expression('SMA10 crossup SMA20 AND SMA20 >= SMA50 or SMA20 crossup SMA50 AND SMA10 >= SMA20 | SMA10 crossdown SMA20 AND SMA20 <= SMA50 or SMA20 crossdown SMA50 AND SMA10 <= SMA20',df)

    Signals=exp.eval()
    TestBack=testback_data(Signals,stop_loss,take_profit).iloc[:,2:]
    TestBack=TestBack.reset_index(drop=True)

    # concat(df,TestBack)
    df = df.copy() if TestBack.empty else TestBack.copy() if df.empty else pd.concat([df, TestBack],axis=1)

    testback_result = result(TestBack).T

    return df,testback_result

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
        stock = st.selectbox("Stock", single_stocks)
        

        # 日期区间
        from_day="2000-01-01"
        to_day="2024-01-30"
        from_day=st.text_input('From day',value=from_day, key='from_day')
        to_day=st.text_input('To day',value=to_day, key='to_day')
        date_interval=(from_day,to_day)
        

        # 策略
        strategies=['SMA','MACD']
        strategy = st.selectbox("Strategy", strategies)
        

        # 控制最大持有天数、最小持有天数、止盈点、止损点
        #目前最大持有天数和最小持有天数还没定
        max_hold_day=st.text_input('max hold day', key='max_hold_day')
        min_hold_day=st.text_input('min hold day', key='min_hold_day')
        stop_loss=st.text_input('stop loss(Standard Deviation)', "1", key='stop_loss')
        take_profit=st.text_input('take profit(Standard Deviation)', "2", key='take_profit')

        # 登出部分
        authenticator.logout('Logout', 'main', key='logout_button')


    # 主界面
    f'### Welcome {st.session_state["name"]}!'

    tab_Dataframe, tab_Chart = st.tabs(['Dataframe', 'Chart'])

    with tab_Dataframe:
        col_left,col_right = st.columns([0.7, 0.3])
        df,res=getDataframe(market,stock,strategy,float(stop_loss),float(take_profit), date_interval)
        from_day=df['日期'].iloc[0]
        to_day=df['日期'].iloc[-1]
        with col_left:
            st.dataframe(df,use_container_width=True)
        with col_right:
            st.dataframe(res,use_container_width=True)

    with tab_Chart:

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
            $("[data-testid='block-container']").css("padding","1rem 1rem 1rem 1rem");
         console.log("Testing3");
        })
    </script>
    """
    ,width=0,height=0)
    '---'
    
elif st.session_state["authentication_status"] is False:
    st.error('Username/password is incorrect')
elif st.session_state["authentication_status"] is None:
    st.warning('Please enter your username and password')
