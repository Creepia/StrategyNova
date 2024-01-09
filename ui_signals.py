import streamlit as st
import pandas as pd
import numpy as np
from st_pages import show_pages_from_config
import os

class Expression:
    def __init__(self,s:str,data:pd.DataFrame):
        '''
        - self.tokens: A sequence of dataframes and operators
        '''
        self.data=data
        self.tokens:list[str|pd.DataFrame]=[]
        self.values_stack:list[pd.DataFrame]=[]
        self.symbols_stack:list[str]=[]
        self.precedences={
            '$':0,
            '|':1,
            'and':2,
            '>':3,
            '<':3,
            '>=':3,
            '<=':3,
            '==':3,
            'crossup':3,
            'crossdown':3
        }
        for token in s.split(' '):
            if token in self.precedences:
                self.tokens.append(token)
            elif token.isdigit():
                self.tokens.append(pd.Series(np.repeat(float(token),data.shape[0])))
            elif token in data.columns:
                self.tokens.append(data[token])
            elif token=='RANDOM':
                rand_signals = pd.Series(np.random.randint(3,size=data.shape[0]))
                rand_signals = rand_signals.replace({0:'',1:'buy',2:'sell'})
                self.tokens.append(rand_signals)
            else:
                st.error('Invalid Expression')
        # st.write(self.tokens)

    def doOp(self):
        op = self.symbols_stack.pop()
        y = self.values_stack.pop()
        x = self.values_stack.pop()
        # ('==============\n==============',op,y,x,sep='\n')
        # First deal with them as 'buy' signals, then change the signals to 'sell' when operating '|'
        if op == '|':
            y=y.map({'buy':'sell'})
            signals=x.combine_first(y)
            self.values_stack.append(signals)
        elif op == 'and':
            signals=x.where(x==y,None)
            self.values_stack.append(signals)
        elif op == '>':
            signals = pd.Series(np.where(x > y, 'buy', None))
            self.values_stack.append(signals)
        elif op == '>=':
            signals = pd.Series(np.where(x >= y, 'buy', None))
            self.values_stack.append(signals)
        elif op == '<':
            signals = pd.Series(np.where(x < y, 'buy', None))
            self.values_stack.append(signals)
        elif op == '<=':
            signals = pd.Series(np.where(x <= y, 'buy', None))
            self.values_stack.append(signals)
        elif op == '==':
            signals = pd.Series(np.where(x == y, 'buy', None))
            self.values_stack.append(signals)
        elif op == 'crossup':
            signals=pd.Series(np.where((x.shift() < y.shift()) & (x > y),'buy',None))
            self.values_stack.append(signals)
        elif op == 'crossdown':
            signals=pd.Series(np.where((x.shift() > y.shift()) & (x < y),'buy',None))
            self.values_stack.append(signals)
        # print(self.values_stack[-1],'==============\n==============',sep='\n')
    def repeatOps(self,op):
        while len(self.values_stack)>1 and self.precedences[op]<=self.precedences[self.symbols_stack[-1]]:
            #st.write(op)
            self.doOp()
            #st.write(self.values_stack[-1])
    def eval(self):
        # st.write(self.tokens)
        for token in self.tokens:
            # print(token,type(token))
            if isinstance(token,str):
                # print('===A str===')
                self.repeatOps(token)
                self.symbols_stack.append(token)
            elif isinstance(token,pd.Series) or isinstance(token,pd.DataFrame):
                # print('===A dataframe===')
                self.values_stack.append(token)
        self.repeatOps('$')
        self.values_stack[-1] = pd.DataFrame({'日期':self.data['日期'],'收盘':self.data['收盘'],'signals':self.values_stack[-1]})
        # st.write(self.values_stack)
        # st.write(self.symbols_stack)
        if not (len(self.values_stack)==1 and len(self.symbols_stack)==0):
            st.error('Something Wrong of calculating signals')
        return self.values_stack[-1]

# Show pages
show_pages_from_config()

'#### Signals'
applied_indicators_set = st.selectbox('Applied Indicator Set', tuple(os.listdir('applied_indicators')))

signal_set_name = st.text_input('Signal Set Name','good_signals')

any_file_with_indicators = f'applied_indicators/{applied_indicators_set}/' + os.listdir(f'applied_indicators/{applied_indicators_set}')[0]
list_columns = pd.read_csv(any_file_with_indicators).columns.tolist()

signal_conditions=['RANDOM']
if 'EMA' in list_columns:
    # buy condition | sell condition
    signal_conditions.append('收盘 > EMA | 收盘 < EMA')
if 'MACD' in list_columns:
    signal_conditions.append('MACD crossup 0 | MACD crossdown 0')
    signal_conditions.append('MACD < 0 | MACD > 0')
if 'DMI' in list_columns:
    signal_conditions.append('DIP crossup DIN | DIP crossdown DIN')
current_condition = st.selectbox('Saved Condition',signal_conditions)

with st.expander('Custom Expression'):
    text_expression = st.text_area('Signal Expression (buy condition | sell condition)',current_condition)

btn_preview_for_one_stock = st.button('Preview for one stock')
if btn_preview_for_one_stock:
    exp=Expression(text_expression,pd.read_csv(any_file_with_indicators))
    st.dataframe(exp.eval())

# Similar part as the ui_indicators.py
if st.button('Calculate for the set',type='primary',disabled=not btn_preview_for_one_stock):
    prg_applying_indicators = st.progress(0, text='Calculating...')
    if not os.path.exists(f'signals/{applied_indicators_set}/{signal_set_name}'):
        os.makedirs(f'signals/{applied_indicators_set}/{signal_set_name}')
    prg_applying_indicators.progress(10,'Calculating...')
    #  To every file, calculate the signals
    for file in os.listdir(f'applied_indicators/{applied_indicators_set}'):
        source_path = f'applied_indicators/{applied_indicators_set}/{file}'
        target_path = f'signals/{applied_indicators_set}/{signal_set_name}/{file}'
        exp=Expression(text_expression,pd.read_csv(source_path))
        exp.eval().to_csv(target_path,index=False)
    prg_applying_indicators.progress(100,'Finished')
