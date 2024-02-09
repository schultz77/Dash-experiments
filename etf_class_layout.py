
import dash_ag_grid as dag
from dash import html, dcc
import dash_bootstrap_components as dbc
import pandas as pd

import yfinance as yf

from datetime import datetime
from dataclasses import dataclass, field


@dataclass
class Etf:
    stock_data: dict = None
    data: dict = None
    df: pd.DataFrame = None
    defaultColDef: dict = None
    grid: dag = None

    pie: dbc.Card = None
    header: html.Div = None
    badge = dbc.Row
    candlestick: dbc.Card = None
    my_ticker: list = field(default=None)

    equities: dict = field(default_factory=lambda: {
        "YOURS.DE": "TEST ETF",
        "YOURS1.DE": "TEST1 ETF",
        "YOURS2.DE": "TEST2 ETF",
        "YOURS3.DE": "TEST3 ETF",
        "YOURS4.DE": "TEST4 ETF",
        "YOURS5.DE": "TEST5 ETF",

    })

    columnDefs: list = field(default_factory=dict)

    def __post_init__(self):
        self.get_etf_grid()
        self.get_header()
        self.get_pie()
        self.get_candlestick()
        self.get_badge()

    def get_stock_data(self):
        self.stock_data = yf.download(tickers=list(self.equities.keys()), period="2y", group_by="ticker")

    def last_close(self, ticker):
        amount = self.stock_data[ticker]["Close"].iloc[-1]
        return amount

    def set_data(self):
        self.get_stock_data()

        self.my_ticker = [ticker for ticker in self.equities]
        price = [self.last_close(ticker) for ticker in self.equities]
        my_company = [name for name in self.equities.values()]

        for cnt in range(2):
            self.my_ticker.append(list(self.equities.keys())[cnt])
            price.append(self.last_close(list(self.equities.keys())[cnt]))
            my_company.append(list(self.equities.values())[cnt])

        self.data = {
            "ticker": self.my_ticker,
            "bank": ['BANK', 'BANK', 'BANK', 'BANK', 'BANK', 'BANK2', 'BANK3', 'BANK3'],
            "company": my_company,
            "art": ['capitalizing', 'capitalizing', 'capitalizing', 'distributing', 'distributing', 'capitalizing',
                    'capitalizing', 'capitalizing'],
            "buy_in": [28.34, 48.696242, 112.111, 123.8080, 78.3175, 15.79, 27.89, 58.59],
            "quantity": [235, 330, 18, 41, 252.66705, 427.512825, 190.084, 198.545],
            "price": price,
        }
        self.df = pd.DataFrame(self.data)

    def set_col_def(self):
        locale_de = """d3.formatLocale({
          "decimal": ",",
          "thousands": "\u00a0",
          "grouping": [3],
          "currency": ["", "\u00a0€"],
          "percent": "\u202f%",
          "nan": ""
        })"""

        self.columnDefs = [
            {
                "headerName": "Ticker",
                "field": "ticker",
                "filter": True,
                "width": 100,
            },
            {
                "headerName": "Broker",
                "field": "bank",
                "filter": True,
                "width": 105,
            },
            {
                "headerName": "Company",
                "field": "company",
                "filter": True,
                "width": 125,
            },
            {
                "headerName": "Type",
                "field": "art",
                "filter": True,
                "editable": False,
                "width": 110,
            },
            {
                "headerName": "Shares",
                "field": "quantity",
                "editable": True,
                "type": "rightAligned",
                "width": 100,
                "valueFormatter": {"function": f"{locale_de}.format(',.2f')(params.value)"},
            },
            {
                "headerName": "Buy In",
                "field": "buy_in",
                "editable": False,
                "type": "rightAligned",
                "valueFormatter": {"function": f"{locale_de}.format('$,.2f')(params.value)"},
                "width": 105,
            },
            {
                "headerName": "Last Close Price",
                "field": "price",
                "type": "rightAligned",
                # "valueFormatter": {"function": "d3.format('$,.2f')(params.value)"},
                # "valueFormatter": {"function": "EUR(params.value)"},
                "valueFormatter": {"function": f"{locale_de}.format('$,.2f')(params.value)"},
                "cellRenderer": "agAnimateShowChangeCellRenderer",
                "width": 105,
            },
            {
                "headerName": "Market Value",
                "type": "rightAligned",
                "valueGetter": {"function": "Number(params.data.price) * Number(params.data.quantity)"},
                # "valueFormatter": {"function": "d3.format('$,.2f')(params.value)"},
                # "valueFormatter": {"function": "EUR(params.value)"},
                "valueFormatter": {"function": f"{locale_de}.format('$,.2f')(params.value)"},
                "cellRenderer": "agAnimateShowChangeCellRenderer",
                "width": 105,
            },
            {
                "headerName": "Performance",
                "type": "rightAligned",
                "valueGetter": {
                    "function": "(Number(params.data.price)-Number(params.data.buy_in))*1 / Number(params.data.buy_in)"
                },
                # "valueFormatter": {"function": "d3.format('$,.2f')(params.value)"},
                # "valueFormatter": {"function": "EUR(params.value)"},
                "valueFormatter": {"function": f"{locale_de}.format('.2%')(params.value)"},
                "cellRenderer": "agAnimateShowChangeCellRenderer",
                "width": 105,
                "cellStyle": {
                    "styleConditions": [
                        {
                            "condition": "params.value > 4.5/100",
                            "style": {"backgroundColor": "#196A4E", "color": "white"},
                        },
                        {
                            "condition": "params.value < 0",
                            "style": {"backgroundColor": "#800000", "color": "white"},
                        },
                    ]
                }
            },
        ]

        self.defaultColDef = {
            "filter": "agNumberColumnFilter",
            "resizable": True,
            "sortable": True,
            "editable": False,
            "floatingFilter": True,
        }

    def get_etf_grid(self):
        self.set_col_def()
        self.set_data()

        self.grid = dag.AgGrid(
            id="portfolio-grid",
            className="ag-theme-alpine-dark",
            columnDefs=self.columnDefs,
            rowData=self.df.to_dict("records"),
            columnSize="sizeToFit",
            defaultColDef=self.defaultColDef,
            dashGridOptions={"undoRedoCellEditing": True, "rowSelection": "single", 'domLayout': 'autoHeight'},
        )

    def get_candlestick(self):
        self.candlestick = dbc.Card(dcc.Graph(id="candlestick"), body=True)

    def get_pie(self):
        self.pie = dbc.Card(dcc.Graph(id="asset-allocation"), body=True)

    def get_header(self):
        self.header = html.Div("My Portfolio", className="h2 p-2 text-white bg-primary text-center")

    def get_badge(self):
        self.badge = dbc.Row([dbc.Col(),
                              dbc.Col(
                                  dbc.Badge(
                                      f"Last update: {datetime.now().strftime('%d.%m.%Y - %H:%M:%S')}",
                                      id='last_update'),
                                  width="auto"
                              ),
                              ])
