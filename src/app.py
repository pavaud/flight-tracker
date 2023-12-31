#!/usr/bin/env python

"""Tracking all airplanes currently flying on earth.

Filters can be used to search for a specific flight, route or airport.

Usage: $ python app.py
"""

import logging
import os
from datetime import datetime

import pandas as pd
from dash import Dash, dcc, html, dash_table
from dash.dependencies import Input, Output, State
import plotly.express as px
import plotly.graph_objects as go

import constants as c
import utils


# make debug or not depending on docker-compose
try:
    DEBUG = os.environ["DASH_DEBUG_MODE"]
except Exception:
    DEBUG = True

# create app and server
app = Dash(__name__)
server = app.server

# Parse commandline arguments
args = utils.init_args()

# Logging config
utils.init_log_conf(args.loglevel, c.DASH_LOG_PATH)

# GLOBAL VARIABLES

# global dataframe of flying airplanes
response = utils.get_opensky_flights()
df = utils.get_opensky_df(response)
# global map figure
map_fig = go.Figure()
map_fig = utils.add_flights_on_map(map_fig, df)
# number of interval triggered
n_intervals = 0

# submit button of the airplane selection panel
submit_clicks = 0
# clicks on the map
map_n_clicks = 0
# close button of the airplane selection panel
x_close_selection_clicks = 0
# close button of the airport panel
x_close_airport_clicks = 0
# close button of the route panel
x_close_route_clicks = 0
# previous clickData
clickData_previous = None
# memorized callsign when click on airplane
callsign = ""


# LAYOUT

# filters
filters_layout = html.Div(
    [
        html.Div(
            [
                html.H3("Search", style={"display": "inline"}),
                html.Span(
                    [
                        html.Span(className="Select-arrow", title="is_open"),
                    ],
                    className="Select-arrow-zone",
                    id="select_filters_arrow",
                ),
            ]
        ),
        html.Div(
            [
                dcc.Dropdown(
                    placeholder="Select Filter",
                    id="filters_drop",
                    options=["By Flight", "By Route", "By Airports"],
                    clearable=True,
                    className="dropdownMenu",
                    multi=False,
                ),
                html.Div(
                    [
                        html.Div(
                            [
                                dcc.Input(
                                    placeholder="(ex: LH400)",
                                    id="input_flightnumber",
                                    className="input_fields",
                                    style={"display": "none"},
                                ),
                                dcc.Input(
                                    placeholder="(ex: FRA)",
                                    id="input_departure",
                                    className="input_fields",
                                    style={"display": "none"},
                                ),
                                dcc.Input(
                                    placeholder="(ex: LHR)",
                                    id="input_arrival",
                                    className="input_fields",
                                    style={"display": "none"},
                                ),
                                dcc.Input(
                                    placeholder="(ex: FRA)",
                                    id="input_airport",
                                    className="input_fields",
                                    style={"display": "none"},
                                ),
                            ],
                            id="input_div",
                        ),
                        html.Button("SUBMIT", id="submit_val", n_clicks=0),
                    ],
                    id="fields_for_applied_filters",
                    style={"display": "none"},
                ),
            ],
            id="dropdown_applied_filters",
            style={"display": "none"},
        ),
    ],
    id="filters_container",
    style={"display": "block"},
    className="stack-top col-3",
)

# title
title_layout = html.Div(
    [
        html.Div(
            [
                html.H1(
                    "FLIGHT TRACKER",
                    className="header-title",
                    style={"textAlign": "center", "font-size": 15},
                )
            ]
        ),
        html.Div(id="live-update-text"),
    ],
    id="title_container",
    style={"display": "block"},
    className="stack-top col-3",
)

