import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import plotly.express as px
import plotly.graph_objects as go


def get_prob_line_by_date(df, date):
    tdf = df[df["GV1_DATE"] == date].copy()
    tdf = tdf.sort_values("created_at").reset_index(drop=True)

    dates = sorted(tdf["GV1_DATE"].unique())
    labels = dates
    baser = tdf["GEN_VAL3"].iloc[-1] + 0.125
    x_data = np.array(tdf["date"].tolist())
    sdf = tdf[[i for i in tdf.columns if "." in i]].dropna(how="all", axis=1).copy()
    rates = [float(x) for x in sdf.columns]
    y_data = sdf.values.T
    lp = sdf.iloc[-1].dropna().sort_values().reset_index().values.astype(float)
    colors = ["#FF5F1F", "black", "#1ABC9C", "#F70D1A", "#F778A1"]

    fig = go.Figure()

    for i, (r, y) in enumerate(zip(rates, y_data)):
        fig.add_trace(
            go.Scatter(
                x=x_data,
                y=y,
                mode="markers+lines",
                name='<b>{}%</b><i style="font-size: 12;">/{:+}bps</i>'.format(
                    r, int((r - baser) * 100)
                ),
                # name='<b>{}%</b>({:+}bps)'.format(r, int((r-baser)*100)),
                line=dict(color=colors[i % len(colors)], width=2),
                connectgaps=False,
                marker=dict(
                    color=colors[i % len(colors)],
                    size=3,
                    line=dict(color=colors[i % len(colors)], width=2),
                ),
            )
        )

    for i, dd in enumerate(fig.data):
        x, y = dd.x[-1], dd.y[-1]
        if i > 0:
            x1, y1 = fig.data[i - 1].x[-1], fig.data[i - 1].y[-1]
            if abs(y - y1) < 5:
                y = y - 10

        fig.add_scatter(
            x=[x],
            y=[y],
            mode="markers+text",
            text="{:.0f}%".format(dd.y[-1]),
            textfont=dict(color=dd.line.color),
            textposition="top right",
            marker=dict(color=dd.line.color, size=12, opacity=0),
            legendgroup=dd.name,
            showlegend=False,
        )

        fig.add_scatter(
            x=[x],
            y=[y],
            mode="markers+text",
            text=dd.name,
            textfont=dict(color=dd.line.color),
            textposition="middle right",
            marker=dict(color=dd.line.color, size=12, opacity=0),
            legendgroup=dd.name,
            showlegend=False,
        )
        # dot
        fig.add_scatter(
            x=[x],
            y=[dd.y[-1]],
            mode="markers",
            text=dd.name,
            textfont=dict(color=dd.line.color),
            textposition="middle right",
            marker=dict(color=dd.line.color, size=12),
            legendgroup=dd.name,
            showlegend=False,
        )

    fig.update_layout(
        title=dict(
            text="Next Meeting Date: {}".format(
                pd.to_datetime(date).strftime("%d-%b-%Y")
            ),
            font_size=16,
        ),
        width=800,
        height=600,
        xaxis_range=[x_data[0], pd.to_datetime(x_data[-1]).date() + timedelta(3)],
        xaxis=dict(
            autorange=False,
            showline=True,
            showgrid=False,
            showticklabels=True,
            automargin=True,
            linecolor="rgb(204, 204, 204)",
            linewidth=2,
            ticks="outside",
            tickfont=dict(family="Arial", size=12, color="rgb(82, 82, 82)",),
        ),
        yaxis=dict(
            title="Probability",
            gridcolor="#D5D8DC",
            ticksuffix="%",
            tickformat=".0f",
            showgrid=True,
            zeroline=False,
            showline=False,
            showticklabels=True,
        ),
        autosize=True,
        margin=dict(
            autoexpand=True,
            l=150,
            r=10,
            t=110,
            # pad=200,
        ),
        showlegend=True,
        legend=dict(orientation="h", yanchor="top", y=-0.2, xanchor="center", x=0),
        plot_bgcolor="white",
    )

    change = not all(
        tdf[[i for i in tdf.columns if "." in i]].iloc[-2].fillna(0).rank()
        == tdf[[i for i in tdf.columns if "." in i]].iloc[-1].fillna(0).rank()
    )
    fig.layout.xaxis.fixedrange = True
    fig.layout.yaxis.fixedrange = True
    return fig, change, date


