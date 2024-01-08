import streamlit as st
import pandas as pd
import numpy as np
from st_pages import show_pages_from_config
import os

class Expression:
    def __init__(self,s:str,data:pd.DataFrame):
        '''
        - self.s: A sequence of dataframes and operators
        '''
        self.s:list[str|pd.DataFrame]=[]
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
                self.s.append(token)
            elif token.isdigit():
                self.s.append(pd.DataFrame(np.repeat(float(token),data.shape[0])))
            elif token in data.columns:
                self.s.append(data[token])
            elif token=='RANDOM':
                rand_signals = pd.DataFrame(np.random.randint(3,size=data.shape[0]))
                rand_signals = rand_signals.replace({0:'',1:'buy',2:'sell'})
                self.s.append(rand_signals)

    def doOp(self):
        op = self.symbols_stack.pop()
        y = self.values_stack.pop()
        x = self.values_stack.pop()
        # First deal with them as 'buy' signals, then change the signals to 'sell' when operating '|'
        if op == '|':
            y=y.map(lambda i:'sell' if i=='buy' else None)
            signals=x.combine_first(y)
            self.values_stack.append(signals)
        elif op == 'and':
            signals=x.where(x==y,None)
            self.values_stack.append(signals)
        elif op == '>':
            df=pd.concat([x,y],axis=1)
            signals=df.apply(lambda i:'buy' if x>y else None,axis=1)
            self.values_stack.append(signals)
        elif op == '>=':
            df=pd.concat([x,y],axis=1)
            signals=df.apply(lambda i:'buy' if x>=y else None,axis=1)
            self.values_stack.append(signals)
        elif op == '<':
            df=pd.concat([x,y],axis=1)
            signals=df.apply(lambda i:'buy' if x<y else None,axis=1)
            self.values_stack.append(signals)
        elif op == '<=':
            df=pd.concat([x,y],axis=1)
            signals=df.apply(lambda i:'buy' if x<=y else None,axis=1)
            self.values_stack.append(signals)
        elif op == '==':
            df=pd.concat([x,y],axis=1)
            signals=df.apply(lambda i:'buy' if x==y else None,axis=1)
            self.values_stack.append(signals)
        elif op == 'crossup':
            signals=pd.DataFrame(np.repeat(None,x.shape[0]))
            for i in range(1,x.shape[0]):
                st.write(x[i-1])
                if x.iloc[i-1]<y.iloc[i-1] and x.iloc[i]>y.iloc[i]:
                    signals[i]='buy'
            self.values_stack.append(signals)
        elif op == 'crossdown':
            signals=pd.DataFrame(np.repeat(None,x.shape[0]))
            for i in range(1,x.shape[0]):
                if x.iloc[i-1]>y.iloc[i-1] and x.iloc[i]<y.iloc[i]:
                    signals[i]='buy'
            self.values_stack.append(signals)
    def repeatOps(self,op):
        st.write(op)
        while len(self.values_stack)>1 and self.precedences[op]<=self.precedences[self.symbols_stack[-1]]:
            self.doOp()
    def eval(self):
        for token in self.s:
            if isinstance(token,str):
                self.repeatOps(token)
                self.symbols_stack.append(token)
            else:
                self.values_stack.append(token)
        self.repeatOps('$')
        st.write(self.values_stack)
        st.write(self.symbols_stack)
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
    signal_conditions.append('Close > EMA | Close < EMA')
if 'MACD' in list_columns:
    signal_conditions.append('MACD crossup 0 | MACD crossdown 0')
if 'DMI' in list_columns:
    signal_conditions.append('DIP crossup DIN | DIP crossdown DIN')
current_condition = st.selectbox('Saved Condition',signal_conditions)

with st.expander('Custom Expression'):
    text_expression = st.text_area('Signal Expression (buy condition | sell condition)',current_condition)

btn_preview_for_one_stock = st.button('Preview for one stock')
if btn_preview_for_one_stock:
    exp=Expression(text_expression,pd.read_csv(any_file_with_indicators))
    exp.eval()