# hovered airplane
hovered_airplane_layout = html.Div(
    [
        html.Div([html.H3(id="hover_callsign")], id="hover_title"),
        html.Div(
            [
                html.Div(
                    [
                        html.Div(
                            [
                                html.H4(
                                    "Latitude : ", style={"display": "inline"}
                                )
                            ]
                        ),
                        html.Div(
                            [
                                html.H4(
                                    "longitude : ", style={"display": "inline"}
                                )
                            ]
                        ),
                        html.Div(
                            [html.H4("Origin : ", style={"display": "inline"})]
                        ),
                        html.Div(
                            [
                                html.H4(
                                    "Altitude (m) : ",
                                    style={"display": "inline"},
                                )
                            ]
                        ),
                        html.Div(
                            [
                                html.H4(
                                    "Speed (m/s) : ",
                                    style={"display": "inline"},
                                )
                            ]
                        ),
                    ],
                    id="hover_labels",
                ),
                html.Div(
                    [
                        html.Div([html.Span(id="hover_lat")]),
                        html.Div([html.Span(id="hover_lon")]),
                        html.Div([html.Span(id="hover_origin")]),
                        html.Div([html.Span(id="hover_alt")]),
                        html.Div([html.Span(id="hover_speed")]),
                    ],
                    id="hover_values",
                ),
            ]
        ),
    ],
    id="hovered_airplane",
    style={"display": "none"},
)

# clicked airplane
clicked_airplane_layout = html.Div(
    [
        html.Div(
            [
                html.H3(id="click_callsign"),
                html.Span("X", id="x_close_selection"),
            ]
        ),
        html.Div(
            [
                html.Div(
                    [
                        html.Div(
                            html.Div("Latitude : "), className="click_label"
                        ),
                        html.Div(
                            html.Span(id="click_lat"), className="click_value"
                        ),
                    ],
                    className="click_row_info",
                ),
                html.Div(
                    [
                        html.Div(
                            [html.Div("longitude : ")], className="click_label"
                        ),
                        html.Div(
                            [html.Span(id="click_lon")],
                            className="click_value",
                        ),
                    ],
                    className="click_row_info",
                ),
                html.Div(
                    [
                        html.Div(
                            [html.Div("Origin : ")], className="click_label"
                        ),
                        html.Div(
                            [html.Span(id="click_origin")],
                            className="click_value",
                        ),
                    ],
                    className="click_row_info",
                ),
                html.Div(
                    [
                        html.Div(
                            [html.Div("Altitude (m) : ")],
                            className="click_label",
                        ),
                        html.Div(
                            [html.Span(id="click_alt")],
                            className="click_value",
                        ),
                    ],
                    className="click_row_info",
                ),
                html.Div(
                    [
                        html.Div(
                            [html.Div("Speed (m/s) : ")],
                            className="click_label",
                        ),
                        html.Div(
                            [html.Span(id="click_speed")],
                            className="click_value",
                        ),
                    ],
                    className="click_row_info",
                ),
                html.Div(
                    [
                        html.Div(
                            [html.Div("ICAO 24 : ")], className="click_label"
                        ),
                        html.Div(
                            [html.Span(id="click_icao")],
                            className="click_value",
                        ),
                    ],
                    className="click_row_info",
                ),
                html.Div(
                    [
                        html.Div(
                            [html.Div("Time Position : ")],
                            className="click_label",
                        ),
                        html.Div(
                            [html.Span(id="click_time")],
                            className="click_value",
                        ),
                    ],
                    className="click_row_info",
                ),
                html.Div(
                    [
                        html.Div(
                            [html.Div("Last Contact : ")],
                            className="click_label",
                        ),
                        html.Div(
                            [html.Span(id="click_last_contact")],
                            className="click_value",
                        ),
                    ],
                    className="click_row_info",
                ),
                html.Div(
                    [
                        html.Div(
                            [html.Div("True Track (°): ")],
                            className="click_label",
                        ),
                        html.Div(
                            [html.Span(id="click_true_track")],
                            className="click_value",
                        ),
                    ],
                    className="click_row_info",
                ),
                html.Div(
                    [
                        html.Div(
                            [html.Div("Vertical Rate (m/s) : ")],
                            className="click_label",
                        ),
                        html.Div(
                            [html.Span(id="click_vertical")],
                            className="click_value",
                        ),
                    ],
                    className="click_row_info",
                ),
                html.Div(
                    [
                        html.Div(
                            [html.Div("Position Source : ")],
                            className="click_label",
                        ),
                        html.Div(
                            [html.Span(id="click_pos_source")],
                            className="click_value",
                        ),
                    ],
                    className="click_row_info",
                ),
            ],
            id="click_values",
        ),
        html.Div([dcc.Graph(id="alt_graph")], id="altitude_graph"),
    ],
    id="click_airplane",
    style={"display": "none"},
)