def get_expected_line(df):
    a = np.array(sorted(df["date"].unique(), reverse=True))
    df = df[df["date"].isin([a[0], a[6], a[29]])].copy()

    df["created_at"] = pd.to_datetime(df["created_at"])

    df["datehour"] = (
        df["created_at"].dt.date.astype(str)
        + "_"
        + df["created_at"].dt.hour.astype(str).str.zfill(2)
    )
    df["date"] = df["created_at"].dt.date.astype(str)

    fig = go.Figure()

    y_data = df.groupby(["date"])["expected_tp"].apply(list)
    x_data = df.groupby(["date"])["GV1_DATE"].apply(list)
    labels = df["date"].unique().tolist()

    labels = sorted(df["date"].unique())
    colors = ["#728FCE", "#4863A0", "rgb(67,67,67)"]
    mode_size = [4, 8, 12]
    line_size = [2, 3, 4]
    font_size = [8, 12, 16]

    i = 0
    fig.add_trace(
        go.Scatter(
            x=x_data[i],
            y=y_data[i],
            mode="markers+lines",
            marker_symbol="hexagon",
            marker_size=6,
            name="{} (W{}, a month ago)".format(
                datetime.strptime(labels[i], "%Y-%m-%d").strftime("%d-%b-%Y"),
                datetime.strptime(labels[i], "%Y-%m-%d").isocalendar().week,
            ),
            line=dict(color=colors[i], width=line_size[i], dash="dot"),
            connectgaps=True,
        )
    )

    i = 1
    fig.add_trace(
        go.Scatter(
            x=x_data[i],
            y=y_data[i],
            mode="markers+lines",
            marker_symbol="hexagon",
            marker_size=6,
            name="{} (W{}, a week ago)".format(
                datetime.strptime(labels[i], "%Y-%m-%d").strftime("%d-%b-%Y"),
                datetime.strptime(labels[i], "%Y-%m-%d").isocalendar().week,
            ),
            line=dict(color=colors[i], width=line_size[i], dash="dot"),
            connectgaps=True,
        )
    )

    i = 2
    fig.add_trace(
        go.Scatter(
            x=x_data[i],
            y=y_data[i],
            mode="markers+lines",
            marker_symbol="hexagon",
            marker_size=10,
            name="{} (W{}, today)".format(
                datetime.strptime(labels[i], "%Y-%m-%d").strftime("%d-%b-%Y"),
                datetime.strptime(labels[i], "%Y-%m-%d").isocalendar().week,
            ),
            line=dict(color=colors[i], width=line_size[i]),
            connectgaps=True,
        )
    )

    dd = fig.data[i]
    fig.add_scatter(
        x=[dd.x[-1]],
        y=[dd.y[-1]],
        mode="markers+text",
        text="{:.2f}%".format(dd.y[-1]),
        textfont=dict(color=dd.line.color),
        textposition="top right",
        marker=dict(color=dd.line.color, size=10, opacity=0),
        legendgroup=dd.name,
        showlegend=False,
    )

    fig.add_scatter(
        x=[dd.x[-1]],
        y=[dd.y[-1]],
        mode="markers+text",
        text=dd.name,
        textfont=dict(color=dd.line.color),
        textposition="middle right",
        marker=dict(color=dd.line.color, size=10),
        legendgroup=dd.name,
        showlegend=False,
    )

    annotations = []
    annotations.append({})

    # add max point
    max_y = max(y_data[-1])
    max_x = x_data[-1][np.argmax(y_data[-1])]
    fig.add_annotation(
        x=max_x,
        y=max_y,
        text="".format(max_y),
        font=dict(size=16, color=colors[-1]),
        showarrow=False,
        arrowhead=2,
        arrowsize=1,
        arrowwidth=2,
    )

    fdates = df["GV1_DATE"].unique().tolist()
    a = datetime.strptime(fdates[0], "%Y-%m-%d").strftime("%b %Y")
    b = datetime.strptime(fdates[-1], "%Y-%m-%d").strftime("%b %Y")
    annotations.append(
        dict(
            xref="paper",
            yref="paper",
            x=0.5,
            y=1.05,
            xanchor="center",
            yanchor="bottom",
            text="Market Expectations for Fed Funds Rate<br>(Fed Funds Futures, {} - {})".format(
                a, b
            ),
            font=dict(family="Arial", size=20, color="rgb(37,37,37)"),
            showarrow=False,
        )
    )
    # Source
    annotations.append(
        dict(
            xref="paper",
            yref="paper",
            x=0.5,
            y=-0.1,
            xanchor="center",
            yanchor="top",
            text="Data Source: Refinitiv, Probability Distribution (USA FED)",
            font=dict(family="Arial", size=12, color="rgb(150,150,150)"),
            showarrow=False,
        )
    )

    fig.update_layout(annotations=annotations)
    fig.update_layout(
        width=1200,
        height=600,
        xaxis_range=[
            pd.to_datetime(x_data[0][0]).date() + timedelta(-30),
            pd.to_datetime(x_data[0][-1]).date() + timedelta(60),
        ],
        xaxis=dict(
            dtick="M1",
            tickformat="%b-%y",
            showline=True,
            showgrid=False,
            showticklabels=True,
            linecolor="rgb(204, 204, 204)",
            linewidth=2,
            ticks="outside",
            tickfont=dict(family="Arial", size=12, color="rgb(82, 82, 82)",),
        ),
        yaxis=dict(
            title="Rate",
            ticksuffix="%",
            tickformat=".2f",
            gridcolor="#D5D8DC",
            showgrid=True,
            zeroline=False,
            showline=True,
            showticklabels=True,
        ),
        autosize=True,
        margin=dict(autoexpand=True, l=150, r=50, t=110,),
        showlegend=True,
        legend=dict(orientation="h", yanchor="top", y=-0.2, xanchor="center", x=0.5),
        plot_bgcolor="white",
    )
    fig.layout.xaxis.fixedrange = True
    fig.layout.yaxis.fixedrange = True
    # fig.update_xaxes(visible=False)
    return fig


