# standard
from datetime import datetime
# third-party
from dash import Dash, dcc, html, dash_table
from dash.dependencies import Input, Output, State
# project
from utils import *


debug = False if os.environ["DASH_DEBUG_MODE"] == "False" else True

app = Dash(__name__)
server = app.server


# LAYOUT

# filters 
filters_layout = html.Div([
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
        #html.P('Applied filters:', id='filter_text'),
        dcc.Dropdown(
            placeholder='Select Filter',
            id='filters_drop',
            options=['By Flight','By Route', 'By Airports'],
            clearable=True,
            className='dropdownMenu',
            multi=False
        ),
        html.Div([
            html.Div([
                dcc.Input(
                    placeholder="(ex: LH400)",
                    id="input_flightnumber",
                    className='input_fields',
                    style = {'display': 'none'}),
                dcc.Input(
                    placeholder="(ex: FRA)",
                    id="input_departure",
                    className='input_fields',
                    style = {'display': 'none'}),
                dcc.Input(
                    placeholder="(ex: JFK)",
                    id="input_arrival",
                    className='input_fields',
                    style = {'display': 'none'}),
                dcc.Input(
                    placeholder="(ex: FRA)",
                    id="input_airport",
                    className='input_fields',
                    style = {'display': 'none'})    
            ],  id='input_div'
            ),


            html.Button('SUBMIT', id='submit_val', n_clicks=0),
        ],
            id='fields_for_applied_filters',
            style = {'display': 'none'}
        ),

    ],
        id='dropdown_applied_filters',
        style = {'display': 'none'}
    ),
    
],
    id="filters_container",
    style={"display": "block"},
    className="stack-top col-3"
)

# title
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

# hovered airplane
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

# clicked airplane
clicked_airplane_layout = html.Div([
    html.Div([
        html.H3(id="click_callsign"),
        html.Span('X', id="x_close_selection")]),
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

# filter airport 
filtered_airport_layout = html.Div([
    html.Div(id="airport_infos"),
    html.Div([
        html.H3("Departures",
                 style={"display": "inline-block",
                        'textAlign': 'center',
                        "width":"100%"}
        ),
        html.Div(id='departures_table',
                className = "airport_table",
                style={"display": "block"})
    ], id="departures_panel",
       style={"display": "inline-block"}
    ),
    html.Div([
        html.H3("Arrivals",
                 style={"display": "inline-block",
                        'textAlign': 'center',
                        "width":"100%"}
        ),
        html.Div(id='arrivals_table',
                 className = "airport_table",
                 style={"display": "block"})
    ], id="arrivals_panel",
       style={"display": "inline-block"}
    ),
    html.Span('X', id="x_close_airport"),
],
    id="airport_panel",
    style={"display": "none"},
)

# dashboard
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
    filtered_airport_layout,
],
    id='page-content',
    style={'position': 'relative'},
)



# GLOBAL VARIABLES

# global dataframe of flying airplane
df = []
# close button of the airplane selection panel
x_close_selection_clicks = 0
# submit button of the airplane selection panel
submit_clicks = 0
# clicks on the map
map_n_clicks = 0 
# close button of the airport selection panel
x_close_airport_clicks = 0

# CALLBACKS

@app.callback(Output('live-update-text', 'children'), 
             [Input('graph-update', 'n_intervals')])
def last_update(n):
    """ displays the last update time on the titel layout """

    return html.H2('Last Update: ' + str(datetime.now().strftime('%d-%m-%Y %H:%M:%S')),
                    className="header-title", 
                    style = {'textAlign': 'center',
                             'font-size': 12})


@app.callback(Output('live-graph', 'figure'), 
             [Input('graph-update', 'n_intervals')])
def flight_tracker_update(n):
    """ displays the map on the background layout"""

    global df
    df , fig = flight_tracker()

    return fig


@app.callback(Output('hovered_airplane', "style"),
              Output('hover_callsign', 'children'),
              Output('hover_lat', 'children'),
              Output('hover_lon', 'children'),
              Output('hover_origin', 'children'),
              Output('hover_alt', 'children'),
              Output('hover_speed', 'children'),
              [Input('live-graph', 'hoverData')])
def update_hovered_airplane(hoverData):
    """
    Display moving panel with few position info 
    next to mouse pointer when hovering airplane 
    """

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

        style = {'display': 'block',
                'top':str(top+10)+'px',
                'left':str(left+10)+'px'}
    else:
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
              [Input('live-graph', 'clickData')],
              Input('x_close_selection', 'n_clicks'),
              )
def update_clicked_airplane(clickData, n_clicks):
    """
    Open right side panel with full airplane info 
    when airplane is clicked and close with the top-right X
    """
    global x_close_selection_clicks

    # value to display when clicked
    if clickData is not None :
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

    # close panel
    if n_clicks != x_close_selection_clicks:
        style = {'display': 'none'}
        x_close_selection_clicks = n_clicks

    return style, callsign, lat, lon, origin, alt, speed, icao, time, last_contact, true_track, vertical, pos


