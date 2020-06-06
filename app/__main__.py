# -*- coding: utf-8 -*-
import dash
import dash_table
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
import yaml
from iriscovid19 import IRISCOVID19
from iris_python_suite import irisglobal, irisdomestic, irisglobalchart
import networkx as nx
import dash_bootstrap_components as dbc

#todo: demonstrate a profile of different aproachs in code

try:
    with open("../data/config.yaml", "r") as file:
        config = yaml.safe_load(file)
except Exception as e:
    print('Error reading the config file')

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP], suppress_callback_exceptions=True)

#Class with IRIS Persistence
obj_irisdomestic = irisdomestic(config["iris"])


iriscovid19 = IRISCOVID19()
iriscovid19.deaths_file_path = config["file"]["covid19_deaths_global"]
iriscovid19.countries_lookup_file_path = config["file"]["countries_lookup"]
iriscovid19.iris_config = config["iris"]
iriscovid19.iris_connection = obj_irisdomestic.iris_connection
iriscovid19.set_default_countries(config["covid19_app"]["default_countries"])
iriscovid19.import_countries_lookup()
iriscovid19.import_global_deaths()
iriscovid19.process_global_deaths()
default_countries = iriscovid19.get_default_countries()
dropdown_countries = iriscovid19.get_dash_formatted_countries()



def populate_global_for_chart():
    obj_irisdomestic.set(0, "^computer", "hardware", "input","keyborad")
    obj_irisdomestic.set(0, "^computer", "hardware", "input","usb drive")
    obj_irisdomestic.set(0, "^computer", "hardware", "input","mouse")
    obj_irisdomestic.set(0, "^computer", "hardware", "input","webcam")
    obj_irisdomestic.set(0, "^computer", "hardware", "output","screen")
    obj_irisdomestic.set(0, "^computer", "hardware", "output","printer")
    obj_irisdomestic.set(0, "^computer", "hardware", "output","soundbox")
    obj_irisdomestic.set(0, "^computer", "software", "os")
    obj_irisdomestic.set(0, "^computer", "software", "os", "linux")
    obj_irisdomestic.set(0, "^computer", "software", "os", "linux", "ubuntu")
    obj_irisdomestic.set(0, "^computer", "software", "os", "linux", "alpine")
    obj_irisdomestic.set(0, "^computer", "software", "os", "linux", "centOS")
    obj_irisdomestic.set(0, "^computer", "software", "os", "linux", "Debian")
    obj_irisdomestic.set(0, "^computer", "software", "os", "unix")
    obj_irisdomestic.set(0, "^computer", "software", "os", "macOS", "iEverything")
    obj_irisdomestic.set(0, "^computer", "software", "os", "windows", "ms office")
    obj_irisdomestic.set(0, "^computer", "software", "os", "windows", "ms paint")
    obj_irisdomestic.set(0, "^computer", "software", "os", "windows", "a lot games")

populate_global_for_chart()

'''
Page Layouts
'''

def get_index_layout():
    return html.Div([
                html.H1(children='IRIS Python Suite'),
                html.Div([
                    dbc.NavItem(dbc.NavLink("Global View Graph", href="/global-chart")),
                    dbc.NavItem(dbc.NavLink("COVID-19 Chart", href="/covid19-chart")),
                    dbc.NavItem(dbc.NavLink("Config CRUD", href="/config-CRUD")),
                    dbc.NavItem(dbc.NavLink("Reset Data (Dont Panic!)", href="/reset-data")),
                    dbc.NavItem(dbc.NavLink("Vote in iris-python-suite!",
                                            href="https://openexchange.intersystems.com/contest/current",
                                            target="_blank"))
                ])
                # represents the URL bar, doesn't render anything
    ])

def get_config_crud_layout():
    default_countries = iriscovid19.get_default_countries()
    return html.Div(children=[
        html.H1(children='Example of CRUD - Modifying the Default Config in IRIS Global'),
        html.P(children='''Change the default countries to show on COVID-19 Chart'''),
        html.Div(children=[
            html.Label('Default Countries (auto save)'),
            dcc.Dropdown(id='countries-dropdown-CRUD',
                         options=dropdown_countries,
                         value=default_countries,
                         multi=True),
            html.Div(id='result-crud')
        ])])

def get_covid19_layout():
    default_countries = iriscovid19.get_default_countries()
    return html.Div(children=[
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

    iriscovid19.deaths_file_path = config["file"]["covid19_deaths_global"]
    iriscovid19.countries_lookup_file_path = config["file"]["countries_lookup"]
    iriscovid19.iris_config = config["iris"]
    iriscovid19.set_default_countries(config["covid19_app"]["default_countries"])
    iriscovid19.import_countries_lookup()
    iriscovid19.import_global_deaths()
    iriscovid19.process_global_deaths()
    populate_global_for_chart()

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
                html.Br(),
        html.Div(
            dcc.Graph(
                id='global-graph',
                figure={
                    'layout': {
                        'title': ''
                    }
                }
            ))
    ])

