# -*- coding: utf-8 -*-
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
import yaml
from iriscovid19 import IRISCOVID19
import cProfile

#todo: create a class that convert yaml to global
#todo: create a class that convert global to yaml
try:
    with open("../data/config.yaml", "r") as file:
        config = yaml.safe_load(file)
except Exception as e:
    print('Error reading the config file')

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
app = dash.Dash(__name__, external_stylesheets=external_stylesheets, suppress_callback_exceptions=True)

#Class with IRIS Persistence
iriscovid19 = IRISCOVID19()
iriscovid19.deaths_file_path = config["file"]["covid19_deaths_global"]
iriscovid19.countries_lookup_file_path = config["file"]["countries_lookup"]
iriscovid19.iris_config = config["iris"]
iriscovid19.set_default_countries(config["covid19_app"]["default_countries"])
iriscovid19.import_countries_lookup()
iriscovid19.import_global_deaths()
iriscovid19.process_global_deaths()

'''
Page Layouts
'''

def get_index_layout():
    return html.Div([
                html.H1(children='IRIS Python Suite'),
                # represents the URL bar, doesn't render anything
                dcc.Link('COVID-19 Chart Example "/covid19-chart"', href='/covid19-chart'),
                html.Br(),
                dcc.Link('Global CRUD Example "/config-CRUD"', href='/config-CRUD'),
                html.Br(),
                dcc.Link('Reset Data (Dont Panic!) "/reset-data"', href='/reset-data'),
                html.Br()
    ])

def get_config_crud_layout():
    default_countries = iriscovid19.get_default_countries()
    dropdown_countries = iriscovid19.get_dash_formatted_countries()

    return html.Div(children=[
        html.H1(children='Example of CRUD - Modifying the Default Config in IRIS Global'),
        html.P(children='''Change the default countries to show on COVID-19 Chart'''),
        html.Div([
            # represents the URL bar, doesn't render anything
            dcc.Location(id='url', refresh=False),
            html.Br(),
            dcc.Link('COVID-19 Chart Example "/covid19-chart"', href='/covid19-chart'),
            html.Br()
        ]),
        html.Div(children=[
            html.Label('Default Countries (auto save)'),
            dcc.Dropdown(id='countries-dropdown-CRUD',
                         options=dropdown_countries,
                         value=default_countries,
                         multi=True),
            html.Div(id='result-crud')
        ])])

def get_covid19_layout():
    dropdown_countries = iriscovid19.get_dash_formatted_countries()
    default_countries = iriscovid19.get_default_countries()
    return html.Div(children=[
        html.H1(children='IRIS Native API + Python + JHU Data'),
        html.Div(children='''
                Starting using IRIS Native API by Banzai
            '''),
        html.Div([
            # represents the URL bar, doesn't render anything
            html.Br(),
            dcc.Link('Global CRUD Example "/config-CRUD"', href='/config-CRUD'),
            html.Br(),
            dcc.Link('Main Menu "/"', href='/'),
            html.Br()
        ]),
        html.Div(children=[
            html.Label('Countries'),
            dcc.Dropdown(
                id='countries-dropdown',
                options=dropdown_countries,
                value=default_countries,
                multi=True
            ),
            dcc.RadioItems(
                id='yaxis-type',
                options=[{'label': i, 'value': i} for i in ['Linear', 'Log']],
                value='Linear',
                labelStyle={'display': 'inline-block'}
            ),
            dcc.RadioItems(
                id='time-series-type',
                options=[{'label': i[1], 'value': i[0]} for i in [('timeless', 'Days After 1st Death'),('date', 'Real Dates')]],
                value='timeless',
                labelStyle={'display': 'inline-block'}
            )
        ]),
        dcc.RadioItems(
            id='count-type',
            options=[{'label': i[1], 'value': i[0]} for i in [('rate', 'Rate (Deaths per 100 000 people)'), ('total', 'Total Deaths')]],
            value='rate',
            labelStyle={'display': 'inline-block'}
        ),
        html.Div(
        dcc.Graph(
            id='covid-graph',
            figure={
                'layout': {
                    'title': 'COVID-19 Comparison'
                }
            }
        ))
    ])

def get_reset_data_layout():
    try:
        with open("../data/config.yaml", "r") as file:
            config = yaml.safe_load(file)
    except Exception as e:
        print('Error reading the config file')

    iriscovid19 = IRISCOVID19()
    iriscovid19.deaths_file_path = config["file"]["covid19_deaths_global"]
    iriscovid19.countries_lookup_file_path = config["file"]["countries_lookup"]
    iriscovid19.iris_config = config["iris"]
    iriscovid19.set_default_countries(config["covid19_app"]["default_countries"])
    iriscovid19.import_countries_lookup()
    iriscovid19.import_global_deaths()
    iriscovid19.process_global_deaths()
    return html.Div([
                html.H1(children='Data Reseted! Dont Panic!'),
                html.H3(children='Data ingested from  ../data files to IRIS Database!'),
                html.H3(children='Reset config to Banzais Default!'),
                # represents the URL bar, doesn't render anything
                html.Br(),
                dcc.Link('COVID-19 Chart Example "/covid19-chart"', href='/covid19-chart'),
                html.Br(),
                dcc.Link('Global CRUD Example "/config-CRUD"', href='/config-CRUD'),
                html.Br(),
                dcc.Link('Main menu "/"', href='/'),
                html.Br()
    ])

'''
Input Callbacks
'''


@app.callback(Output('result-crud', 'children'),[Input('countries-dropdown-CRUD', 'value')])
def update_countries_default(countries):
    iriscovid19.set_default_countries(countries)
    return 'Actually the global ^config("defaultcountries") has the value: ' \
           + ','.join(iriscovid19.get_default_countries())

@app.callback(Output('covid-graph', 'figure'),
              [Input('yaxis-type', 'value'),
                Input('countries-dropdown', 'value'),
                Input('time-series-type', 'value'),
                Input('count-type', 'value')
               ])
def update_graph(yaxis_type, countries, time_series_type, count_type, suppress_callback_exceptions=True):
    plotly_data = iriscovid19.get_plotly_formatted_time_series(countries, time_series_type, count_type)
    return {
                'data': plotly_data,
                'layout': {
                    'title': 'COVID-19 Comparison',
                    'yaxis': {'title': "Deaths Total" if count_type=="total" else "Rate (Deaths per 100 000 people)",
                              'type': yaxis_type.lower()
                              },
                    'xaxis': {'title': 'Days after 1st Death' if time_series_type=="timeless" else "Date"}
                }
            }

# Update the index
@app.callback(dash.dependencies.Output('page-content', 'children'),
              [dash.dependencies.Input('url', 'pathname')])
def display_page(pathname, suppress_callback_exceptions=True):
    if pathname == '/config-CRUD':
        return get_config_crud_layout()
    elif pathname == '/covid19-chart':
        return get_covid19_layout()
    elif pathname == '/reset-data':
        return get_reset_data_layout()
    else:
        return get_index_layout()

if __name__ == '__main__':
    app.layout = html.Div([dcc.Location(id='url', refresh=False), html.Div(id='page-content')])
    app.run_server(debug=True,host='0.0.0.0')