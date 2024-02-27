import pandas as pd
import streamlit as st
import streamlit_authenticator as stauth
import os
import yaml

from yaml.loader import SafeLoader
from pyecharts import options as opts
from pyecharts.charts import Line, Scatter

from strategy_tools import *










class NewPage:
    """
    这个类初始化时会为当前页面增加登入系统，且在用户首次登入成功后增加用户文件夹.
    """
    def __init__(self,showPageFunction,key=""):
        """
        ## Parameters
        - showPageFunction: 这个函数包括streamlit的该页面布局
        - key: 对于不同页面，应使用不同的key，使得一些元素的key随着页面key改变
        """
        # 加载认证配置文件
        with open('stauth.yaml') as f:
            config = yaml.load(f, Loader=SafeLoader)

        # 初始化认证器
        authenticator = stauth.Authenticate(
            config['credentials'],
            config['cookie']['name'],
            config['cookie']['key'],
            config['cookie']['expiry_days'],
            config['preauthorized']
        )
        # 渲染登录界面并处理登录逻辑
        if 'authentication_status' not in st.session_state:
            st.session_state['authentication_status'] = None

        if st.session_state['authentication_status'] is not True:
            authenticator.login('Login', 'main')

        # 根据认证状态显示内容
        if st.session_state["authentication_status"] is True:
            # 初始化用户文件夹
            for folder in ['source', 'applied_indicators', 'signals', 'testback', 'summary']:
                if not os.path.exists(f'users/{st.session_state["username"]}/{folder}/default_set'):
                    os.makedirs(f'users/{st.session_state["username"]}/{folder}/default_set')

            showPageFunction()

            with st.sidebar:
                # 登出部分
                # authenticator.logout('Logout', 'main', key=key+'logout_button')
                pass

        elif st.session_state["authentication_status"] is False:
            st.error('Username/password is incorrect')
        elif st.session_state["authentication_status"] is None:
            st.warning('Please enter your username and password')









def getDataframe(market: str, stock: str, strategy: str, stop_loss: int, take_profit: int, date_interval: tuple[str, str]|bool,doTestback:bool=True) -> tuple[pd.DataFrame, pd.DataFrame]:
    """
    - 获取当前需要的Dataframe.（基础版本，没有缓存修饰器）
    - 返回(df,testback_result).
    - 返回的df带有 标准差 平均值 以及选择的策略需要的指标列.
    - 返回的testback_result带有 ID alldays times win_rate total_returns annual_returns 列.
    ## Parameters
    - market: 市场
    - stock: 股票
    - strategy: 策略
    - stop_loss: 止损倍率
    - take_profit: 止盈倍率
    - date_interval: 时间段，若为False，则不过滤时间
    - doTestBack: 是否返回回测数据，若为False，仅返回Dataframe类型的df而非tuple
    """
    df = pd.read_csv(f'public_source/{market}/{stock}')
    df['日期'] = pd.to_datetime(df['日期'])

    if date_interval!=False:
        start_date, end_date = date_interval
        start_date = pd.to_datetime(start_date)
        end_date = pd.to_datetime(end_date)
        # print(start_date,end_date)
        df = df[(df['日期'] >= start_date) & (df['日期'] <= end_date)].reset_index(drop=True)
        # st.write(pd.to_datetime(df['日期']))

    if doTestback:
        df['STD'] = df['收盘'].rolling(50).std()
        df['MA'] = df['收盘'].rolling(50).mean()

    exp = apply_strategy(strategy, df)

    if doTestback:
        Signals = exp.eval()
        TestBack = testback_data(Signals,stop_loss,take_profit).iloc[:,1:]
        TestBack = TestBack.reset_index(drop=True)

        # concat(df,TestBack)
        df = df.copy() if TestBack.empty else TestBack.copy(
        ) if df.empty else pd.concat([df, TestBack], axis=1)

        testback_result = result(TestBack)
        return df, testback_result
    else:
        return df








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
            'annual_returns':0,
            'total_return_premium': 0,
            'annual_return_premium': 0,

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
    stock_total_return = (backtest_results['Close'].iloc[-1] - backtest_results['Close'].iloc[0])/backtest_results['Close'].iloc[0]
    total_premium_return = total_returns - stock_total_return
    annual_premium_return = (total_premium_return+1) ** (1/(len(backtest_results)/252))-1


    return pd.DataFrame({
        'ID':id,
        'alldays':len(backtest_results),
        'times':len(diff_list),
        'win_rate':win_rate,
        'total_returns': total_returns,
        'annual_returns': annual_returns,
        'total_return_premium': total_premium_return,
        'annual_return_premium': annual_premium_return
    },dtype='float',index=['result'])


