# standard
import time
from datetime import datetime
# third-party
from pymongo import MongoClient
from dash import Dash, dcc, html
from dash.dependencies import Input, Output, State
# project
from utils import *


app = Dash(__name__)


# LAYOUT

filters_layout = html.Section([
    html.Div([
        html.H3('Search', style={'display': 'inline'}),
        html.Span([
            html.Span(className="Select-arrow", title="is_open"),
        ],
            className='Select-arrow-zone',
            id='select_filters_arrow'
        ),
    ]
    ),
    html.Div([
        html.P('Applied filters:', id='preferencesText'),
        dcc.Dropdown(
            placeholder='Select Filters',
            id='filters_drop',
            options=['oui','non'],
            clearable=False,
            className='dropdownMenu',
            multi=False
        )
    ],
        id='dropdown_menu_applied_filters',
        style = {'display': 'none'}
    ),
],
    id="filters_container",
    style={"display": "block"},
    className="stack-top col-3"
)


title_layout = html.Div([
    html.Div([
        html.H1("FLIGHT TRACKER", 
            className="header-title", 
            style = {'textAlign': 'center', 'font-size': 15})
    ]),
    html.Div(id ='live-update-text')
],
    id="title_container",
    style={"display": "block"},
    className="stack-top col-3"
)


hovered_airplane_layout = html.Div([
    html.Div([html.H3(id="hover_callsign")], id="hover_title"),
    html.Div([
        html.Div([
            html.Div([html.H4("Latitude : ", style={'display': 'inline'})]),
            html.Div([html.H4("longitude : ", style={'display': 'inline'})]),
            html.Div([html.H4("Origin : ", style={'display': 'inline'})]),
            html.Div([html.H4("Altitude (m) : ", style={'display': 'inline'})]),
            html.Div([html.H4("Speed (m/s) : ", style={'display': 'inline'})]),
        ],
            id="hover_labels", 
        ),
        html.Div([
            html.Div([html.Span(id="hover_lat")]),
            html.Div([html.Span(id="hover_lon")]),
            html.Div([html.Span(id="hover_origin")]),
            html.Div([html.Span(id="hover_alt")]),
            html.Div([html.Span(id="hover_speed")]),
        ],
            id="hover_values", 
        )
    ]),
],
    id="hovered_airplane",
    style={"display": "none"},
)

clicked_airplane_layout = html.Div([
    html.Div([html.H3(id="click_callsign")], id="click_title"),
    html.Div([
        html.Div([
                html.Div(html.Div("Latitude : "),className='click_label'),
                html.Div(html.Span(id="click_lat"),className='click_value'),
        ],className='click_row_info'),
        html.Div([
            html.Div([html.Div("longitude : ")],className='click_label'),
            html.Div([html.Span(id="click_lon")],className='click_value'),
        ],className='click_row_info'),
        html.Div([
            html.Div([html.Div("Origin : ")],className='click_label'),
            html.Div([html.Span(id="click_origin")],className='click_value'),
        ],className='click_row_info'),
        html.Div([
            html.Div([html.Div("Altitude (m) : ")],className='click_label'),
            html.Div([html.Span(id="click_alt")],className='click_value'),
        ],className='click_row_info'),
        html.Div([
            html.Div([html.Div("Speed (m/s) : ")],className='click_label'),
            html.Div([html.Span(id="click_speed")],className='click_value'),
        ],className='click_row_info'),
        html.Div([
            html.Div([html.Div("ICAO 24 : ")],className='click_label'),
            html.Div([html.Span(id="click_icao")],className='click_value'),
        ],className='click_row_info'),
        html.Div([
            html.Div([html.Div("Time Position : ")],className='click_label'),
            html.Div([html.Span(id="click_time")],className='click_value'),
        ],className='click_row_info'),
        html.Div([
            html.Div([html.Div("Last Contact : ")],className='click_label'),
            html.Div([html.Span(id="click_last_contact")],className='click_value'),
        ],className='click_row_info'),
        html.Div([
            html.Div([html.Div("True Track (°): ")],className='click_label'),
            html.Div([html.Span(id="click_true_track")],className='click_value'),
        ],className='click_row_info'),
        html.Div([
            html.Div([html.Div("Vertical Rate (m/s) : ")],className='click_label'),
            html.Div([html.Span(id="click_vertical")],className='click_value'),
        ],className='click_row_info'),
        html.Div([
            html.Div([html.Div("Position Source : ")],className='click_label'),
            html.Div([html.Span(id="click_pos_source")],className='click_value'),
        ],className='click_row_info'),
    ],
        id="click_values"
    ),
    html.Div([
        dcc.Graph(id="alt-graph")
    ],
        id="altitude-graph"
    ),
],
    id="click_airplane",
    style={"display": "none"},
)


