import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import streamlit as st

class Expression:
    def __init__(self,s:str,data:pd.DataFrame):
        '''
        ## Parameters
        - s: A sequence of dataframes and operators, splited in one space.
        - data: the dataframe.
        - Precedences of tokens: | or and OR AND > crossup + * **
        ## Examples
        #### exp=Expression('MACD < 0 | MACD > 0',df) \n
        - Meaning the buy condition is MACD < 0, sell condition is MACD > 0.
        - The dataframe df should have 'MACD' column.
        - Use Signals=exp.eval() for getting the result.
        '''
        self.data=data
        self.tokens:list[str|pd.DataFrame]=[]
        self.values_stack:list[pd.DataFrame]=[]
        self.symbols_stack:list[str]=[]
        self.precedences={
            '$':0,
            '|':1,
            'or':2,
            'and':3,
            'OR':4,
            'AND':5,
            '>':6,
            '<':6,
            '>=':6,
            '<=':6,
            '==':6,
            'crossup':7,
            'crossdown':7,
            '+':8,
            '-':8,
            '*':9,
            '/':9,
            '**':10
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
                en_support={
                    'Date':'日期',
                    'Open':'开盘',
                    'Close':'收盘',
                    'High':'最高',
                    'Low':'最低'
                }
                if token in en_support:
                    self.tokens.append(data[en_support[token]])
                else:
                    print('Invalid Expression')
        st.write(self.tokens)

    def doOp(self):
        op = self.symbols_stack.pop()
        y = self.values_stack.pop()
        x = self.values_stack.pop()
        # ('==============\n==============',op,y,x,sep='\n')
        # First deal with them as 'buy' signals, then change the signals to 'sell' when operating '|'
        if op == '|':
            st.write(x)
            st.write(y)
            y=np.where(y=='buy','sell',None)
            x=pd.DataFrame({'signals':x})
            y=pd.DataFrame({'signals':y})
            signals=x.combine_first(y)
            st.write(signals)
            self.values_stack.append(signals)
        elif op == 'and' or op == 'AND':
            signals=x.where(x==y,None)
            self.values_stack.append(signals)
        elif op == 'or' or op== 'OR':
            signals=np.where(x=='buy',True,False) | np.where(y=='buy',True,False)
            signals=np.where(signals,'buy',None)
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
        elif op=='+':
            self.values_stack.append(x+y)
        elif op=='-':
            self.values_stack.append(x-y)
        elif op=='*':
            self.values_stack.append(x*y)
        elif op=='/':
            self.values_stack.append(x/y)
        elif op=='**':
            self.values_stack.append(x**y)
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
        st.write(self.values_stack[-1])
        self.values_stack[-1] = pd.DataFrame({'日期':self.data['日期'],'收盘':self.data['收盘'],'signals':self.values_stack[-1]['signals']})
        
        if 'STD' in self.data:
            self.values_stack[-1]['STD']=self.data['STD']
        if 'MA' in self.data:
            self.values_stack[-1]['MA']=self.data['MA']
        # st.write(self.values_stack)
        # st.write(self.symbols_stack)
        if not (len(self.values_stack)==1 and len(self.symbols_stack)==0):
            print('Something Wrong of calculating signals')
        
        return self.values_stack[-1]

def testback_data(buy_signals,stop_loss=1,take_profit=2,initial_cash = 1000000):
   
    # 创建回测结果的数据框
    backtest = pd.DataFrame(columns=['index', 'Close', 'Signal', 'Position', 'Equity', 'Value'])

    # 初始化回测参数
    # initial_cash = 1000000  # 初始资金
    position = "Hold"     # 当前仓位，默认为持仓
    equity = initial_cash  # 初始资产等于初始资金
    value = initial_cash
    shares = 0
    st = "hold"
    upper_limit = 9999999
    lower_limit = 0
    std = 0
    # moving_ave = 0

    # 遍历每一行买入信号数据
    for i, row in buy_signals.iterrows():
        date = row['日期']
        close = row['收盘']
        signal = row['signals']
        std = row['STD']

        # avoid divided by 0 problem
        if close==0.0:
            continue
        # if signal > 0.5 and st != 'buy':
        if signal == 'buy' and st != 'buy':
            # 买入操作
            st = 'buy'
            position = 'buy'
            shares += equity / close  # 计算可买入的股票数量
            equity = 0  # 资金置为0，全仓买入
            upper_limit = close + take_profit*std
            lower_limit = close - stop_loss*std
        # elif signal < 0.5 and st != 'sell':
        elif signal == 'sell' and st != 'sell':
            # 卖出操作
            position = 'sell'
            st = 'sell'
            equity += shares * close
            shares = 0  # 持有股票数量置为0
        elif close > upper_limit and st != 'sell' or close < lower_limit and st != 'sell':
            # 卖出操作
            position = 'sell'
            st = 'sell'
            equity += shares * close
            shares = 0  # 持有股票数量置为0
        else:
            position = ""
            equity = equity
            shares = shares
        value = shares *close + equity
        # 将回测结果添加到数据框中
        # We need to assure dataframes are both non-empty when using pd.concat() in new version
        backtest_row = pd.DataFrame({'index': date, 'Close': close, 'Signal': signal, 'Position': position, 'Equity': equity,'Value':value}, index=[0])
        # if both DataFrames non empty
        backtest = backtest.copy() if backtest_row.empty else backtest_row.copy() if backtest.empty else pd.concat([backtest, backtest_row])
    return backtest

def result(backtest_results,id=None,initial_cash=1000000):
    # Avoid empty dataframes
    if backtest_results.shape[0]==0:
        return pd.DataFrame({
            'ID':id,
            'alldays':0,
            'times':0,
            'win_rate':0,
            'total_returns':0,
            'annual_returns':0
        },index=[0])
    col_list = list(backtest_results['Equity'][backtest_results['Equity'] != 0])
    col_list = [float(x) for x in col_list]
    clean_list = [col_list[0]] + [col_list[i] for i in range(1, len(col_list)) if col_list[i] != col_list[i-1]]
    diff_list = [clean_list[i+1] - clean_list[i] for i in range(len(clean_list)-1)]
    if len(diff_list)!=0:
        win_rate = sum([x > 0 for x in diff_list]) / len(diff_list)
    else:
        win_rate = 0

    equity_series = backtest_results['Equity']
    last_equity = equity_series.iloc[-1]

    if last_equity == 0:
        # 循环向前查找直到找到一个非零值
        for i in range(len(equity_series) - 2, -1, -1):
            if equity_series.iloc[i] != 0:
                last_equity = equity_series.iloc[i]
                break

    total_returns = (last_equity - initial_cash) / initial_cash
    annual_returns = (total_returns+1) ** (1/(len(backtest_results)/252))-1

    # 换成百分号形式
    total_returns_percent = round(total_returns * 100, 2)
    annual_returns_percent = round(annual_returns * 100, 2)

    return pd.DataFrame({
        'ID':id,
        'alldays':len(backtest_results),
        'times':len(diff_list),
        'win_rate':win_rate,
        'total_returns': f"{total_returns_percent:.2f}%",
        'annual_returns': f"{annual_returns_percent:.2f}%"
    },index=[0])

def plot_buy_sell_points(df):
    # 绘制折线图
    plt.figure(figsize=(35, 15))
    plt.plot(df['日期'], df['收盘'], label='Price')

    # 标注买卖点
    buy_points = df[df['Position'] == 'buy']
    sell_points = df[df['Position'] == 'sell']

    plt.scatter(buy_points['日期'], buy_points['收盘'], color='green', label='Buy', marker='^', s=50)
    plt.scatter(sell_points['日期'], sell_points['收盘'], color='red', label='Sell', marker='v', s=50)

    # 添加标题、标签等
    plt.title('Buy and Sell Points')
    plt.xlabel('Date')
    plt.ylabel('Close Price')
    plt.legend()
    plt.grid(True)

    # 在Streamlit页面上显示图表 
    st.pyplot(plt,use_container_width=True)

def plot_value_over_time(df):
    # 创建 Matplotlib 图表
    fig, ax1 = plt.subplots(figsize=(35, 15))

    # 绘制收盘价曲线
    ax1.plot(df['日期'], df['收盘'], label='Price')

    # 创建第二个 y 轴用于绘制价值变化曲线
    ax2 = ax1.twinx()
    ax2.plot(df['日期'], df['Value'], label='Value', color='orange')

    # 设置标题、标签等
    ax1.set_title('Price and Value Over Time')
    ax1.set_xlabel('Date')
    ax1.set_ylabel('Closing Price', color='blue')
    ax2.set_ylabel('Portfolio Value', color='orange')

    # 显示图例
    ax1.legend(loc='upper left')
    ax2.legend(loc='upper right')

    # 显示网格
    ax1.grid(True)

    # 在 Streamlit 页面上显示图表
    st.pyplot(fig, use_container_width=True)


