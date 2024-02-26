from st_pages import show_pages_from_config
import streamlit as st
import pandas as pd
from self_tools import *
from streamlit.components.v1 import html

def showHomePage():
    
    # Show pages
    show_pages_from_config(".streamlit/pages.toml")

    f'### Welcome {st.session_state["name"]}!'

    """
    - No item here yet...
    - Something should be shown in home page...
    """

page=NewPage(showHomePage,"home")