app.layout = html.Div([
    html.Div([
        title_layout,
        html.Div([
            dcc.Graph(id = 'live-graph', 
                      clear_on_unhover=True)
        ],
            className='background-map-container'
        ),
        dcc.Interval(id = 'graph-update',
                    interval = 60*1000,
                    n_intervals = 0
                    ),
    ],
        id="map_container",
        style={'display': 'flex'}
    ),
    filters_layout,
    hovered_airplane_layout,
    clicked_airplane_layout,
],
    id='page-content',
    style={'position': 'relative'},
)



# CALLBACKS

# global dataframe of flying airplane
# can be accessed by multiple callbacks
df = []

@app.callback(Output('live-update-text', 'children'), 
             [Input('graph-update', 'n_intervals')])
def last_update(n):
    return html.H2('Last Update: ' + str(datetime.now().strftime('%d-%m-%Y %H:%M:%S')),
                    className="header-title", 
                    style = {'textAlign': 'center',
                             'font-size': 12})


@app.callback(Output('live-graph', 'figure'), 
             [Input('graph-update', 'n_intervals')])
def flight_tracker_update(n):
    
    global df 
    #print(df)
    df , fig = flight_tracker()
    return fig


@app.callback(Output('hovered_airplane', "style"),
              Output('hover_callsign', 'children'),
              Output('hover_lat', 'children'),
              Output('hover_lon', 'children'),
              Output('hover_origin', 'children'),
              Output('hover_alt', 'children'),
              Output('hover_speed', 'children'),
              #Output('hover_infos', 'children'),
              [Input('live-graph', 'hoverData')])
def update_hovered_airplane(hoverData):

    if hoverData is not None:
        top = hoverData['points'][0]['bbox']['y0']
        left = hoverData['points'][0]['bbox']['x0']

        row_nb = hoverData['points'][0]['pointIndex']
        row = df.iloc[row_nb]
        callsign = row.callsign
        lat = row.lat
        lon = row.long
        origin = row.origin_country
        alt = row.baro_altitude
        speed = row.velocity

        #infos = hoverData['points'][0]['text']

        style = {'display': 'block',
                'top':str(top)+'px',
                'left':str(left)+'px'}
    else:
        #infos = ""
        callsign = ""
        lat = ""
        lon = ""
        origin = ""
        alt = ""
        speed = ""
        style = {'display': 'none'}

    return style, callsign, lat, lon, origin, alt, speed


@app.callback(Output('click_airplane', "style"),
              Output('click_callsign', 'children'),
              Output('click_lat', 'children'),
              Output('click_lon', 'children'),
              Output('click_origin', 'children'),
              Output('click_alt', 'children'),
              Output('click_speed', 'children'),
              Output('click_icao', 'children'),
              Output('click_time', 'children'),
              Output('click_last_contact', 'children'),
              Output('click_true_track', 'children'),
              Output('click_vertical', 'children'),
              Output('click_pos_source', 'children'),
              [Input('live-graph', 'clickData')])
def update_clicked_airplane(clickData):
    print('OK')
    if clickData is not None:
        row_nb = clickData['points'][0]['pointIndex']
        row = df.iloc[row_nb]
        callsign = row.callsign
        lat = row.lat
        lon = row.long
        origin = row.origin_country
        alt = row.baro_altitude
        speed = row.velocity
        icao = row.icao24
        time = datetime.utcfromtimestamp(row.time_position)
        last_contact = datetime.utcfromtimestamp(row.last_contact)
        true_track = row.true_track
        vertical = row.vertical_rate
        pos = row.position_source

        style = {'display': 'block'}
    else:
        #infos = ""
        callsign = ""
        lat = ""
        lon = ""
        origin = ""
        alt = ""
        speed = ""
        icao = ""
        time = ""
        last_contact = ""
        true_track = ""
        vertical = ""
        pos = ""
        style = {'display': 'none'}

    return style, callsign, lat, lon, origin, alt, speed, icao, time, last_contact, true_track, vertical, pos



@app.callback(Output('dropdown_menu_applied_filters', 'style'),
              Output('select_filters_arrow', 'title'),
              Input('select_filters_arrow', 'n_clicks'),
              State('select_filters_arrow', 'title'))
def toggle_applied_filters(n_clicks, state):
    style = {'display': 'none'}
    if n_clicks is not None:
        if state == 'is_open':
            style = {'display': 'none'}
            state = 'is_closed'
        else:
            style = {'display': 'block'}
            state = 'is_open'

    return style, state

if __name__ == "__main__":
    app.run_server(debug = True)
