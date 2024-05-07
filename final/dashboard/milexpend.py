import pandas as pd
import plotly.express as px

def prepare_and_plot_data(file_path):
    df_dollars = pd.read_excel(file_path, sheet_name="Current US$", skiprows=4)
    df_share_gdp = pd.read_excel(file_path, sheet_name="Share of GDP", skiprows=4)
    years = df_dollars.iloc[0, 2:].astype(int)

    countries = ["United States of America", "China", "Russia", "Taiwan", "Japan", "Korea, South", "Australia"]
    df_dollars_selected = df_dollars[df_dollars.iloc[:, 0].isin(countries)]
    df_share_gdp_selected = df_share_gdp[df_share_gdp.iloc[:, 0].isin(countries)]

    df_dollars_selected = df_dollars_selected.drop(df_dollars_selected.columns[1], axis=1)
    df_share_gdp_selected = df_share_gdp_selected.drop(df_share_gdp_selected.columns[1], axis=1)

    df_dollars_transposed = df_dollars_selected.set_index(df_dollars_selected.columns[0]).transpose()
    df_share_gdp_transposed = df_share_gdp_selected.set_index(df_share_gdp_selected.columns[0]).transpose()

    df_dollars_transposed.index = years.values
    df_share_gdp_transposed.index = years.values

    df_dollars_transposed.columns = [f"{col} - Current US$" for col in df_dollars_transposed.columns]
    df_share_gdp_transposed.columns = [f"{col} - Share of GDP" for col in df_share_gdp_transposed.columns]

    combined_df = pd.concat([df_dollars_transposed, df_share_gdp_transposed], axis=1)
    ordered_columns = sum([[dollar_col, gdp_col] for dollar_col, gdp_col in zip(df_dollars_transposed.columns, df_share_gdp_transposed.columns)], [])
    combined_df = combined_df[ordered_columns]

    df_long = combined_df.reset_index().melt(id_vars='index', var_name='Country_Variable', value_name='Value')
    df_long[['Country', 'Variable']] = df_long['Country_Variable'].str.rsplit(' - ', n=1, expand=True)
    df_long.drop(columns=['Country_Variable'], inplace=True)

    df_usd = df_long[df_long['Variable'] == 'Current US$'].rename(columns={'Value': 'USD'}).drop('Variable', axis=1)
    df_gdp = df_long[df_long['Variable'] == 'Share of GDP'].rename(columns={'Value': 'GDP'}).drop('Variable', axis=1)

    df_plot = pd.merge(df_usd, df_gdp, on=['index', 'Country'])
    df_plot.rename(columns={'index': 'Year'}, inplace=True)

    df_plot['USD'] = pd.to_numeric(df_plot['USD'], errors='coerce') / 1000  # Convert millions to billions
    df_plot['GDP'] = pd.to_numeric(df_plot['GDP'], errors='coerce')

    fig = px.scatter(df_plot, x='GDP', y='USD', animation_frame='Year', animation_group='Country',
                     size='USD', color='Country', hover_name='Country', size_max=60,
                     log_x=False, range_x=[df_plot['GDP'].min(), df_plot['GDP'].max()],
                     range_y=[df_plot['USD'].min(), df_plot['USD'].max()])
    fig.update_layout(title='Military Expenditure as a Share of GDP Over Time',
                      xaxis_title='Share of GDP (%)', yaxis_title='Military Expenditure (Billions US$)',
                      xaxis=dict(type='linear'), yaxis=dict(type='linear', tickformat=',.2f'),
                      yaxis_tickprefix='$', yaxis_tickformat=',.2fB')
    return fig