# filter airport
filtered_airport_layout = html.Div(
    [
        html.Div(id="airport_infos"),
        html.Div(
            [
                html.H3(
                    "Departures",
                    style={
                        "display": "inline-block",
                        "textAlign": "center",
                        "width": "100%",
                    },
                ),
                html.Div(
                    id="departures_table",
                    className="airport_table",
                    style={"display": "block"},
                ),
            ],
            id="departures_panel",
            style={"display": "inline-block"},
        ),
        html.Div(
            [
                html.H3(
                    "Arrivals",
                    style={
                        "display": "inline-block",
                        "textAlign": "center",
                        "width": "100%",
                    },
                ),
                html.Div(
                    id="arrivals_table",
                    className="airport_table",
                    style={"display": "block"},
                ),
            ],
            id="arrivals_panel",
            style={"display": "inline-block"},
        ),
        html.Span("X", id="x_close_airport"),
    ],
    id="airport_panel",
    style={"display": "none"},
)

# filter route
filtered_route_layout = html.Div(
    [
        html.Div(
            [
                html.Div(id="airline_route"),
                html.Div(id="flightnumber_route"),
                html.Div(id="arr_dep_city"),
            ],
            id="head_route",
        ),
        html.Span("X", id="x_close_route"),
        html.Div(
            [
                html.Div(
                    [
                        html.Div(id="dep_iata_route", className="iata_route"),
                        html.Div(
                            id="dep_airport_route", className="airport_route"
                        ),
                        html.Div(id="dep_time_route", className="time_route"),
                    ],
                    id="dep_route",
                    className="arr_dep_route",
                    style={"display": "inline-block"},
                ),
                html.Div(
                    [
                        html.Div(id="arr_iata_route", className="iata_route"),
                        html.Div(
                            id="arr_airport_route", className="airport_route"
                        ),
                        html.Div(id="arr_time_route", className="time_route"),
                    ],
                    id="arr_route",
                    className="arr_dep_route",
                    style={"display": "inline-block"},
                ),
            ],
            id="arr_dep_route",
        ),
    ],
    id="route_panel",
    className="route",
    style={"display": "none"},
)


# dashboard
app.layout = html.Div(
    [
        html.Div(
            [
                title_layout,
                html.Div(
                    [
                        dcc.Graph(
                            figure=map_fig,
                            id="map",
                            clear_on_unhover=True,
                        )
                    ],
                    className="background-map-container",
                ),
                dcc.Interval(
                    id="map-interval",
                    interval=c.MAP_UPDATE_INTERVAL,
                    n_intervals=0,
                ),
            ],
            id="map_container",
            style={"display": "flex"},
        ),
        filters_layout,
        hovered_airplane_layout,
        clicked_airplane_layout,
        filtered_airport_layout,
        filtered_route_layout,
    ],
    id="page-content",
    style={"position": "relative"},
)


# CALLBACKS


@app.callback(
    Output("live-update-text", "children"),
    Input("map-interval", "n_intervals"),
)
def last_update(n):
    """displays the last update time on the titel layout"""

    return html.H2(
        "Last Update: " + str(datetime.now().strftime("%d-%m-%Y %H:%M:%S")),
        className="header-title",
        style={"textAlign": "center", "font-size": 12},
    )


