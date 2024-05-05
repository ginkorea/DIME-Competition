import pandas as pd
import plotly.graph_objects as go


class InvestmentChoroplethMap:
    def __init__(self, dataset1_path=None, dataset2_path=None, combined_path=None):
        # Load each dataset
        self.summary_combined = None
        self.summary_dataset2 = None
        self.summary_dataset1 = None
        if dataset1_path is None:
            dataset1_path = '../data/Investments.csv'
        if dataset2_path is None:
            dataset2_path = '../data/Construction.csv'
        if combined_path is None:
            combined_path = '../data/Investments_and_construction.csv'
        self.df_dataset1 = pd.read_csv(dataset1_path)
        self.df_dataset2 = pd.read_csv(dataset2_path)
        self.df_combined = pd.read_csv(combined_path)

    def preprocess_data(self):
        # Preprocess each dataset to summarize investments by country
        self.summary_dataset1 = self.df_dataset1.groupby('Country')['Quantity in Millions'].sum().reset_index()
        self.summary_dataset2 = self.df_dataset2.groupby('Country')['Quantity in Millions'].sum().reset_index()
        self.summary_combined = self.df_combined.groupby('Country')['Quantity in Millions'].sum().reset_index()

    @staticmethod
    def create_choropleth(df, title):
        # Helper function to create a choropleth map for a given dataset
        return go.Choropleth(
            locations=df['Country'],
            locationmode='country names',
            z=df['Quantity in Millions'],
            text=df['Country'],
            colorscale='Reds',
            marker_line_color='darkgray',
            marker_line_width=0.5,
            colorbar_title='Investment<br>Millions USD',
            name=title,
            showscale=True  # Show color scale
        )

    def create_map(self):
        # Create initial figure with the first dataset visible
        initial_data = self.create_choropleth(self.summary_dataset1, 'Investments')
        fig = go.Figure(initial_data)

        fig.update_layout(
            updatemenus=[{
                'buttons': [
                    {
                        'label': 'Investments',
                        'method': 'update',
                        'args': [{'visible': [True, False, False]},
                                 {'title': 'Chinese Investments by Country'}]
                    },
                    {
                        'label': 'Construction',
                        'method': 'update',
                        'args': [{'visible': [False, True, False]},
                                 {'title': 'Chinese Construction by Country'}]
                    },
                    {
                        'label': 'Combined Investment and Construction',
                        'method': 'update',
                        'args': [{'visible': [False, False, True]},
                                 {'title': 'Combined Chinese Investments and Construction by Country'}]
                    }
                ],
                'direction': 'down',
                'pad': {'r': 10, 't': 87},  # Adjusted to move down from the top to prevent overlapping
                'showactive': True,
                'x': 0.1,
                'xanchor': 'left',
                'y': 1,
                'yanchor': 'bottom'
            }],
            title_text='Global Investment and Construction by China',
            title_x=0.5,  # Center the title
            geo=dict(
                showframe=False,
                showcoastlines=False,
                projection_type='equirectangular'
            ),
            margin={"r": 10, "t": 50, "l": 10, "b": 10}  # Adjust margin to ensure full map visibility
        )

        # Add other datasets to the figure but make them invisible initially
        fig.add_trace(self.create_choropleth(self.summary_dataset2, 'Construction'))
        fig.add_trace(self.create_choropleth(self.summary_combined, 'Combined Investment and Construction'))
        fig.data[1].visible = False
        fig.data[2].visible = False

        return fig


if __name__ == "__main__":
    investment_map = InvestmentChoroplethMap()
    investment_map.preprocess_data()
    fig = investment_map.create_map()
    fig.show()