@app.callback(Output('live-graph', 'clickData'),
             [Input('map_container', 'n_clicks')])
def reset_clickData(n_clicks):
    """ 
    workaround to clear the clickData field and 
    remove right panel when clicking anywhere on the map except
    airplane
    """
    return None



@app.callback(Output('dropdown_applied_filters', 'style'),
              Output('select_filters_arrow', 'title'),
              Input('select_filters_arrow', 'n_clicks'),
              State('select_filters_arrow', 'title'))
def toggle_applied_filters(n_clicks, state):
    """ toggle filter box """

    style = {'display': 'none'}
    if n_clicks is not None:
        if state == 'is_open':
            style = {'display': 'none'}
            state = 'is_closed'
        else:
            style = {'display': 'block'}
            state = 'is_open'

    return style, state


@app.callback(Output('fields_for_applied_filters', 'style'),
              Output('input_flightnumber', 'style'),
              Output('input_departure', 'style'),
              Output('input_arrival', 'style'),
              Output('input_airport', 'style'),
              Input('filters_drop', 'value'))
def toggle_fields(dd_value):
    """ toggle fields depending on filter selected """

    fields_style = {'display': 'none'}
    input_flightnumber_style = {'display': 'none'}
    input_departure_style = {'display': 'none'}
    input_arrival_style = {'display': 'none'}
    input_airport_style = {'display': 'none'}

    if dd_value is not None:
        fields_style = {'display': 'block'}
        if dd_value == 'By Flight':
            input_flightnumber_style = {'display': 'block'}
        elif dd_value == 'By Route':
            input_departure_style = {'display': 'block'}
            input_arrival_style = {'display': 'block'}
        elif dd_value == 'By Airports':
            input_airport_style = {'display': 'block'}

    return fields_style, input_flightnumber_style, \
            input_departure_style, input_arrival_style, \
            input_airport_style


@app.callback(Output('airport_panel', 'style'),
              Output('arrivals_table', 'children'),
              Output('departures_table', 'children'),
              Output('airport_infos', 'children'),
              Input('submit_val','n_clicks'),
              Input('map_container', 'n_clicks'),
              Input('x_close_airport', 'n_clicks'),
              State('input_airport', 'value'))
def display_airport_panel(sub_clicks,map_clicks,close_clicks,value):
    """
    display airport panel based on airport field value
    when submit button is clicked
    """
    global submit_clicks
    global map_n_clicks
    global x_close_airport_clicks

    style = {'display': 'none'}
    df_arr = ""
    df_dep = ""
    arrivals_tbl = ""
    departures_tbl = ""
    airport_name = ""

    if (map_n_clicks == map_clicks) or map_clicks is None:
        if (sub_clicks != submit_clicks) and not (value is None or value == "") :
            print(value)
            style = {'display': 'block'}
            submit_clicks = sub_clicks

            df_arr = get_arrivals(value)
            df_dep = get_departures(value)

            arrivals_tbl = dash_table.DataTable(
                            data=df_arr.to_dict('records'),
                            columns=[{"name": i, "id": i} for i in df_arr.columns],
                            style_as_list_view=True,
                            style_header={
                                'backgroundColor': 'cornflowerblue',
                                'color':'white',
                                'fontWeight': 'bold'
                            },
                            style_cell_conditional=[
                                {
                                    'if': {'column_id': c},
                                    'textAlign': 'center'
                                } for c in df_arr.columns
                            ],
                            style_data_conditional=[
                                {
                                    'if': {'row_index': 'odd'},
                                    'backgroundColor': 'rgb(220, 220, 220)',
                                }
                            ],
                            page_size=10)
            departures_tbl = dash_table.DataTable(
                            data=df_dep.to_dict('records'),
                            columns=[{"name": i, "id": i} for i in df_dep.columns],
                            style_as_list_view=True,
                            style_header={
                                'backgroundColor': 'cornflowerblue',
                                'color':'white',
                                'fontWeight': 'bold'
                            },
                            style_cell_conditional=[
                                {
                                    'if': {'column_id': c},
                                    'textAlign': 'center'
                                } for c in df_dep.columns
                            ],
                            style_data_conditional=[
                                {
                                    'if': {'row_index': 'odd'},
                                    'backgroundColor': 'rgb(220, 220, 220)',
                                }
                            ],
                            page_size=10)
            try:
                airport_name = get_airport_infos(value)[0]
            except IndexError:
                airport_name = ""
            airport_name = value.upper() + " ("+ airport_name + ")"
    else:
        map_n_clicks += 1

    # close panel
    if close_clicks != x_close_airport_clicks:
        style = {'display': 'none'}
        x_close_airport_clicks = close_clicks

    return style, arrivals_tbl, departures_tbl, airport_name

    



# main
if __name__ == "__main__":
    app.run(port="8050",debug = debug)