def get_global_chart_layout():
    return html.Div(children=[
        html.Div([
            html.Br(),
            html.Label('Type a global array separated by "," e.g: ^computer'),
            dcc.Input(
                id="txt_global_chart",
                type="text",
                placeholder="^computer",
                value="^computer"
            )]
        ),
        html.Div(
            dcc.Graph(id="global-chart-graph")
        )
    ])

def get_chatbot_training_layout():
    return html.Div(children=[
        html.Div([
            html.Br(),
            html.P('Questions and answers to training the Banzairis Bot')]),
        html.Div(children=[
            html.Label('Countries'),
            dcc.Dropdown(
                id='training-country',
                options=[{"label":x, "value":"^chatbot.training.data."+x} for x in ["english", "russian", "portuguese", "spanish"]],
                value="^chatbot.training.data.english",
                multi=False
            )]),
            dash_table.DataTable(
            id='table-chatbot',
            columns=[{"name": "Question", "id": "question"},{"name": "Answer", "id": "answer"}],
            editable=True
        ),
        html.Button('Add Row', id='editing-rows-button', n_clicks=0),
        html.Button('SAVE THE DATA', id='save-rows-button', n_clicks=0),
        html.Div(id="table-editing-simple-output")
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

@app.callback(Output('global-chart-graph', 'figure'),
              [Input('txt_global_chart', 'value')])
def update_global_chart(global_text):
    global_array = tuple([x.strip() for x in global_text.split(",")])
    obj_nx = nx.Graph()
    global_chart = obj_irisdomestic.view_global_chart(obj_nx=obj_nx, *global_array)
    fig = global_chart.get_fig()
    return fig

@app.callback(
    Output('table-chatbot', 'data'),
    [Input('editing-rows-button', 'n_clicks'),
    Input('training-country', 'value')],
    [State('table-chatbot', 'columns')])
def add_row(n_clicks, global_training_country, columns):
    questions = obj_irisdomestic.iterator(global_training_country, "question")
    rows = []
    for question, answer in questions:
        rows.append({"question": question, "answer": answer})
    if dash.callback_context.triggered[0]['prop_id'].split('.')[0] ==  "editing-rows-button":
        if n_clicks > 0:
            rows.append({c['id']: '' for c in columns})
    return rows

@app.callback(
    Output('table-editing-simple-output', 'children'),
    [Input('save-rows-button', 'n_clicks')],
    [State('table-chatbot', 'data'),
     State('training-country', 'value')])
def save_data(n_clicks, data, global_training_country):
    if n_clicks > 0:
        for register in data:
            obj_irisdomestic.set(register["answer"], global_training_country, "question", register["question"])
            obj_irisdomestic.set("0", global_training_country, "isupdated")
        return "data saved"
    else:
        return ""




# Update the index
@app.callback(dash.dependencies.Output('page-content', 'children'),
              [dash.dependencies.Input('url', 'pathname')])
def display_page(pathname, suppress_callback_exceptions=True):
    if pathname == '/config-CRUD':
        return get_config_crud_layout()
    elif pathname == '/covid19-chart':
        return get_covid19_layout()
    elif pathname == '/global-chart':
        return get_global_chart_layout()
    elif pathname == '/reset-data':
        return get_reset_data_layout()
    elif pathname == '/chatbot-training-data':
        return get_chatbot_training_layout()
    else:
        return get_index_layout()

navbar = dbc.NavbarSimple(id="list_menu_content",
    children=[
        dbc.NavItem(dbc.NavLink("Global View Graph", href="/global-chart")),
        dbc.NavItem(dbc.NavLink("COVID-19 Chart", href="/covid19-chart")),
        dbc.NavItem(dbc.NavLink("Config CRUD", href="/config-CRUD")),
        dbc.NavItem(dbc.NavLink("Chatbot Training Data", href="/chatbot-training-data")),
        dbc.NavItem(dbc.NavLink("Talk with Chatbot", href="http://localhost:8080", target="_blank")),
        dbc.NavItem(dbc.NavLink("Vote in iris-python-suite!",
                                href="https://openexchange.intersystems.com/contest/current", target="_blank"))
    ],
    brand="IRIS Python Examples - by Banzai",
    brand_href="/",
    color="dark",
    dark=True,
)

if __name__ == '__main__':
    app.layout = html.Div([dcc.Location(id='url', refresh=False),
                          html.Div(navbar),
                          html.Div(id='page-content')])
    app.run_server(debug=False,host='0.0.0.0')