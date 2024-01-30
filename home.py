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

# 加载配置文件
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
def getDataframe(market,stock,strategy,stop_loss,take_profit):
    if stock!='ALL':
        df=pd.read_csv(f'public_source/{market}/{stock}')
    
    df['STD'] = df['收盘'].rolling(50).std()
    df['MA'] = df['收盘'].rolling(50).mean()

    if strategy=='MACD':
        _, _, df["MACD"] = tal.MACD(df['收盘'], 10, 20, 9)
        exp=Expression('MACD < 0 | MACD > 0',df)
    elif strategy=='SMA':
        df["SMA"]=tal.SMA(df["收盘"],10)
        exp=Expression('SMA < 50 | SMA > 50',df)

    Signals=exp.eval()
    TestBack=testback_data(Signals,stop_loss,take_profit).iloc[:,2:]
    TestBack=TestBack.reset_index(drop=True)

    # concat(df,TestBack)
    df = df.copy() if TestBack.empty else TestBack.copy() if df.empty else pd.concat([df, TestBack],axis=1)
        
    testback_result=result(TestBack).T

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
        earlist_date = datetime.date(2000, 1, 1)
        latest_date = datetime.date(2024, 1, 30)
        date_inteval = st.date_input(
            "Select the date inteval", (earlist_date, latest_date), min_value=earlist_date, max_value=latest_date, format="YYYY-MM-DD")

        # 策略
        strategies=['SMA','MACD']
        strategy = st.selectbox("Strategy", strategies)
        

        # 控制最大持有天数、最小持有天数、止盈点、止损点
        max_hold_day=st.text_input('max hold day',key='max_hold_day')
        min_hold_day=st.text_input('min hold day',key='min_hold_day')
        stop_loss=st.text_input('stop loss',"1",key='stop_loss')
        take_profit=st.text_input('take profit',"1.5",key='take_profit')

        # 登出部分
        authenticator.logout('Logout', 'main', key='logout_button')


    # 主界面
    f'### Welcome {st.session_state["name"]}!'

    tab_Dataframe, tab_Chart = st.tabs(['Dataframe', 'Chart'])

    with tab_Dataframe:
        col_left,col_right = st.columns([0.7, 0.3])
        df,res=getDataframe(market,stock,strategy,float(stop_loss),float(take_profit))
        with col_left:
            st.dataframe(df,use_container_width=True)
        with col_right:
            st.dataframe(res,use_container_width=True)

    with tab_Chart:
        pass

    '---'


# 渲染登录界面并处理登录逻辑
if 'authentication_status' not in st.session_state:
    st.session_state['authentication_status'] = None

if st.session_state['authentication_status'] is not True:
    authenticator.login('Login', 'main')

# 根据认证状态显示内容
if st.session_state["authentication_status"] is True:
    showIndexPage()
elif st.session_state["authentication_status"] is False:
    st.error('Username/password is incorrect')
elif st.session_state["authentication_status"] is None:
    st.warning('Please enter your username and password')
