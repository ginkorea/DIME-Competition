import json
import pandas as pd
import plotly.graph_objects as go
import requests
from base_map import MilitaryBasesMap  # Ensure the base_map module is accessible


class CombinedMap:
    def __init__(self, dataset1_path=None, dataset2_path=None, combined_path=None, bases_path=None):
        # Load investment datasets
        self.df_dataset1 = pd.read_csv(dataset1_path or 'data/Investments.csv')
        self.df_dataset2 = pd.read_csv(dataset2_path or 'data/Construction.csv')
        self.df_combined = pd.read_csv(combined_path or 'data/Investments_and_construction.csv')

        # Initialize and prepare military bases data
        self.military_map = MilitaryBasesMap(bases_path)
        self.military_map.assign_colors()

        # Fetch GeoJSON data for countries
        self.geojson = self.fetch_geojson()
        self.change_json_id_to_name()

    @staticmethod
    def create_choropleth(df, title, geojson):
        # Create a choropleth map for a given dataset
        return go.Choroplethmapbox(
            geojson=geojson,  # Use the GeoJSON data for countries how do I use name of the variable here?
            ## use 'name' instead of 'id' in the GeoJSON features
            locations=df['Country'],  # Make sure this matches the 'id' in your GeoJSON features
            z=df['Quantity in Millions'],
            colorscale='Reds',
            marker_line_color='darkgray',
            marker_line_width=0.5,
            colorbar_title='Investment<br>Millions USD',
            name=title,
            showscale=True  # Show color scale
        )

    @staticmethod
    def fetch_geojson():
        url = "https://raw.githubusercontent.com/johan/world.geo.json/master/countries.geo.json"
        response = requests.get(url)
        return response.json()

    def change_json_id_to_name(self):
        special_countries = {
            'USA': "USA",
            "RUS": "Russian Federation",
            'GBR': 'Britain',
            'TZA': 'Tanzania',
        }
        # Change the 'id' field to 'name' in the GeoJSON
        for feature in self.geojson['features']:
            if feature['id'] not in special_countries:
                feature['id'] = feature['properties']['name']
            else:
                feature['id'] = special_countries[feature['id']]

    def preprocess_data(self):
        self.summary_dataset1 = self.df_dataset1.groupby('Country')['Quantity in Millions'].sum().reset_index()
        self.summary_dataset2 = self.df_dataset2.groupby('Country')['Quantity in Millions'].sum().reset_index()
        self.summary_combined = self.df_combined.groupby('Country')['Quantity in Millions'].sum().reset_index()

    import plotly.graph_objects as go



    def create_map(self):
        fig = go.Figure()

        # Custom colorscale with transparency
        rd_bu_transparent = [
            [0.0, 'rgba(5, 10, 172, 0.6)'],  # Blue, less opaque
            [0.5, 'rgba(255, 255, 255, 0.6)'],  # White, midpoint
            [1.0, 'rgba(178, 10, 28, 0.6)']  # Red, less opaque
        ]

        # Add choropleth layers without setting zmax here
        traces = [
            go.Choroplethmapbox(
                geojson=self.geojson,
                locations=self.summary_dataset1['Country'],
                z=self.summary_dataset1['Quantity in Millions'],
                colorscale=rd_bu_transparent,
                zmin=0,
                marker_line_color='black',
                marker_line_width=0.2,
                colorbar_title='Millions USD',
                name='Investments',
                colorbar=dict(
                    title='Millions USD',
                    x=1,  # Position the colorbar to the right of the map
                    xanchor='left',
                    titleside='right'
                ),
                visible=True  # Only the first dataset is visible initially
            ),
            go.Choroplethmapbox(
                geojson=self.geojson,
                locations=self.summary_dataset2['Country'],
                z=self.summary_dataset2['Quantity in Millions'],
                colorscale=rd_bu_transparent,
                zmin=0,
                marker_line_color='black',
                marker_line_width=0.2,
                name='Construction',
                colorbar=dict(
                    title='Millions USD',
                    x=1,  # Position the colorbar to the right of the map
                    xanchor='left',
                    titleside='right'
                ),
                visible=False
            ),
            go.Choroplethmapbox(
                geojson=self.geojson,
                locations=self.summary_combined['Country'],
                z=self.summary_combined['Quantity in Millions'],
                colorscale=rd_bu_transparent,
                zmin=0,
                marker_line_color='black',
                marker_line_width=0.2,
                name='Combined Investment and Construction',
                colorbar=dict(
                    title='Millions USD',
                    x=1,  # Position the colorbar to the right of the map
                    xanchor='left',
                    titleside='right'
                ),
                visible=False
            )
        ]

        for trace in traces:
            fig.add_trace(trace)

        # Add the military bases as scattermapbox traces
        base_fig = self.military_map.create_map(update_layout=False)
        for trace in base_fig.data:
            trace.showlegend = True  # Enable legend for bases
            fig.add_trace(trace)

        # Setup toggle buttons for interactivity
        fig.update_layout(
            updatemenus=[
                {
                    'buttons': [
                        {'label': 'Investments',
                         'method': 'update',
                         'args': [{'visible': [True, False, False] + [True] * len(base_fig.data)},
                                  {'title': 'Investments by Country',
                                   'mapbox.zmax': self.summary_dataset1['Quantity in Millions'].max()}]},
                        {'label': 'Construction',
                         'method': 'update',
                         'args': [{'visible': [False, True, False] + [True] * len(base_fig.data)},
                                  {'title': 'Construction by Country',
                                   'mapbox.zmax': self.summary_dataset2['Quantity in Millions'].max()}]},
                        {'label': 'Combined',
                         'method': 'update',
                         'args': [{'visible': [False, False, True] + [True] * len(base_fig.data)},
                                  {'title': 'Combined Investments and Construction by Country',
                                   'mapbox.zmax': self.summary_combined['Quantity in Millions'].max()}]}
                    ],
                    'direction': 'down',
                    'showactive': True,
                    'x': 0.1,
                    'xanchor': 'left',
                    'y': 1.25,  # Adjust y position to prevent overlap with title
                    'yanchor': 'top'
                }
            ],
            mapbox_style="dark",
            mapbox_accesstoken=self.military_map.mapbox_access_token,
            mapbox_zoom=3,
            mapbox_center={"lat": 20, "lon": 0},
            title={
                'text': "Investments and Construction by Country",
                'y': 0.9,
                'x': 0.5,
                'xanchor': 'center',
                'yanchor': 'top'
            },
            legend=dict(
                x=0.02,  # Adjust the x position of the legend
                y=0.98,  # Adjust the y position to move it to the top
                orientation='h'  # Optionally make the legend horizontal
            )
        )

        return fig


if __name__ == "__main__":
    investment_map = CombinedMap()
    investment_map.preprocess_data()
    fig = investment_map.create_map()
    fig.show()
