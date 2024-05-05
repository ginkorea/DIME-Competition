import pandas as pd
import plotly.express as px


def generate_cumulative_investment_chart(file_path):
    sheet_4_df = pd.read_excel(file_path, sheet_name=3)
    header_row_index = 4
    data_start_row = header_row_index + 1
    column_names = sheet_4_df.iloc[header_row_index]

    df = pd.read_excel(file_path, sheet_name=3, skiprows=data_start_row, names=column_names)

    month_to_num = {
        'January': 1, 'February': 2, 'March': 3, 'April': 4, 'May': 5, 'June': 6,
        'July': 7, 'August': 8, 'September': 9, 'October': 10, 'November': 11, 'December': 12
    }
    df['Month'] = df['Month'].map(month_to_num)
    df['Date'] = pd.to_datetime(df[['Year', 'Month']].assign(DAY=1))
    df['Quantity in Millions'] = pd.to_numeric(df['Quantity in Millions'], errors='coerce')

    grouped_data = df.groupby(['Date', 'Region', 'Sector'], as_index=False)['Quantity in Millions'].sum()
    grouped_data['Cumulative Investment'] = grouped_data.groupby(['Region', 'Sector'])['Quantity in Millions'].cumsum()

    all_dates = pd.date_range(start=grouped_data['Date'].min(), end=grouped_data['Date'].max(), freq='MS')
    all_combinations = pd.MultiIndex.from_product(
        [grouped_data['Region'].unique(), grouped_data['Sector'].unique(), all_dates],
        names=['Region', 'Sector', 'Date']
    ).to_frame(index=False)

    full_data = pd.merge(all_combinations, grouped_data, on=['Region', 'Sector', 'Date'], how='left')
    full_data['Cumulative Investment'] = full_data.groupby(['Region', 'Sector'])[
        'Cumulative Investment'].ffill().fillna(0)
    full_data['Date_str'] = full_data['Date'].dt.strftime('%Y-%m')

    pivot_data = full_data.pivot_table(index=['Date_str', 'Sector'], columns='Region', values='Cumulative Investment',
                                       fill_value=0).reset_index()
    plot_data = pd.melt(pivot_data, id_vars=['Date_str', 'Sector'], var_name='Region',
                        value_name='Cumulative Investment')

    fig = px.bar(
        plot_data,
        x='Region',
        y='Cumulative Investment',
        color='Sector',
        animation_frame='Date_str',
        title="Cumulative Investment Size by Region and Sector Over Time (in Millions)",
        category_orders={"Date_str": sorted(plot_data['Date_str'].unique())},
        color_discrete_sequence=px.colors.qualitative.Alphabet
    )
    fig.update_layout(yaxis_tickformat='')
    fig.update_yaxes(title='Cumulative Investment (Millions)')
    return fig
