import json
import pandas as pd
import plotly.graph_objects as go
import requests
from dash import dcc, html
from dash.dependencies import Input, Output
import dash_bootstrap_components as dbc
from flask import Flask
from dash import Dash
from base_map import MilitaryBasesMap  # Ensure the base_map module is accessible


class AllianceMap:
    def __init__(self, dataset_path=None, bases_path=None):
        if dataset_path is None:
            dataset_path = '~/Workspace/dv/final_project/final/data/US_China_Alliances_Partnerships.csv'
        self.df_alliances = pd.read_csv(dataset_path)
        # Determine overlaps
        self.df_alliances = self.df_alliances.groupby('country2').apply(self.aggregate_relations).reset_index()

        self.geojson = self.fetch_geojson()
        self.change_json_id_to_name()

    @staticmethod
    def aggregate_relations(group):
        if 'US' in group['country1'].values and 'China' in group['country1'].values:
            country1 = 'Both'
        else:
            country1 = ' / '.join(set(group['country1']))

        type_combined = ' / '.join(set(group['type']))  # Combine unique types
        goal_combined = ' / '.join(set(group['goal']))  # Combine unique goals
        organization_combined = ' / '.join(set(group['organization']))  # Combine unique organizations

        return pd.Series({
            'country1': country1,
            'type': type_combined,
            'goal': goal_combined,
            'organization': organization_combined
        })

    @staticmethod
    def assign_color(country1):
        if country1 == 'Both':
            return 0  # Purple for both
        elif country1 == 'US':
            return -1  # Blue for USA
        elif country1 == 'China':
            return 1  # Red for China

    def create_map(self):
        fig = go.Figure()

        # Create the Choropleth map trace
        alliance_trace = go.Choroplethmapbox(
            geojson=self.geojson,
            locations=self.df_alliances['country2'],
            z=self.df_alliances['country1'].apply(self.assign_color),
            colorscale=[(-1, 'blue'), (0, 'purple'), (1, 'red')],
            text=self.df_alliances.apply(lambda x: f"{x['type']} / {x['goal']} / {x['organization']}", axis=1),
            marker_line_color='black',
            marker_line_width=0.5,
            colorbar=dict(
                title='Type of Relation',
                tickvals=[-1, 0, 1],
                ticktext=['US', 'Both', 'China']
            )
        )

        fig.add_trace(alliance_trace)

        # Configure map layout
        fig.update_layout(
            mapbox_style="carto-positron",
            mapbox_zoom=1,
            mapbox_center={"lat": 20, "lon": 0},
            margin={"r": 0, "t": 0, "l": 0, "b": 0}
        )

        return fig

    @staticmethod
    def fetch_geojson():
        url = "https://raw.githubusercontent.com/johan/world.geo.json/master/countries.geo.json"
        response = requests.get(url)
        return response.json()

    def change_json_id_to_name(self):
        # Change the 'id' field to 'name' in the GeoJSON
        for feature in self.geojson['features']:
            feature['id'] = feature['properties']['name']

