# Import Dash libraries
from dash import Dash, dcc, html, Input, Output
import plotly.graph_objects as go
import pandas as pd
import numpy as np


class SouthKoreaDemographicsApp:
    def __init__(self, title=None, debug=True, port=8050, host='127.0.0.1',
                 df_admin=None, df_demographics=None, projection_years=50, initial_birth_rate=0.7,
                 initial_projection_year=20, initial_mortality_rate=1.0):
        self.df_admin = pd.read_csv(df_admin or 'data/Population__Households_and_Housing_Units_20240508191732.csv',
                                    skiprows=[0])
        self.df_demographics = pd.read_csv(df_demographics or 'data/demographics.csv')
        self.projection_years = projection_years
        self.initial_birth_rate = initial_birth_rate
        self.initial_projection_year = initial_projection_year
        self.initial_mortality_rate = initial_mortality_rate
        self.title = title or "South Korea Demographics Dashboard"
        self.debug = debug
        self.port = port
        self.host = host

        # Correct the columns
        self.corrected_columns = [
            "AdministrativeDivision",
            "TotalPopulation",
            "MaleTotal",
            "FemaleTotal",
            "KoreanTotal",
            "KoreanMale",
            "KoreanFemale",
            "ForeignerTotal",
            "ForeignerMale",
            "ForeignerFemale",
            "HouseholdTotal",
            "OccupancyType",
            "InstitutionalHouseholds",
            "ForeignerHouseholds",
            "HousingUnitsTotal",
            "DetachedDwelling",
            "Apartment",
            "RowHouse",
            "ApartmentPrivateHouse",
            "HouseCommercialBuilding",
            "LivingQuartersOtherHousing"
        ]
        self.df_admin.columns = self.corrected_columns

        # Convert numerical columns to numeric types
        numerical_columns = self.df_admin.columns[1:]
        self.df_admin[numerical_columns] = self.df_admin[numerical_columns].apply(pd.to_numeric, errors='coerce')

        self.base_asfr_percentages = {
            '15_19': 0.02,
            '20_24': 0.20,
            '25_29': 0.30,
            '30_34': 0.25,
            '35_39': 0.15,
            '40_44': 0.05,
            '45_49': 0.03
        }

        # Define age-specific mortality rates per 1,000 (hypothetical rates)
        self.default_mortality_rates = {
            age: rate / 1000 for age, rate in {
                **{i: 5 for i in range(0, 1)},  # Infants
                **{i: 2 for i in range(1, 5)},  # Early childhood
                **{i: 1 for i in range(5, 15)},  # School age
                **{i: 2 for i in range(15, 20)},  # Adolescence
                **{i: 3 for i in range(20, 30)},  # Early adulthood
                **{i: 5 for i in range(30, 40)},  # Middle adulthood
                **{i: 8 for i in range(40, 50)},  # Late adulthood
                **{i: 10 for i in range(50, 60)},  # Senior years
                **{i: 20 for i in range(60, 70)},  # Elderly
                **{i: 30 for i in range(70, 80)},  # Very old
                **{i: 50 for i in range(80, 90)},  # Frail elderly
                **{i: 70 for i in range(90, 100)},  # Nonagenarians
                **{i: 100 for i in range(100, 105)}  # Centenarians
            }.items()
        }

        # Initialize the Dash app
        self.app = Dash(__name__)
        self.layout()
        self.callbacks()

    def layout(self):
        self.app.layout = html.Div([
            # Title
            html.H1(self.title),

            # Controls Panel
            html.Div([
                # Slider for birth rate per woman
                html.Label("Birth Rate per Woman"),
                dcc.Slider(
                    id='birth-rate-slider',
                    min=0.0, max=8.0, step=0.05, value=self.initial_birth_rate,
                    marks={i: f'{i:.1f}' for i in np.arange(0.0, 8.1, 0.5)}
                ),
                # Slider for migration adjustment
                html.Label("Migration Adjustment (%)"),
                dcc.Slider(
                    id='migration-slider',
                    min=-2, max=2, step=0.05, value=0,
                    marks={i: f'{i}%' for i in range(-3, 3, 1)}
                ),
                # Slider for projection year
                html.Label("Projection Year"),
                dcc.Slider(
                    id='projection-year-slider',
                    min=0, max=self.projection_years, step=1, value=self.initial_projection_year,
                    marks={i: str(2024 + i) for i in range(0, self.projection_years + 1, 5)}
                ),
                # Slider for overall mortality adjustment
                html.Label("Overall Mortality Adjustment (%)"),
                dcc.Slider(
                    id='mortality-slider',
                    min=0.5, max=2.0, step=0.05, value=self.initial_mortality_rate,
                    marks={i: f'{i:.2f}' for i in np.arange(0.5, 2.05, 0.1)}
                )
            ], style={'padding': 20, 'maxWidth': 500}),

            # Graph Panel
            html.Div([
                # Population projection graph
                dcc.Graph(id='population-projection-graph'),
                # Demographic breakdown graph
                dcc.Graph(id='demographic-breakdown-graph')
            ])
        ])

    @staticmethod
    def extract_initial_age_data_by_year(df):
        initial_data = {}

        age_ranges = {
            '0-4': range(0, 5),
            '5-9': range(5, 10),
            '10-14': range(10, 15),
            '15-19': range(15, 20),
            '20-24': range(20, 25),
            '25-29': range(25, 30),
            '30-34': range(30, 35),
            '35-39': range(35, 40),
            '40-44': range(40, 45),
            '45-49': range(45, 50),
            '50-54': range(50, 55),
            '55-59': range(55, 60),
            '60-64': range(60, 65),
            '65-69': range(65, 70),
            '70-74': range(70, 75),
            '75-79': range(75, 80),
            '80-84': range(80, 85),
            '85-89': range(85, 90),
            '90-94': range(90, 95),
            '95-99': range(95, 100),
            '100+': range(100, 105)
        }

        for age_range, years in age_ranges.items():
            male_count = df.loc[df['AgeGroup'] == age_range, 'Male'].values[0]
            female_count = df.loc[df['AgeGroup'] == age_range, 'Female'].values[0]

            per_year_male = male_count / len(years)
            per_year_female = female_count / len(years)

            for year in years:
                initial_data[f'Male_{year}'] = per_year_male
                initial_data[f'Female_{year}'] = per_year_female

        return initial_data

    def compute_dynamic_asf_rs(self, tfr):
        return {age: tfr * pct / 5 for age, pct in self.base_asfr_percentages.items()}

    @staticmethod
    def project_population_by_year(initial_data, asfrs, mortality_rates, migration_adj, years, mortality_factor):
        projected_data = {k: [v] for k, v in initial_data.items()}

        for year in range(1, years):
            # Age people by 1 year and apply mortality
            for age in range(104, -1, -1):
                male_key = f'Male_{age}'
                female_key = f'Female_{age}'

                if age == 0:
                    continue

                # Apply migration and adjusted mortality rates
                projected_data[male_key].append(
                    projected_data[f'Male_{age - 1}'][year - 1] * (1 - mortality_rates[age] * mortality_factor) * (1 + migration_adj / 100)
                )
                projected_data[female_key].append(
                    projected_data[f'Female_{age - 1}'][year - 1] * (1 - mortality_rates[age] * mortality_factor) * (1 + migration_adj / 100)
                )

            # Calculate new births using ASFRs for ages 15-49
            new_births = sum(
                projected_data[f'Female_{age}'][year - 1] * asfrs.get(f'{age // 5 * 5}_{age // 5 * 5 + 4}', 0)
                for age in range(15, 50)
            )

            projected_data['Male_0'].append(new_births / 2)
            projected_data['Female_0'].append(new_births / 2)

        return projected_data

    @staticmethod
    def create_population_pyramid(projected_data, projection_year):
        age_groups = [f'{i}-{i + 4}' for i in range(0, 100, 5)] + ['100+']
        male_values = [
                          -sum(projected_data[f'Male_{age}'][projection_year] for age in range(start, start + 5))
                          for start in range(0, 100, 5)
                      ] + [-sum(projected_data[f'Male_{age}'][projection_year] for age in range(100, 105))]
        female_values = [
                            sum(projected_data[f'Female_{age}'][projection_year] for age in range(start, start + 5))
                            for start in range(0, 100, 5)
                        ] + [sum(projected_data[f'Female_{age}'][projection_year] for age in range(100, 105))]

        pyramid_fig = go.Figure()
        pyramid_fig.add_trace(go.Bar(
            y=age_groups,
            x=male_values,
            name='Male',
            orientation='h',
            marker=dict(color='blue')
        ))
        pyramid_fig.add_trace(go.Bar(
            y=age_groups,
            x=female_values,
            name='Female',
            orientation='h',
            marker=dict(color='fuchsia')
        ))
        pyramid_fig.update_layout(
            title='Population Pyramid for Projection Year',
            barmode='overlay',
            xaxis_title='Population',
            yaxis_title='Age Groups',
            bargap=0.1,
            bargroupgap=0.0
        )

        return pyramid_fig

    def update_graphs(self, tfr, migration_adj, projection_year, mortality_factor):
        # Prepare initial demographic data
        initial_age_data = self.extract_initial_age_data_by_year(self.df_demographics)

        # Dynamically compute ASFRs based on TFR
        asfrs = self.compute_dynamic_asf_rs(tfr)

        # Project population and households over time
        projected_age_groups = self.project_population_by_year(
            initial_age_data, asfrs, self.default_mortality_rates, migration_adj, self.projection_years, mortality_factor
        )

        # Create population projection graph
        population_years = [2024 + i for i in range(self.projection_years)]
        population_fig = go.Figure()
        population_fig.add_trace(go.Scatter(
            x=population_years,
            y=[sum(projected_age_groups[f'Male_{age}'][year] + projected_age_groups[f'Female_{age}'][year] for age in range(0, 105)) for year in range(self.projection_years)],
            mode='lines+markers',
            name='Projected Population'
        ))
        population_fig.update_layout(title='Projected Population Over Time', xaxis_title='Year', yaxis_title='Population')

        # Create population pyramid
        demographic_fig = self.create_population_pyramid(projected_age_groups, projection_year)

        return population_fig, demographic_fig

    def callbacks(self):
        @self.app.callback(
            [Output('population-projection-graph', 'figure'),
             Output('demographic-breakdown-graph', 'figure')],
            [Input('birth-rate-slider', 'value'),
             Input('migration-slider', 'value'),
             Input('projection-year-slider', 'value'),
             Input('mortality-slider', 'value')]
        )
        def update_population_and_demographic_graphs(tfr, migration_adj, projection_year, mortality_factor):
            return self.update_graphs(tfr, migration_adj, projection_year, mortality_factor)

    def run(self):
        self.app.run_server(debug=self.debug, port=self.port, host=self.host)


if __name__ == '__main__':
    app_instance = SouthKoreaDemographicsApp(port=8050, host='localhost', projection_years=50)
    app_instance.run()
