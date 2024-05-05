import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from key.key import mapbox_access_token


class MilitaryBasesMap:
    def __init__(self, file_path=None):
        if file_path is None:
            file_path = '../data/Overseas Military Bases.xlsx'
        self.file_path = file_path
        self.mapbox_access_token = mapbox_access_token
        self.df = pd.read_excel(file_path, sheet_name='Overseas military base')
        self.color_codes = {
            "United States": '#0000FF',
            "China": "#FF0000",
            "United Kingdoms": "#ADD8E6",
            "Australia": "#ADD8E6",
            "Canada": "#ADD8E6",
            "France": "#ADD8E6",
            "Germany": "#ADD8E6",
            "Japan": "#ADD8E6",
            "South Korea": "#ADD8E6",
            "Italy": "#ADD8E6",
            "Spain": "#ADD8E6",
            "Netherlands": "#ADD8E6",
            "Russia": "#FF6666",
            "Iran": "#FF6666",
            "DPRK": "#FF6666",
        }
        self.default_color = "#FFFF00"

    def assign_colors(self):
        self.df['Color'] = self.df['Operator'].apply(lambda x: self.color_codes.get(x, self.default_color))

    def create_map(self, update_layout=True):
        fig = make_subplots(rows=1, cols=1, specs=[[{'type': 'scattermapbox'}]])

        for group, color in self.color_codes.items():
            df_group = self.df[self.df['Operator'] == group]
            if not df_group.empty:
                fig.add_trace(go.Scattermapbox(
                    lat=df_group['Y'],
                    lon=df_group['X'],
                    mode='markers',
                    marker=go.scattermapbox.Marker(size=9, color=color),
                    hoverinfo='text',
                    hovertext=df_group['Name'] + ' - ' + df_group['Operator'],
                    name=group
                ))

        df_default = self.df[~self.df['Operator'].isin(self.color_codes.keys())]
        if not df_default.empty:
            fig.add_trace(go.Scattermapbox(
                lat=df_default['Y'],
                lon=df_default['X'],
                mode='markers',
                marker=go.scattermapbox.Marker(size=9, color=self.default_color),
                hoverinfo='text',
                hovertext=df_default['Name'] + ' - ' + df_default['Operator'],
                name='Other'
            ))
        if update_layout:
            fig.update_layout(
                mapbox_style="light",
                mapbox=dict(
                    accesstoken=mapbox_access_token,
                    center=go.layout.mapbox.Center(lat=0, lon=0),
                    zoom=1
                ),
                margin={"r": 0, "t": 0, "l": 0, "b": 0},
                legend=dict(
                    x=0.02,  # Positioning the legend to the left
                    y=1,  # Positioning the legend at the top
                    bgcolor='rgba(255, 255, 255, 0.5)',  # Making legend background semi-transparent
                    orientation='h'  # Horizontal orientation to take less vertical space
                ),
                title={
                    'text': "Overseas Military Bases",
                    'y': 0.9,
                    'x': 0.5,
                    'xanchor': 'center',
                    'yanchor': 'top'
                },
                updatemenus=[
                    {
                        'buttons': [
                            {
                                'args': [None, {'frame': {'duration': 500, 'redraw': True}, 'fromcurrent': True}],
                                'label': 'Play',
                                'method': 'animate'
                            },
                        ],
                        'direction': 'left',
                        'pad': {'r': 10, 't': 10},  # Reduced top padding
                        'showactive': False,
                        'type': 'buttons',
                        'x': 0.1,  # Horizontal position
                        'xanchor': 'right',
                        'y': 0.2,  # Lower vertical position
                        'yanchor': 'top'
                    }
                ]
            )
        return fig


if __name__ == "__main__":
    military_bases_map = MilitaryBasesMap()
    military_bases_map.assign_colors()
    fig = military_bases_map.create_map()
    fig.show()
