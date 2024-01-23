import streamlit as st
import pandas as pd
from st_pages import show_pages_from_config
import matplotlib.pyplot as plt
import os

def testback_data(buy_signals,initial_cash = 1000000):
    # 创建回测结果的数据框
    backtest = pd.DataFrame(columns=['index', 'Close', 'Signal', 'Position', 'Equity'])

    # 初始化回测参数
    # initial_cash = 1000000  # 初始资金
    position = "Hold"     # 当前仓位，默认为持仓
    equity = initial_cash  # 初始资产等于初始资金
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
            upper_limit = close + 1.5*std
            lower_limit = close - 1*std
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

        # 将回测结果添加到数据框中
        # We need to assure dataframes are both non-empty when using pd.concat() in new version
        backtest_row = pd.DataFrame({'index': date, 'Close': close, 'Signal': signal, 'Position': position, 'Equity': equity}, index=[0])
        # if both DataFrames non empty
        backtest = backtest.copy() if backtest_row.empty else backtest_row.copy() if backtest.empty else pd.concat([backtest, backtest_row])
    return backtest



from io import BytesIO
def testback_diagram(buy_signals, backtest):
    # 创建一个新的图表
    plt.figure(figsize=(10, 6))

    # 绘制股票走势
    plt.plot(buy_signals['日期'], buy_signals['收盘'], label='股票走势', color='blue')

    # 标记买入点和卖出点
    buy_points = backtest[backtest['Position'] == 'buy']
    sell_points = backtest[backtest['Position'] == 'sell']

    plt.scatter(buy_points['index'], buy_points['Close'], marker='^', color='green', label='买入点')
    plt.scatter(sell_points['index'], sell_points['Close'], marker='v', color='red', label='卖出点')

    # 添加标签和标题
    plt.xlabel('日期')
    plt.ylabel('股价')
    plt.title('股票走势和交易信号')
    plt.legend()

    # 将图表保存到 BytesIO 对象中
    buffer = BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    return buffer



# Show pages
show_pages_from_config()

'#### Testback'
stock_set_name = st.selectbox('Stock Set', tuple(os.listdir('signals')))

signal_set_name = st.selectbox('Signal Set', tuple(os.listdir(f'signals/{stock_set_name}')))

any_signals_file = f'signals/{stock_set_name}/{signal_set_name}/' + os.listdir(f'signals/{stock_set_name}/{signal_set_name}')[0]

btn_preview_for_one_stock = st.button('Preview for one stock')
if btn_preview_for_one_stock:
    tb=testback_data(pd.read_csv(any_signals_file),initial_cash=1000000)
    st.dataframe(tb,use_container_width=True)
    st.image(testback_diagram(pd.read_csv(any_signals_file), tb), caption='回测图表', use_column_width=True)

# Similar part as the ui_indicators.py
if st.button('Calculate for the set',type='primary',disabled=not btn_preview_for_one_stock):
    prg_testback = st.progress(0.0, text='Checking folder existency...')
    if not os.path.exists(f'testback/{stock_set_name}/{signal_set_name}'):
        os.makedirs(f'testback/{stock_set_name}/{signal_set_name}')
    #  To every file, do testback
    i=0.0
    for file in os.listdir(f'signals/{stock_set_name}/{signal_set_name}'):
        i += 1
        prg = i / len(os.listdir(f'signals/{stock_set_name}/{signal_set_name}'))
        prg_testback.progress(prg,'Doing testback...')
        source_path = f'signals/{stock_set_name}/{signal_set_name}/{file}'
        target_path = f'testback/{stock_set_name}/{signal_set_name}/{file}'
        tb=testback_data(pd.read_csv(source_path),initial_cash=1000000)
        tb.to_csv(target_path,index=False)
    prg_testback.progress(1.0,'Finished')
