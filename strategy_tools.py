import talib as tal
import pandas as pd
import numpy as np

class Expression:
    """
    - 用来创建一个策略表达式.
    """
    def __init__(self,s:str,data:pd.DataFrame):
        '''
        ## Parameters
        - s: A sequence of dataframes and operators, splited in one space.
        - data: the dataframe.
        ## Examples
        #### exp=Expression('MACD < 0 | MACD > 0',df) \n
        - Meaning the buy condition is MACD < 0, sell condition is MACD > 0.
        - The dataframe df should have 'MACD' column.
        - Precedences of tokens: | or and OR AND > crossup + * **.
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
        # st.write(self.tokens)

    def doOp(self):
        op = self.symbols_stack.pop()
        y = self.values_stack.pop()
        x = self.values_stack.pop()
        # ('==============\n==============',op,y,x,sep='\n')
        # First deal with them as 'buy' signals, then change the signals to 'sell' when operating '|'
        if op == '|':
            # st.write(x)
            # st.write(y)
            y=np.where(y=='buy','sell',None)
            x=pd.DataFrame({'signals':x})
            y=pd.DataFrame({'signals':y})
            signals=x.combine_first(y)
            # st.write(signals)
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
    def eval(self)->pd.DataFrame:
        """
        返回一个包括 日期 收盘 signals 三列的dataframe.
        """
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
        # st.write(self.values_stack[-1])
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












ALL_STRATEGIES = ['SMA', 'MACD','AROON', 'RSI', 'BOLLING','KDJ','DMI','ROC','SMI', 'WPR', 'SAR','CCI', 'OBV']
"""
Strategies added here will be able to be selected
"""

def apply_strategy(strategy:str, df:pd.DataFrame)->Expression:
    """
    这个函数为输入的dataframe增加对应的指标，以及返回其判断规则
    ## Parameters
    - strategy: 指标
    - df: 单股票数据 
    """
    if strategy == 'MACD':
        _, df["MACD_SIG"], df["MACD_HIST"] = tal.MACD(df['收盘'], 12, 26, 9)
        # 买入条件：MACD线向上穿过MACD信号线
        # 卖出条件：MACD线向下穿过MACD信号线
        exp = Expression(
            'MACD_HIST crossup MACD_SIG | MACD_HIST crossdown MACD_SIG', df)
    elif strategy == 'SMA':
        df["SMA10"] = tal.SMA(df["收盘"], 10)
        df["SMA20"] = tal.SMA(df["收盘"], 20)
        df["SMA50"] = tal.SMA(df["收盘"], 50)
        # 买入条件：(SMA10向上穿过SMA20 且 SMA20>=SMA50) 或 (SMA20向上穿过SMA50 且 SMA10>=SMA20)
        # 卖出条件：(SMA10向上穿过SMA20 且 SMA20>=SMA50) 或 (SMA20向上穿过SMA50 且 SMA10>=SMA20)
        exp = Expression(
            'SMA10 crossup SMA20 AND SMA20 >= SMA50 or SMA20 crossup SMA50 AND SMA10 >= SMA20 | SMA10 crossdown SMA20 AND SMA20 <= SMA50 or SMA20 crossdown SMA50 AND SMA10 <= SMA20', df)
    elif strategy=='AROON':
        Aroon(df)
        exp = Expression('Aroon_Up > 70 and Aroon_Down < 30 | Aroon_Up < 30 and Aroon_Down > 70', df)
    elif strategy=='RSI':
        df["RSI"] = tal.RSI(df['收盘'], timeperiod=14)
        #买入条件：RSI小于30
        #卖出：大于70
        exp = Expression('RSI < 30 | RSI >70',df)
    elif strategy=='BOLLING':
        df['upper_band'], df['middle_band'], df['lower_band'] = tal.BBANDS(df['收盘'], timeperiod=14, nbdevup=2, nbdevdn=2)
        # 如果收盘价上穿 BOLL 上轨，则买入 ; 如果收盘价下穿 BOLL 下轨，则开盘卖掉
        exp = Expression('收盘 crossup upper_band | 收盘 crossdown lower_band', df)
    elif strategy=='KDJ':
        df['KLine'], df['DLine'] = tal.STOCH(df["最高"], df["最低"], df["收盘"], fastk_period=9, slowk_period=5, slowk_matype=1, slowd_period=5, slowd_matype=1)
        df['JLine'] = 3 * df['KLine'] - 2 * df['DLine']
        # 买入条件：K线向上穿过D线
        # 卖出条件：K线向下穿过D线
        exp = Expression('KLine crossup DLine | KLine crossdown DLine', df)
    elif strategy=='DMI':
        df['plus_di'] = tal.PLUS_DI(df['最高'], df['最低'], df['收盘'], timeperiod=14)
        df['minus_di'] = tal.MINUS_DI(df['最高'], df['最低'], df['收盘'], timeperiod=14)
        # 当+DI高于-DI时，如果报价的上升(或下降)趋势非常明显，则发出买入信号；当+DI低于-DI时，发出卖出信号。
        exp = Expression('plus_di crossup minus_di | plus_di crossdown minus_di', df)
    elif strategy =='ROC':
        df['ROC'] = tal.ROC(df['收盘'], timeperiod=14)
        # 当ROC指标大于0时买入，小于0时卖出。
        exp = Expression('ROC > 0 | ROC < 0', df)
    elif strategy == 'SMI':
        SMI(df)
        # 当SMI线从下方向上穿过信号线时，表示买入信号。当SMI线从上方向下穿过信号线时，表示卖出信号。
        exp = Expression('SMI crossup signal_line | SMI crossdown signal_line', df)
    elif strategy == 'WPR':
        df['WPR'] = (tal.WILLR(df['最高'], df['最低'], df['收盘'], timeperiod=14)) * (-1)
        # 翻转数值成正数
        # -80%以下判斷為超賣，-20%以上判斷為超買
        exp = Expression('WPR > 80 | WPR < 20', df)
    elif strategy == 'SAR':
        # SAR 止盈 止损类指标
        df['SAR'] = tal.SAR(df['最高'], df['最低'], acceleration=0.02, maximum=0.2)
        df['yesterdayclose'] = df['收盘'].shift(1).fillna(0)
        #股价曲线由下向上突破SAR曲线时，为买进讯号。股价曲线由下向上突破SAR曲线时，为买进讯号。反之卖出
        exp = Expression('yesterdayclose < 收盘 and 收盘 crossup SAR | yesterdayclose > 收盘 and 收盘 crossdown SAR', df)
    elif strategy == 'CCI':
        df['TP'] = (df['最高']+df['最低']+df['收盘'])/3
        df['MA'] = df['TP'].rolling(window=20).mean()
        df['MD'] = df['TP'].rolling(window=20).std()
        df['CCI'] = (df['TP']-df['MA'])/(df['MD']*0.015)
        df['CCIyesterday'] = df['CCI'].shift(1).fillna(0)
        #这里只捕捉了超买的非正常区间，大于100 超买，也买入，直到看到下降趋势
        exp = Expression('CCI > 100 | CCI < CCIyesterday',df)
    elif strategy =='OBV':
        # 使用 TA-Lib 库的 OBV 函数来计算 OBV 指标
        df['OBV'] = tal.OBV(df['收盘'], df['成交量'])
        df['OBV_lag1'] = df['OBV'].shift(1).fillna(0)
        df['OBV_lag2'] = df['OBV'].shift(2).fillna(0)
        df['OBV_lag3'] = df['OBV'].shift(3).fillna(0)
        df['OBV_lag4'] = df['OBV'].shift(4).fillna(0)
        df['close_lag1'] = df['收盘'].shift(1).fillna(0)
        df['close_lag2'] = df['收盘'].shift(2).fillna(0)
        df['close_lag3'] = df['收盘'].shift(3).fillna(0)
        df['close_lag4'] = df['收盘'].shift(4).fillna(0)
        # obv 与 股价连续五天上涨，买入；连续五天下跌，卖出
        exp = Expression('OBV > OBV_lag1 and OBV_lag1 > OBV_lag2 and OBV_lag2 > OBV_lag3 and OBV_lag3 > OBV_lag4 and \
                         收盘 > close_lag1 and close_lag1 > close_lag2 and close_lag2 > close_lag3 and close_lag3 > close_lag4 \
                          | OBV < OBV_lag1 and OBV_lag1 < OBV_lag2 and OBV_lag2 < OBV_lag3 and OBV_lag3 < OBV_lag4 and \
                         收盘 < close_lag1 and close_lag1 < close_lag2 and close_lag2 < close_lag3 and close_lag3 < close_lag4',df)



    return exp


# Extend Indicators

def Aroon(stockdata, window=25):
    # 计算Aroon Up和Aroon Down
    stockdata['Aroon_Up'] = (stockdata['最高'].rolling(window=window).apply(lambda x: x.argmax(), raw=True)+1) / window * 100
    stockdata['Aroon_Down'] =(stockdata['最低'].rolling(window=window).apply(lambda x: x.argmin(), raw=True)+1) / window * 100



def SMI(stockdata, period=14, ema_period=3, signal_period=5):
    # 计算动量值
    stockdata['momentum'] = tal.MOM(stockdata['收盘'], timeperiod=period)
    # 计算动量值的移动平均
    stockdata['momentum_ema'] = tal.EMA(stockdata['momentum'], timeperiod=ema_period)
    # 计算SMI线
    stockdata['SMI'] = stockdata['momentum'] - stockdata['momentum_ema']
    # 计算SMI的信号线
    stockdata['signal_line'] = tal.EMA(stockdata['SMI'], timeperiod=signal_period)
















