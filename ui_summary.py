import streamlit as st
import pandas as pd
from st_pages import show_pages_from_config
import os

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
    win_rate = sum([x > 0 for x in diff_list]) / len(diff_list) if len(diff_list)!=0 else None

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
    return pd.DataFrame({
        'ID':id,
        'alldays':len(backtest_results),
        'times':len(diff_list),
        'win_rate':win_rate,
        'total_returns':total_returns,
        'annual_returns':annual_returns
    },index=[0])


# Show pages
show_pages_from_config()

'#### Summary'
stock_set_name = st.selectbox('Stock Set', tuple(os.listdir(f'users/{st.session_state["username"]}/testback')))

signal_set_name = st.selectbox('Signal Set', tuple(os.listdir(f'users/{st.session_state["username"]}/testback/{stock_set_name}')))

if signal_set_name:
    any_testback_file = f'users/{st.session_state["username"]}/testback/{stock_set_name}/{signal_set_name}/' + os.listdir(f'users/{st.session_state["username"]}/testback/{stock_set_name}/{signal_set_name}')[0]

btn_preview_for_one_stock = st.button('Preview for one stock')
if btn_preview_for_one_stock:
    summary=result(pd.read_csv(any_testback_file),id=os.listdir(f'users/{st.session_state["username"]}/testback/{stock_set_name}/{signal_set_name}')[0],initial_cash=1000000)
    st.dataframe(summary,use_container_width=True)

# Very similar part as the ui_testback.py
if st.button('Calculate for the set',type='primary',disabled=not btn_preview_for_one_stock):
    prg_summary = st.progress(0.0, text='Checking folder existency...')
    if not os.path.exists(f'users/{st.session_state["username"]}/summary/{stock_set_name}'):
        os.makedirs(f'users/{st.session_state["username"]}/summary/{stock_set_name}')
    #  To every folder, do summary
    i=0.0
    summary=pd.DataFrame(columns=['ID','alldays', 'times', 'win_rate', 'total_returns', 'annual_returns'])
    for file in os.listdir(f'users/{st.session_state["username"]}/testback/{stock_set_name}/{signal_set_name}'):
        i += 1
        prg = i / len(os.listdir(f'users/{st.session_state["username"]}/testback/{stock_set_name}/{signal_set_name}'))
        prg_summary.progress(prg,'Doing summary...')
        source_path = f'users/{st.session_state["username"]}/testback/{stock_set_name}/{signal_set_name}/{file}'
        target_path = f'users/{st.session_state["username"]}/summary/{stock_set_name}/{signal_set_name}.csv'
        res=result(pd.read_csv(source_path),id=file,initial_cash=1000000)
        summary = summary.copy() if res.empty else res.copy() if summary.empty else pd.concat([summary, res])
        summary.to_csv(target_path,index=False)
    prg_summary.progress(1.0,'Finished')