@app.callback(
    Output("hovered_airplane", "style"),
    Output("hover_callsign", "children"),
    Output("hover_lat", "children"),
    Output("hover_lon", "children"),
    Output("hover_origin", "children"),
    Output("hover_alt", "children"),
    Output("hover_speed", "children"),
    Input("map", "hoverData"),
)
def update_hovered_airplane(hoverData):
    """
    Display moving panel with few position info
    next to mouse pointer when hovering airplane
    """

    callsign = ""
    lat = ""
    lon = ""
    origin = ""
    alt = ""
    speed = ""
    style = {"display": "none"}

    if hoverData is not None:
        top = hoverData["points"][0]["bbox"]["y0"]
        left = hoverData["points"][0]["bbox"]["x0"]
        callsign = hoverData["points"][0]["text"]

        try:
            # get the row in df of hovered airplane
            row = df.loc[(df.callsign == callsign), :]
            lat = row.lat
            lon = row.long
            origin = row.origin_country
            alt = row.baro_altitude
            speed = row.velocity
            logging.info(f"HOVER {callsign = }\n{row}\n{hoverData}\n")
        except IndexError as e:
            logging.error(f"{e}\n")

        # display panel shifted from the airplane
        style = {
            "display": "block",
            "top": str(top + 10) + "px",
            "left": str(left + 10) + "px",
        }

    return style, callsign, lat, lon, origin, alt, speed


@app.callback(
    Output("click_airplane", "style"),
    Output("click_callsign", "children"),
    Output("click_lat", "children"),
    Output("click_lon", "children"),
    Output("click_origin", "children"),
    Output("click_alt", "children"),
    Output("click_speed", "children"),
    Output("click_icao", "children"),
    Output("click_time", "children"),
    Output("click_last_contact", "children"),
    Output("click_true_track", "children"),
    Output("click_vertical", "children"),
    Output("click_pos_source", "children"),
    Output("alt_graph", "figure"),
    Output("map", "figure"),
    Input("map", "clickData"),
    Input("map-interval", "n_intervals"),
    Input("x_close_selection", "n_clicks"),
)
def update_clicked_airplane(clickData, n, n_clicks):
    """
    Open right side panel with full airplane info
    when airplane is clicked and close with the top-right X
    """
    global x_close_selection_clicks
    global clickData_previous
    global callsign
    global df
    global n_intervals

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
    style = {"display": "none"}
    df_altitude = pd.DataFrame(columns=["time", "altitude"])

    # values to display when clicked
    if clickData is not None:
        callsign = clickData["points"][0]["text"]
        try:
            row = df.loc[(df.callsign == callsign), :]
            lat = row.lat
            lon = row.long
            origin = row.origin_country
            alt = row.baro_altitude
            speed = row.velocity
            icao = row.icao24
            time = datetime.utcfromtimestamp(int(row.iloc[0, 3]))
            last_contact = datetime.utcfromtimestamp(int(row.iloc[0, 4]))
            true_track = row.true_track
            vertical = row.vertical_rate
            pos = row.position_source

            logging.info(f"CLICKED {callsign = }\n{row}\n{clickData}\n")
        except IndexError as e:
            logging.error(f"{callsign = }\n{e}\n")

        # get altitude data
        df_altitude = utils.get_altitudes(callsign)

        style = {"display": "block"}

    # create altitude graph
    alt_fig = px.line(
        data_frame=df_altitude,
        x="time",
        y="altitude",
        labels={"altitude": "Altitude (m)", "time": "Time"},
        title="Airplane Altitude",
        hover_name="altitude",
    )

    # close panel
    if n_clicks != x_close_selection_clicks:
        style = {"display": "none"}
        x_close_selection_clicks = n_clicks

    # update flight position
    if n_intervals != n:
        response = utils.get_opensky_flights()
        df = utils.get_opensky_df(response)
        n_intervals = n
        logging.info(f"Updated positions. Number of flights : {len(df)}")

    # add flights on the map
    map_fig = go.Figure()
    map_fig = utils.add_flights_on_map(map_fig, df)

    # add trace of the selected airplane on the map
    if clickData is not None:
        try:
            if callsign:
                df_position = utils.get_trace(callsign)
                map_fig = utils.add_flight_trace_on_map(map_fig, df_position)
                logging.debug(f"trace {callsign}: {df_position}")
                logging.debug(f"Added trace to map for flight: {callsign}")
        except IndexError as e:
            logging.error(f"{e}")

    return (
        style,
        callsign,
        lat,
        lon,
        origin,
        alt,
        speed,
        icao,
        time,
        last_contact,
        true_track,
        vertical,
        pos,
        alt_fig,
        map_fig,
    )


