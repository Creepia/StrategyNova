from st_pages import show_pages_from_config
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



def showPage():

    # Show pages
    show_pages_from_config(".streamlit/pages.toml")

NewPage(showPage)