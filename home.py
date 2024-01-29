import streamlit as st
import pandas as pd
from shutil import rmtree
import streamlit_authenticator as stauth
import os
import yaml
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



def showIndexPage():

    # 初始化用户文件夹
    for folder in ['source','applied_indicators','signals','testback','summary']:
        if not os.path.exists(f'users/{st.session_state["username"]}/{folder}/default_set'):
            os.makedirs(f'users/{st.session_state["username"]}/{folder}/default_set')

    f'### Welcome {st.session_state["name"]}!'
    '**This is an experimental ui for strategy research**'
    '**Find different pages on the sidebar \:D**'
    '---'

    tab_Dataframe,tab_Chart= st.tabs(['Dataframe', 'Chart'])
    with tab_Dataframe:
        pass

    with tab_Chart:
        pass

    '---'

    with st.sidebar:
        # 登出部分
        authenticator.logout('Logout', 'main', key='logout_button')

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


#页面设计
#页面标题：单股分析
st.sidebar.title("Single Stock Analysis")

#第一个选项：选择市场
selected_option = st.sidebar.selectbox("Market", ["US Market", "HongKong Market", "Chinese Market"])

#第二个选项：股票

#日期区间

#策略

#控制最大持有天数、最小持有天数、止盈点、止损点




