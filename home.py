from st_pages import show_pages_from_config
import streamlit as st
import pandas as pd
from self_tools import NewPage

def showHomePage():
    """
    显示Home页面.
    """
    # Show pages
    show_pages_from_config(".streamlit/pages.toml")

    f'### Welcome {st.session_state["name"]}!'

    """
    - No item here yet...
    - Something should be shown in home page...
    """

page=NewPage(showHomePage,"home")