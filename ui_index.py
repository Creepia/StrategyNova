import streamlit as st
import pandas as pd
from st_pages import show_pages_from_config
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
    for folder in [f'users/{st.session_state["username"]}/source/default_set',
                   f'users/{st.session_state["username"]}/applied_indicators/default_set',
                   f'users/{st.session_state["username"]}/signals/default_set',
                   f'users/{st.session_state["username"]}/testback/default_set',
                   f'users/{st.session_state["username"]}/summary/default_set']:
        if not os.path.exists(folder):
            os.makedirs(folder)

    # Show pages
    show_pages_from_config()
    f'### Welcome {st.session_state["name"]}!'
    '**This is an experimental ui for strategy research**'
    '**Find different pages on the sidebar \:D**'
    '---'

    tab_view_source,tab_clear_folder= st.tabs(['View Source', 'Clear Folder'])
    with tab_view_source:
        current_view = st.selectbox('Stock Set', tuple(os.listdir(f'users/{st.session_state["username"]}/source')),placeholder='default_set',key='index_current_stock_set')
        list_source = os.listdir(f'users/{st.session_state["username"]}/source/{current_view}')
        view_data = pd.DataFrame({
            'stock_file':list_source,
            'shape':[pd.read_csv(f'users/{st.session_state["username"]}/source/{current_view}/{file}').shape for file in list_source]
                                })
        st.dataframe(view_data,use_container_width=True)

    with tab_clear_folder:
        exist_folders=set(['applied_indicators','signals','testback','source','summary']).intersection(set(os.listdir(f'users/{st.session_state["username"]}/')))
        # st.write(set(['applied_indicators','signals','testback','source','summary']))
        # st.write(set(os.listdir('./')))
        option = st.selectbox('Choose the folder you want to clear...',exist_folders,key='folder_to_clear')
        clear_selected_folders_1 = st.button('CLEAR SELECTED FOLDERS?',type='secondary',key='clear_selected_folders_1')
        if st.button('CLEAR SELECTED FOLDERS!',type='primary',key='clear_selected_folders_2',disabled=not clear_selected_folders_1):
            # Avoid misdeletings
            if(len(option)>3):
                rmtree(f'users/{st.session_state["username"]}/{option}')
                st.success(f"Successfully clear '{option}' folder")
    '---'
    # 重設密碼部分
    if st.session_state["authentication_status"]:
        try:
            if authenticator.reset_password(st.session_state["username"], 'Reset password'):
                st.success('Password modified successfully')
        except Exception as e:
            st.error(e)

    # 更改個人信息部分
    if st.session_state["authentication_status"]:
        try:
            if authenticator.update_user_details(st.session_state["username"], 'Update user details'):
                st.success('Entries updated successfully')
        except Exception as e:
            st.error(e)

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
