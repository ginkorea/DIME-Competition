import dash
from dash import dcc, html, Input, Output, State
import plotly.graph_objects as go
import pandas as pd
from dash_bootstrap_components.themes import BOOTSTRAP
from flask import Flask
from milexpend import prepare_and_plot_data
from investment_tracker import generate_cumulative_investment_chart
import dash_bootstrap_components as dbc

from datamanager import DataManager, TreeDiagram
from mapper import CombinedMap

# Initializing the Flask server
server = Flask(__name__)

# Initializing the Dash app with the Flask server
app = dash.Dash(__name__, server=server, external_stylesheets=[BOOTSTRAP], suppress_callback_exceptions=True)
app.title = "PRC/US Great Power Competition Dashboard"


# Define the paths to datasets
dataset_paths = {
    "combined": '~/Workspace/dv/final_project/final/data/Investments_and_construction.csv',
    "construction": '~/Workspace/dv/final_project/final/data/Construction.csv',
    "investments": '~/Workspace/dv/final_project/final/data/Investments.csv',
    "military_expenditure": '~/Workspace/dv/final_project/final/data/SIPRI-Milex-data-1992-2023.xlsx',
    'investment_tracker': '~/Workspace/dv/final_project/final/data/China-Global-Investment-Tracker-2023-Fall.xlsx'
}

# Initialize data managers
data_manager = DataManager(dataset_paths['combined'])
combined_map = CombinedMap(dataset_paths['investments'], dataset_paths['construction'], dataset_paths['combined'])

# Preprocess map data
combined_map.preprocess_data()

# Columns for the hierarchy selector in Sunburst view
all_columns = ['Country', 'Sector', 'Subsector', 'Investor', 'Transaction Party', 'Region']

# Define the navigation menu using dbc components for better styling
navbar = dbc.Nav(
    [
        dbc.NavLink("China Investments and Construction Sunburst", href="/sunburst", active="exact"),
        dbc.NavLink("Map of Chinese Investments and World Overseas Military Bases", href="/map", active="exact"),
        dbc.NavLink("Military Expenditure Analysis", href="/military-expenditure", active="exact"),
        dbc.NavLink("Investment Tracker Analysis", href="/investment-tracker", active="exact"),
    ],
    vertical=True,
    pills=True,  # This option gives a highlight to active link
    style={"font-size": "20px", "width": "250px"}  # Adjust width as per your layout requirement
)

app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    dbc.Row([
        dbc.Col(navbar, width=2),  # Navigation sidebar taking 2 columns of the grid
        dbc.Col(html.Div(id='page-content'), width=10)  # Content taking the rest 10 columns of the grid
    ], style={'height': '100vh'}),  # Adjust height to viewport height
], style={'backgroundColor': '#303030', 'color': '#FFFFFF'})


@app.callback(Output('page-content', 'children'),
              [Input('url', 'pathname')])
def display_page(pathname):
    if pathname == '/map':
        fig = combined_map.create_map()
        fig.update_layout(mapbox_style="dark", height=700)  # Update the map style and height
        return html.Div([
            html.H1("Map of Chinese Investments and World Overseas Military Bases", style={'color': 'white'}),
            dcc.Graph(figure=fig)
        ])
    elif pathname == '/sunburst':
        return html.Div([
            html.H1("China Investments and Construction Sunburst", className="text-light"),
            dcc.Dropdown(
                id='dataset-selector',
                options=[{'label': k, 'value': v} for k, v in dataset_paths.items()],
                value=dataset_paths['combined'],
                clearable=False,
                className="mb-3"
            ),
            dcc.Dropdown(
                id='hierarchy-selector',
                options=[{'label': col, 'value': col} for col in all_columns],
                value=['Country', 'Sector'],
                multi=True,
                className="mb-3"
            ),
            html.H3(id='sunburst-title', className="text-light"),
            dcc.Graph(id='tree-diagram'),
            dcc.Store(id='stored-data', data=data_manager.get_data().to_json(date_format='iso', orient='split')),
            dcc.Store(id='current-path', data=[]),
            html.Button("Back", id="back-button", n_clicks=0, className="btn btn-secondary"),
            html.Div(id="path-display", className="text-light")
        ])
    elif pathname == '/military-expenditure':
        fig = prepare_and_plot_data(dataset_paths['military_expenditure'])
        return html.Div([
            html.H1("Military Expenditure Analysis"),
            dcc.Graph(figure=fig)
        ])
    elif pathname == '/investment-tracker':
        fig = generate_cumulative_investment_chart(dataset_paths['investment_tracker'])
        return html.Div([
            html.H1("Investment Tracker Analysis"),
            dcc.Graph(figure=fig)
        ])
    else:
        return html.Div([
            html.H3("Please select a view.", style={'color': 'white'}),
            html.Br(),
            html.Img(src='landing_image.png')
        ])


@app.callback(
    [Output('tree-diagram', 'figure'),
     Output('current-path', 'data'),
     Output('sunburst-title', 'children')],
    [Input('dataset-selector', 'value'),
     Input('tree-diagram', 'clickData'),
     Input('back-button', 'n_clicks'),
     Input('hierarchy-selector', 'value')],
    [State('stored-data', 'data'),
     State('current-path', 'data')]
)
def update_graph(dataset_path, clickData, back_clicks, selected_hierarchy, json_data, current_path):
    ctx = dash.callback_context
    triggered_id = ctx.triggered[0]['prop_id'].split('.')[0]
    data = pd.read_json(json_data, orient='split')

    if triggered_id == 'dataset-selector':
        _data_manager = DataManager(dataset_path)
        data = _data_manager.get_data()
        json_data = data.to_json(date_format='iso', orient='split')
        current_path = []  # Reset the path for new data

    if 'back-button' in triggered_id and current_path:
        current_path.pop()
    elif clickData and 'tree-diagram' in triggered_id:
        current_path.append(clickData['points'][0]['label'])

    if not current_path:
        filtered_data = data
        next_level = selected_hierarchy[:1]
    else:
        filtered_data = data
        for i, level in enumerate(current_path):
            filtered_data = filtered_data[filtered_data[selected_hierarchy[i]] == level]
        next_index = len(current_path)
        next_level = selected_hierarchy[next_index:next_index + 1] if next_index < len(selected_hierarchy) else []

    if not next_level:
        fig = go.Figure()
        title_text = "Select a node to see further details"
    else:
        tree_diagram = TreeDiagram(filtered_data)
        fig = tree_diagram.create_tree(next_level)
        title_text = " > ".join(current_path) if current_path else " > ".join(selected_hierarchy[:1])

    return fig, current_path, title_text


@app.callback(
    Output('path-display', 'children'),
    [Input('current-path', 'data')]
)
def update_path_display(current_path):
    return " > ".join(current_path) if current_path else "Select a node to see further details."


if __name__ == '__main__':
    app.run_server(debug=True)
