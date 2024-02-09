"""

"""
import dash

from dash import Dash, dcc, Input, Output, State
import dash_bootstrap_components as dbc
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime

import locale

# comment out if running on a server
import os
from threading import Timer
import webbrowser
# comment out if running on a server

from etf_class_layout import Etf

etf = Etf()
app = Dash(__name__, external_stylesheets=[dbc.themes.DARKLY])

app.layout = dbc.Container(
    [
        dcc.Interval(id='interval1', interval=120 * 1000, n_intervals=0),
        etf.header,
        etf.badge,
        dbc.Row([dbc.Col(etf.candlestick), dbc.Col(etf.pie)]),
        dbc.Row(dbc.Col(etf.grid, className="py-4")),
    ],
)


@app.callback(
    Output("candlestick", "figure"),
    Input("portfolio-grid", "selectedRows"),
)
def update_candlestick(selected_row):
    if selected_row is None:
        ticker = "YOURS.DE"
        company = "YOUR ETF"
    elif len(selected_row):
        ticker = selected_row[0]["ticker"]
        company = selected_row[0]["company"]
    else:
        return dash.no_update

    dff_ticker_hist = etf.stock_data[ticker].reset_index()
    dff_ticker_hist["Date"] = pd.to_datetime(dff_ticker_hist["Date"])

    fig = go.Figure(
        go.Candlestick(
            x=dff_ticker_hist["Date"],
            open=dff_ticker_hist["Open"],
            high=dff_ticker_hist["High"],
            low=dff_ticker_hist["Low"],
            close=dff_ticker_hist["Close"],
        )
    )
    fig.update_layout(
        title_text=f"{ticker} {company} Daily Price", template="plotly_dark"
    )
    return fig


@app.callback(
    Output("asset-allocation", "figure"),
    Input("portfolio-grid", "cellValueChanged"),
    State("portfolio-grid", "rowData"),
)
def update_portfolio_stats(_, grid_data):
    dff = pd.DataFrame(grid_data)
    dff["total"] = dff["quantity"].astype(float) * dff["price"].astype(float)
    portfolio_total = dff["total"].sum()

    locale.setlocale(locale.LC_ALL, 'de_DE.utf8')
    my_title = locale.format_string("%.2f", portfolio_total, True)
    return px.pie(
        dff,
        values="total",
        names="ticker",
        hole=0.3,
        # title=f"Portfolio Total {portfolio_total:,.2f}€",
        title=f"Portfolio Total: {my_title}€",
        template="plotly_dark",
    )


@app.callback(
    Output("portfolio-grid", "rowData"),
    Output("last_update", "children"),
    Input('interval1', 'n_intervals'),
    State("portfolio-grid", "rowData"),
)
def time_update(_, row_data):
    stock_data = etf.get_stock_data()

    for cnt, ticker in enumerate(etf.equities):
        row_data[cnt]["price"] = etf.last_close(ticker)

    return row_data, f"Last update: {datetime.now().strftime('%d.%m.%Y - %H:%M:%S')}"


# comment out if running on a server
def open_browser():
    if not os.environ.get("WERKZEUG_RUN_MAIN"):
        webbrowser.open_new('http://127.0.0.1:1222/')


if __name__ == "__main__":
    Timer(1, open_browser).start() # comment out if running on a server
    app.run_server(debug=True, port=1222)