@app.callback(
    Output("map", "clickData"),
    Input("map_container", "n_clicks"),
)
def reset_clickData(n_clicks):
    """
    workaround to clear the clickData field and
    remove right panel when clicking anywhere on the map except
    airplane
    """
    return None


@app.callback(
    Output("dropdown_applied_filters", "style"),
    Output("select_filters_arrow", "title"),
    Input("select_filters_arrow", "n_clicks"),
    State("select_filters_arrow", "title"),
)
def toggle_applied_filters(i_arrow_clicks, s_state):
    """toggle filter box"""

    o_style = {"display": "none"}
    if i_arrow_clicks is not None:
        if s_state == "is_open":
            o_style = {"display": "none"}
            s_state = "is_closed"
        else:
            o_style = {"display": "block"}
            s_state = "is_open"

    return o_style, s_state


@app.callback(
    Output("fields_for_applied_filters", "style"),
    Output("input_flightnumber", "style"),
    Output("input_departure", "style"),
    Output("input_arrival", "style"),
    Output("input_airport", "style"),
    Input("filters_drop", "value"),
)
def toggle_fields(i_dd_value):
    """toggle fields depending on filter selected"""

    o_fields_style = {"display": "none"}
    o_input_flightnumber_style = {"display": "none"}
    o_input_departure_style = {"display": "none"}
    o_input_arrival_style = {"display": "none"}
    o_input_airport_style = {"display": "none"}

    if i_dd_value is not None:
        o_fields_style = {"display": "block"}
        if i_dd_value == "By Flight":
            o_input_flightnumber_style = {"display": "block"}
        elif i_dd_value == "By Route":
            o_input_departure_style = {"display": "block"}
            o_input_arrival_style = {"display": "block"}
        elif i_dd_value == "By Airports":
            o_input_airport_style = {"display": "block"}

    return (
        o_fields_style,
        o_input_flightnumber_style,
        o_input_departure_style,
        o_input_arrival_style,
        o_input_airport_style,
    )


@app.callback(
    Output("airport_panel", "style"),
    Output("arrivals_table", "children"),
    Output("departures_table", "children"),
    Output("airport_infos", "children"),
    Output("input_airport", "value"),
    Input("submit_val", "n_clicks"),
    Input("map_container", "n_clicks"),
    Input("x_close_airport", "n_clicks"),
    State("input_airport", "value"),
)
def display_airport_panel(i_sub_clicks, i_map_clicks, i_close_clicks, i_value):
    """
    display airport panel based on airport field value
    when submit button is clicked
    """

    global submit_clicks
    global map_n_clicks
    global x_close_airport_clicks

    o_style = {"display": "none"}
    df_arr = ""
    df_dep = ""
    o_arrivals_tbl = ""
    o_departures_tbl = ""
    o_airport_name = ""
    o_in_airport = ""

    if (
        ((map_n_clicks == i_map_clicks) or i_map_clicks is None)
        and (i_sub_clicks != submit_clicks)
        and not (i_value is None or i_value == "")
    ):
        o_style = {"display": "block"}
        submit_clicks = i_sub_clicks

        df_arr = utils.get_arrivals(i_value)
        df_dep = utils.get_departures(i_value)

        o_arrivals_tbl = dash_table.DataTable(
            data=df_arr.to_dict("records"),
            columns=[{"name": i, "id": i} for i in df_arr.columns],
            style_as_list_view=True,
            style_header={
                "backgroundColor": "cornflowerblue",
                "color": "white",
                "fontWeight": "bold",
            },
            style_cell_conditional=[
                {"if": {"column_id": c}, "textAlign": "center"}
                for c in df_arr.columns
            ],
            style_data_conditional=[
                {
                    "if": {"row_index": "odd"},
                    "backgroundColor": "rgb(220, 220, 220)",
                }
            ],
            page_size=10,
        )
        o_departures_tbl = dash_table.DataTable(
            data=df_dep.to_dict("records"),
            columns=[{"name": i, "id": i} for i in df_dep.columns],
            style_as_list_view=True,
            style_header={
                "backgroundColor": "cornflowerblue",
                "color": "white",
                "fontWeight": "bold",
            },
            style_cell_conditional=[
                {"if": {"column_id": c}, "textAlign": "center"}
                for c in df_dep.columns
            ],
            style_data_conditional=[
                {
                    "if": {"row_index": "odd"},
                    "backgroundColor": "rgb(220, 220, 220)",
                }
            ],
            page_size=10,
        )

        try:
            o_airport_name = utils.get_airport_infos(i_value)[0]
        except IndexError as e:
            logging.error(f"Error while getting airport infos.\n{e}")
            o_airport_name = ""

        o_airport_name = i_value.upper() + " (" + o_airport_name + ")"

    else:
        map_n_clicks = i_map_clicks

    # close panel
    if i_close_clicks != x_close_airport_clicks:
        o_style = {"display": "none"}
        x_close_airport_clicks = i_close_clicks

    return (
        o_style,
        o_arrivals_tbl,
        o_departures_tbl,
        o_airport_name,
        o_in_airport,
    )


