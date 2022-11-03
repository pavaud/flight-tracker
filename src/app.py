# standard
import time
from datetime import datetime
# third-party
from pymongo import MongoClient
# project
from utils import *
import dash
from dash import Dash, dcc, html
from dash.dependencies import Input, Output
#from jupyter_dash import JupyterDash

app = Dash(__name__)

app.layout = html.Div([
                       html.H1("Real-time flight tracker", className="header-title", 
                               style = {'textAlign': 'center', 'font-size': 15}),
                       html.Div(id ='live-update-text'),
                       dcc.Graph(id = 'live-graph', animate = True),
                       dcc.Interval(id = 'graph-update',
                                    interval = 60*1000,
                                    n_intervals = 0
                                    ),
                      ])

#-------------------------------------------------------------------------------
# Callbacks to update aircraft position and last update time
@app.callback(Output('live-update-text', 'children'), [Input('graph-update', 'n_intervals')])
def last_update(n):
    return html.H2('Last update: ' + str(datetime.now().strftime('%d-%m-%Y %H:%M:%S')),
                    className="header-title", style = {'textAlign': 'center', 'font-size': 9})

@app.callback(Output('live-graph', 'figure'), [Input('graph-update', 'n_intervals')])
def flight_tracker_update(n):
    return flight_tracker()


if __name__ == "__main__":
    app.run_server(debug = True)
