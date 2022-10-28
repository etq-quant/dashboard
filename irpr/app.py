import streamlit as st
import pandas as pd
from irpr import *

try:
    df = pd.read_csv('data.csv')
    ldf = pd.read_csv('ldata.csv')
except:
    df = pd.read_csv('irpr/data.csv')
    ldf = pd.read_csv('irpr/ldata.csv')

st.set_page_config(
    page_title="Interest Rate Probability | US Federal Reserve",
    layout="wide",
)
st.title("Interest Rate Probability | US Federal Reserve")


st.table(get_table(ldf))

dates = sorted(df['GV1_DATE'].unique())

figs = [get_prob_line_by_date(df, d)[0] for d in dates[:4]]

fig_line = get_expected_line(df)
st.plotly_chart(fig_line)

col1, col2 = st.columns(2)
col1.plotly_chart(figs[0])
col2.plotly_chart(figs[1])
col1, col2 = st.columns(2)
col1.plotly_chart(figs[2])
col2.plotly_chart(figs[3])
