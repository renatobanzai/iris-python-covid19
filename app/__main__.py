# -*- coding: utf-8 -*-
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
import yaml
from iriscovid19 import IRISCOVID19

#todo: create a class that convert yaml to global
#todo: create a class that convert global to yaml
try:
    with open("../data/config.yaml", "r") as file:
        config = yaml.safe_load(file)
except Exception as e:
    print('Error reading the config file')

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

#Class with IRIS Persistence
iriscovid19 = IRISCOVID19()
iriscovid19.deaths_file_path = config["file"]["covid19_deaths_global"]
iriscovid19.countries_lookup_file_path = config["file"]["countries_lookup"]
iriscovid19.iris_config = config["iris"]
iriscovid19.import_countries_lookup()
iriscovid19.import_global_deaths()
iriscovid19.process_global_deaths()

def get_layout(dropdown_countries):
    return html.Div(children=[
        html.H1(children='IRIS Native API + Python + JHU Data'),
        html.Div(children='''
                Starting using IRIS Native API by Banzai
            '''),
        html.Div(children=[
            html.Label('Countries'),
            dcc.Dropdown(
                id='countries-dropdown',
                options=dropdown_countries,
                value=['brazil', 'sweden', 'united kingdom'],
                multi=True
            ),
            dcc.RadioItems(
                id='yaxis-type',
                options=[{'label': i, 'value': i} for i in ['Linear', 'Log']],
                value='Linear',
                labelStyle={'display': 'inline-block'}
            )
        ]),
        html.Div(
        dcc.Graph(
            id='covid-graph',
            figure={
                'layout': {
                    'title': 'COVID-19 Comparison',
                    'yaxis': {'title': 'Deaths'},
                    'xaxis': {'title': 'Days after 1st Death'}
                }
            }
        ))
    ])

def plot_data(countries=[]):
    dropdown_countries = iriscovid19.get_dash_formatted_countries()
    app.layout = get_layout(dropdown_countries)

@app.callback(Output('covid-graph', 'figure'),
              [Input('yaxis-type', 'value'),
                Input('countries-dropdown', 'value')])
def update_graph(yaxis_type, countries):
    plotly_data = iriscovid19.get_plotly_formatted_time_series(countries)
    return {
                'data': plotly_data,
                'layout': {
                    'title': 'COVID-19 Comparison',
                    'yaxis': {'title': 'Total COVID-19 Deaths',
                              'type': yaxis_type.lower()
                              },
                    'xaxis': {'title': 'Days after 1st Death'}
                }
            }

if __name__ == '__main__':
    plot_data()
    app.run_server(debug=True,host='0.0.0.0')