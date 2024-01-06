import streamlit as st
import numpy as np
    import pandas as pd
    import matplotlib.pyplot as plt
    import os
    # import efinance as ef
    # from st_pages import show_pages_from_config, add_page_title
def run_app():
    # Specify what pages should be shown in the sidebar, and what their titles and icons
    # should be
    # show_pages_from_config()
    # Using object notation
    add_selectbox = st.sidebar.selectbox(
        "How would you like to be contacted?",
        ("Email", "Home phone", "Mobile phone")
    )

    # Using "with" notation
    with st.sidebar:
        add_radio = st.radio(
            "Choose a shipping method",
            ("Standard (5-15 days)", "Express (2-5 days)")
        )
    # 展示文本；文本直接使用Markdown语法
    st.markdown("# Streamlit示例")
    st.markdown("""
                - 这是
                - 一个
                - 无序列表
                """)



    # 展示pandas数据框
    st.dataframe(pd.DataFrame([[1, 2], [3, 4]], columns=["a", "b"]))

    # 展示matplotlib绘图
    arr = np.random.normal(1, 1, size=100)
    plt.hist(arr, bins=20)
    plt.title("matplotlib plot")
    st.pyplot()

    # 加入交互控件，如输入框
    number = st.number_input("Insert a number", 123)
    st.write("输入的数字是：", number)
if __name__ == '__main__':
    pass