import streamlit as st
import pandas as pd
from self_tools import NewPage

st.set_page_config(
    page_title="Home",
    page_icon="🏠",
    initial_sidebar_state = "collapsed"
)

def showHomePage():
    """
    显示Home页面.
    """
    # st.write('<style>div.block-container{padding:1% 1%;max-width:95%}</style>', unsafe_allow_html=True)

    st.write(f'''
             <h1 style="text-align:center">Welcome {st.session_state["name"]}</h1>
             <p style="text-align:center">No item here yet...</p>
             <p style="text-align:center">Something should be shown...</p>
             '''
             , unsafe_allow_html=True)


page=NewPage(showHomePage,"home")