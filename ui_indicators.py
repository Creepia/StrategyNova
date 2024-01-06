import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from st_pages import show_pages_from_config
import os

class Indicator:
    def __init__(self,name:str,need:list[str]):
        self.name=name
        self.need=need
    def calculate(self):
        raise PermissionError('Indicator is a raw class type')
    
class RSI(Indicator):
    def __init__(self,name:str):
        self.name=name
        self.need=['收盘']
    def calculate(self,day):
        return 

class RANDOM(Indicator):
    def __init__(self,name:str,need:list[str]):
        self.name=name
        self.need=['收盘']

# Show pages
show_pages_from_config()

'#### Indicators'

source_stock_set = st.selectbox('Source Stock Set', tuple(os.listdir('source')))

indicators=['RSI','RANDOM']
selected_indicators = st.multiselect('selected indicators',indicators,[])