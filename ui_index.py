import streamlit as st
import pandas as pd
from st_pages import show_pages_from_config
import os
from shutil import rmtree

for folder in ['source/default_set','applied_indicators/default_set','signals/default_set','testback/default_set','summary/default_set']:
    if not os.path.exists(folder):
        os.makedirs(folder)

# Show pages
show_pages_from_config()

'**This is an experimental ui for strategy research**'
'**Find different pages on the sidebar \:D**'
'---'

tab_view_source,tab_clear_folder= st.tabs(['View Source', 'Clear Folder'])
with tab_view_source:
    current_view = st.selectbox('Stock Set', tuple(os.listdir('source')),placeholder='default_set')
    list_source = os.listdir(f'source/{current_view}')
    view_data = pd.DataFrame({
        'stock_file':list_source,
        'shape':[pd.read_csv(f'source/{current_view}/{file}').shape for file in list_source]
                            })
    st.dataframe(view_data,use_container_width=True)

with tab_clear_folder:
    exist_folders=set(['applied_indicators','signals','testback','source','summary']).intersection(set(os.listdir('./')))
    st.write(set(['applied_indicators','signals','testback','source','summary']))
    st.write(set(os.listdir('./')))
    option = st.selectbox('Choose the folder you want to clear...',exist_folders)
    clear_selected_folders_1 = st.button('CLEAR SELECTED FOLDERS?',type='secondary',key='clear_selected_folders_1')
    if st.button('CLEAR SELECTED FOLDERS!',type='primary',key='clear_selected_folders_2',disabled=not clear_selected_folders_1):
        # Avoid misdeletings
        if(len(option)>3):
            rmtree(option)
            st.success(f"Successfully clear '{option}' folder")