import streamlit as st
import pandas as pd
from irpr import *
import myenv
import importlib
importlib.reload(myenv)


df = pd.read_csv("data/data.csv")
ldf = pd.read_csv("data/ldata.csv")

st.set_page_config(
    page_title="Interest Rate Probability | US Federal Reserve", layout="wide",
)
st.title("Interest Rate Probability | US Federal Reserve")
# st.table(get_table(ldf))
st.write(get_table(ldf).to_html(escape=False, index=False), unsafe_allow_html=True)
st.caption(myenv.datetime_text)

dates = sorted(ldf["GV1_DATE"].unique())
figs = [get_prob_line_by_date(df, d)[0] for d in dates[:4]]
fig_line = get_expected_line(df)
st.plotly_chart(fig_line)

col1, col2 = st.columns(2)
col1.plotly_chart(figs[0])
col2.plotly_chart(figs[1])
col1, col2 = st.columns(2)
col1.plotly_chart(figs[2])
col2.plotly_chart(figs[3])