def get_table(ldf):
    # change color of cells
    def _color_red_or_green(val):
        if val.endswith("bps"):
            val = int(val.split("bps")[0].strip())
        colors = {
            -25: "#FDEDEC",
            -50: "#FADBD8",
            -75: "#F5B7B1",
            -100: "#F1948A",
            25: "#EAFAF1",
            50: "#D1F2EB",
            75: "#ABEBC6",
            100: "#82E0AA",
        }
        color = colors.get(val, None)
        if type(val) == int and val < -100:
            color = "#EC7063"
        elif type(val) == int and val > 100:
            color = "#58D68D"
        return "background: %s" % color

    nldf = ldf[
        ["GV1_DATE", "Instrument", "GEN_VAL3", "expected_tp"]
        + [i for i in ldf.columns if "." in i]
    ].copy()
    nldf.columns = [
        "{:.2f}".format((float(i))) if "." in i else i for i in nldf.columns
    ]

    nldf.rename(
        columns={
            "GV1_DATE": "Meeting Date",
            "GEN_VAL3": "Current Rate",
            "expected_tp": "Expected Rate",
        },
        inplace=True,
    )

    icols = sorted([i for i in nldf.columns if '.' in i])
    imin = min(map(float, icols))
    imax = max(map(float, icols))
    nldf["Meeting Date"] = pd.to_datetime(nldf["Meeting Date"]).dt.strftime("%d-%b-%Y")
    nldf["Current Rate"] = nldf["Current Rate"] + 0.125
    nldf["FED Rate (after)"] = nldf.apply(
        lambda x: icols[np.nanargmax([x[i] for i in icols])], axis=1
    ).astype(float)
    nldf["FED Rate (before)"] = (
        nldf["FED Rate (after)"].shift().fillna(nldf["Current Rate"])
    )
    nldf["Rate Change"] = (
        nldf["FED Rate (after)"] - nldf["FED Rate (after)"].shift()
    ).fillna(nldf["FED Rate (after)"] - nldf["Current Rate"])
    nldf["Rate Change"] = nldf["Rate Change"].map(
        lambda x: "{:+0.0f} bps".format(x * 100) if x else "-"
    )
    # nldf['Rate Change'] = ['-','+1000 bps','+75 bps', '+50 bps', '+25 bps', '-25 bps', '-50 bps', '-75 bps', '-100bps', '-1000bps']
    nldf = nldf[
        ["Meeting Date", "FED Rate (before)", "Rate Change", "FED Rate (after)"]
        + icols
        + ["Instrument", "Expected Rate"]
    ]

    current_rate_subset = pd.IndexSlice[0, "FED Rate (before)"]

    fig = (
        nldf.style.background_gradient(subset=icols, cmap="Blues", axis=1)
        .bar(subset=["Expected Rate"], color="#DADBDD", vmin=imin, vmax=imax)
        .highlight_null(subset=icols, color="#FFF9E3")
        .format(precision=2)
        .highlight_max(subset=["Expected Rate"], color="#BCC6CC", axis=0)
        .set_table_styles(
            [
                {
                    "selector": "thead th",
                    "props": [("background-color", "#36454F"), ("color", "white")],
                },
                {"selector": "thead th:first-child", "props": [("display", "none")]},
                {"selector": "tbody th:first-child", "props": [("display", "none")]},
                {
                    "selector": ".col",
                    "props": [("width", "100%"), ("white-space", "nowrap;")],
                },
            ],
        )
        .set_properties(subset=icols, **{"min-width": "50px"})
        .set_properties(
            subset=["Meeting Date", "FED Rate (before)"], **{"min-width": "100px"}
        )
        .set_properties(**{"text-align": "center"})
        .set_properties(subset=["Expected Rate"], **{"text-align": "right"})
        .applymap(_color_red_or_green, subset=["Rate Change"])
        .applymap(lambda x: "background-color: #FFE87C", subset=current_rate_subset)
    )
    return fig
