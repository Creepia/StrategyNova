import streamlit as st
import pandas as pd
from shutil import rmtree
import streamlit_authenticator as stauth
import os
import yaml
import datetime
from yaml.loader import SafeLoader

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
def getDataframe(market,stock):
    if stock!='ALL':
        df=pd.read_csv(f'public_source/{market}/{stock}')
    return df

def showIndexPage():

    # 初始化用户文件夹
    for folder in ['source', 'applied_indicators', 'signals', 'testback', 'summary']:
        if not os.path.exists(f'users/{st.session_state["username"]}/{folder}/default_set'):
            os.makedirs(
                f'users/{st.session_state["username"]}/{folder}/default_set')

    # 页面设计
    with st.sidebar:
        # 页面标题：单股分析
        st.sidebar.title("Single Stock Analysis")

        # 第一个选项：选择市场
        sources = os.listdir('public_source')
        market = st.sidebar.selectbox("Market", sources)

        # 第二个选项：股票
        single_stocks = os.listdir(f'public_source/{market}')
        stock = st.sidebar.selectbox("Stock", single_stocks)

        # 日期区间
        earlist_date = datetime.date(2000, 1, 1)
        latest_date = datetime.date(2024, 1, 30)
        date_inteval = st.date_input(
            "Select the date inteval", (earlist_date, latest_date), min_value=earlist_date, max_value=latest_date, format="YYYY-MM-DD")

        # 策略

        # 控制最大持有天数、最小持有天数、止盈点、止损点

        # 登出部分
        authenticator.logout('Logout', 'main', key='logout_button')

    f'### Welcome {st.session_state["name"]}!'

    tab_Dataframe, tab_Chart = st.tabs(['Dataframe', 'Chart'])
    with tab_Dataframe:
        df=getDataframe(market,stock)
        df

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