@app.callback(
    Output("route_panel", "style"),
    Output("airline_route", "children"),
    Output("flightnumber_route", "children"),
    Output("arr_dep_city", "children"),
    Output("dep_iata_route", "children"),
    Output("dep_airport_route", "children"),
    Output("dep_time_route", "children"),
    Output("arr_iata_route", "children"),
    Output("arr_airport_route", "children"),
    Output("arr_time_route", "children"),
    Output("input_departure", "value"),
    Output("input_arrival", "value"),
    Input("submit_val", "n_clicks"),
    Input("map_container", "n_clicks"),
    Input("x_close_route", "n_clicks"),
    State("input_departure", "value"),
    State("input_arrival", "value"),
)
def display_route_panel(
    i_sub_clicks, i_map_clicks, i_close_clicks, s_dep_value, s_arr_value
):
    """
    display route panel based on airport fields value
    when submit button is clicked
    """

    global submit_clicks
    global map_n_clicks
    global x_close_route_clicks

    # default style
    o_style = {"display": "none"}
    o_airline = ""
    o_flightnumber = ""
    o_arr_dep_route = ""
    o_dep_iata = ""
    o_arr_iata = ""
    o_dep_airport = ""
    o_arr_airport = ""
    o_dep_time = ""
    o_arr_time = ""

    # remove input fields text from filter
    in_dep = ""
    in_arr = ""

    # get routes infos
    if (
        ((map_n_clicks == i_map_clicks) or i_map_clicks is None)
        and (i_sub_clicks != submit_clicks)
        and not (
            (s_dep_value is None)
            or (s_dep_value == "")
            or (s_arr_value is None)
            or (s_arr_value == "")
        )
    ):
        submit_clicks = i_sub_clicks

        o_style = {"display": "block"}

        try:
            df_flight = utils.get_routes(s_dep_value, s_arr_value).iloc[:1, :]

            if not df_flight.empty:
                o_airline = df_flight["airline_name"]
                o_flightnumber = df_flight["flight"]
                o_arr_dep_route = (
                    df_flight["dep_city"] + " --> " + df_flight["arr_city"]
                )
                o_dep_iata = s_dep_value.upper()
                o_arr_iata = s_arr_value.upper()
                o_dep_airport = df_flight["dep_airport"]
                o_arr_airport = df_flight["arr_airport"]
                o_dep_time = df_flight["dep_scheduled"]
                o_arr_time = df_flight["arr_scheduled"]
            else:
                o_airline = "NOT FOUND"
        except Exception as e:
            logging.error(f"No routes found.\n{e}")

    else:
        map_n_clicks = i_map_clicks

    # close panel
    if i_close_clicks != x_close_route_clicks:
        o_style = {"display": "none"}
        x_close_route_clicks = i_close_clicks

    return (
        o_style,
        o_airline,
        o_flightnumber,
        o_arr_dep_route,
        o_dep_iata,
        o_dep_airport,
        o_dep_time,
        o_arr_iata,
        o_arr_airport,
        o_arr_time,
        in_dep,
        in_arr,
    )


# main
if __name__ == "__main__":
    app.run(host=os.getenv("HOST", "0.0.0.0"), port="8050", debug=DEBUG)