def graph_buy_sell_points(df:pd.DataFrame)->Line:
    """
    用于显示买卖点显示图.
    读取一个有 日期 收盘 Position 列的dataframe，返回一个可以被st_pyecharts显示的Line对象.
    ## Parameters
    - df: dataframe
    """
    # 创建折线图对象
    line = Line()

    # 添加收盘价数据
    line.add_xaxis(df['日期'].tolist())
    line.add_yaxis("Price", df['收盘'].tolist())

    # 创建散点图数据
    scatter = Scatter()
    # 添加买卖点
    buy_points = df[df['Position'] == 'buy']
    sell_points = df[df['Position'] == 'sell']

    scatter.add_xaxis(buy_points['日期'].tolist())
    scatter.add_yaxis("Buy", buy_points['收盘'].tolist(), symbol="triangle", symbol_size=5, label_opts=opts.LabelOpts(is_show=False))

    scatter.add_xaxis(sell_points['日期'].tolist())
    scatter.add_yaxis("Sell", sell_points['收盘'].tolist(), symbol="diamond", symbol_size=5,  label_opts=opts.LabelOpts(is_show=False))

    line.overlap(scatter)

    # 设置标题、标签等
    line.set_global_opts(
        #title_opts=opts.TitleOpts(title="Buy and Sell Points"),
        xaxis_opts=opts.AxisOpts(name="Date"),
        yaxis_opts=opts.AxisOpts(name="Close Price"),
        legend_opts=opts.LegendOpts(orient="horizontal", pos_top="bottom"),
        tooltip_opts=opts.TooltipOpts(trigger="axis"),
        toolbox_opts=opts.ToolboxOpts(
            is_show=True,
            orient="vertical",
            pos_right="5%",
            pos_top="15%",
            feature={
                "dataZoom": {"yAxisIndex": "none"},
                "restore": {},
            },
        ),
    )
    # 在Streamlit页面上显示图表
    return line







def graph_value_over_time(df):
    """
    用于显示 收盘价-时间 折线图.
    读取一个有 日期 收盘 Value 列的dataframe，返回一个可以被st_pyecharts显示的Line对象.
    ## Parameters
    - df: dataframe
    """
    plotframe = pd.DataFrame({
        '日期':df['日期'],
        'Total Price Return':(df['收盘']/df['收盘'].iloc[0]-1)*100,
        'Total Strategy Return':(df['Value']/df['Value'].iloc[0]-1)*100
        })

    # 创建折线图对象
    line = Line()

    # 添加收盘价曲线数据
    line.add_xaxis(plotframe['日期'].tolist())
    line.add_yaxis("Stock Return(%)", plotframe['Total Price Return'].tolist(), symbol="circle", symbol_size=8)

    # 添加价值变化曲线数据
    line.add_yaxis("Strategy Return(%)", plotframe['Total Strategy Return'].tolist(), symbol="circle", symbol_size=8)

    # 设置标题、标签等
    line.set_global_opts(
        #title_opts=opts.TitleOpts(title="Price and Value Over Time"),
        xaxis_opts=opts.AxisOpts(name="Date"),
        yaxis_opts=opts.AxisOpts(name="Total Return(%)", axislabel_opts=opts.LabelOpts(formatter="{value}")),
        legend_opts=opts.LegendOpts(orient="horizontal", pos_top="bottom"),
        tooltip_opts=opts.TooltipOpts(trigger="axis"),
        toolbox_opts=opts.ToolboxOpts(
            is_show=True,
            orient="vertical",
            pos_right="5%",
            pos_top="15%",
            feature={
                "dataZoom": {"yAxisIndex": "none"},
                "restore": {},
            },
        ),
    )
    # 在Streamlit页面上显示图表
    return line









