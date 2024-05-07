import pandas as pd
import plotly.graph_objects as go
from dash import dcc, html, Input, Output


class GDPVisualizer:
    def __init__(self, app, file_path):
        self.app = app
        self.file_path = file_path
        self.load_data()
        self.setup_layout()
        self.setup_callbacks()

    def load_data(self):
        # Load the data
        df = pd.read_csv(self.file_path, skiprows=4)
        # Filter for relevant columns
        df = df[['Country Name', 'Country Code'] + [str(year) for year in range(1960, 2023)]]
        # Melt the DataFrame
        self.df_melted = df.melt(id_vars=['Country Name', 'Country Code'], var_name='Year', value_name='GDP')
        # Filter for relevant countries
        self.relevant_countries = ['United States', 'China', 'Russian Federation', 'India', 'Japan', 'Korea, Rep.',
                                   'Australia', 'Philippines']
        self.df_filtered = self.df_melted[self.df_melted['Country Name'].isin(self.relevant_countries)]

    def setup_layout(self):
        self.app_layout = html.Div([
            dcc.Checklist(
                id='country-selector',
                options=[{'label': country, 'value': country} for country in self.relevant_countries],
                value=self.relevant_countries,
                inline=True,
                inputStyle={"margin-right": "5px", "margin-left": "10px"},
            ),
            dcc.RadioItems(
                id='scale-selector',
                options=[
                    {'label': 'Logarithmic Scale', 'value': 'log'},
                    {'label': 'Linear Scale', 'value': 'linear'}
                ],
                value='log',
                inline=True
            ),
            dcc.RangeSlider(
                id='year-slider',
                min=1960,
                max=2019,
                value=[1960, 2019],
                marks={str(year): str(year) for year in range(1960, 2023, 5)},
                step=1
            ),
            dcc.Graph(id='gdp-line-graph'),
        ])

    def setup_callbacks(self):
        @self.app.callback(
            Output('gdp-line-graph', 'figure'),
            [Input('country-selector', 'value'),
             Input('scale-selector', 'value'),
             Input('year-slider', 'value')]
        )
        def update_graph(selected_countries, selected_scale, selected_years):
            fig = go.Figure()
            filtered_df = self.df_filtered[(self.df_filtered['Country Name'].isin(selected_countries)) &
                                           (self.df_filtered['Year'].astype(int) >= selected_years[0]) &
                                           (self.df_filtered['Year'].astype(int) <= selected_years[1])]
            for country in selected_countries:
                country_df = filtered_df[filtered_df['Country Name'] == country]
                fig.add_trace(go.Scatter(x=country_df['Year'], y=country_df['GDP'], mode='lines', name=country))
            fig.update_layout(
                title='GDP Over Time by Country',
                xaxis_title='Year',
                yaxis_title='GDP in US Dollars',
                yaxis_type=selected_scale
            )
            return fig

