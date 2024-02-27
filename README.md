# StrategyNova

## Using Python 3.10

## With libraries

- numpy==1.24.3
- pandas==2.1.4
- TA-Lib==0.4.24
- efinance==0.5.0 (edited for compating with streamlit)
- streamlit==1.30.0
- st_pages==0.4.5
- streamlit-authenticator==0.2.3
- matplotlib==3.8.2

## Origin data format (from efinance)

- 股票名称,股票代码,日期,开盘,收盘,最高,最低,成交量,成交额,振幅,涨跌幅,涨跌额,换手率
- 苹果,AAPL,2000-01-03,-6.81,-6.75,-6.75,-6.84,19144400,0.0,-1.32,1.17,0.08,0.12
- 苹果,AAPL,2000-01-04,-6.78,-6.83,-6.76,-6.85,18310000,0.0,-1.33,-1.19,-0.08,0.12

## Structure

- home.py: Home page.
- analysis.py: Analysis page.
- monitor.py: Monitor page.
- strategy_tools.py: Including all the calculation and signal-decision-methods about strategies.**(Add more strategies here)**
- self_tools.py: Including other useful functions and classes.

## Contributors

- Caion
-
-
```
  _____ _____ ____ _____ 
 |_   _| ____/ ___|_   _|
   | | |  _| \___ \ | |  
   | | | |___ ___) || |  
   |_| |_____|____/ |_|  
```
                         