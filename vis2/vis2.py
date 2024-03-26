import pandas as pd
import plotly.express as px

# Load the Excel file
file_path = 'China-Global-Investment-Tracker-2023-Fall.xlsx'

# Load sheet 4, assuming it contains the data of interest
sheet_4_df = pd.read_excel(file_path, sheet_name=3)

# Adjust these indices based on where the actual data starts and the headers are located
header_row_index = 4
data_start_row = header_row_index + 1

# Extract column names and skip rows up to the header row
column_names = sheet_4_df.iloc[header_row_index]
df = pd.read_excel(file_path, sheet_name=3, skiprows=data_start_row, names=column_names)

# Map month names to their numeric values for datetime conversion
month_to_num = {
    'January': 1, 'February': 2, 'March': 3, 'April': 4, 'May': 5, 'June': 6,
    'July': 7, 'August': 8, 'September': 9, 'October': 10, 'November': 11, 'December': 12
}
df['Month'] = df['Month'].map(month_to_num)

# Create a 'Date' column from 'Year' and 'Month'
df['Date'] = pd.to_datetime(df[['Year', 'Month']].assign(DAY=1))

# Convert 'Quantity in Millions' to numeric
df['Quantity in Millions'] = pd.to_numeric(df['Quantity in Millions'], errors='coerce')

# Group by 'Date', 'Region', 'Sector', and sum up 'Quantity in Millions' for each group
grouped_data = df.groupby(['Date', 'Region', 'Sector'], as_index=False)['Quantity in Millions'].sum()

# Compute cumulative totals over time by region and sector
grouped_data['Cumulative Investment'] = grouped_data.groupby(['Region', 'Sector'])['Quantity in Millions'].cumsum()

# Creating a full range of dates from min to max for our DataFrame
all_dates = pd.date_range(start=grouped_data['Date'].min(), end=grouped_data['Date'].max(), freq='MS')

# Creating a DataFrame with all combinations of Region, Sector, and Date
all_combinations = pd.MultiIndex.from_product([grouped_data['Region'].unique(), grouped_data['Sector'].unique(), all_dates], names=['Region', 'Sector', 'Date']).to_frame(index=False)

# Merging the full combinations with the original data
full_data = pd.merge(all_combinations, grouped_data, on=['Region', 'Sector', 'Date'], how='left')

# Forward filling the 'Cumulative Investment' for missing months
full_data['Cumulative Investment'] = full_data.groupby(['Region', 'Sector'])['Cumulative Investment'].ffill().fillna(0)

# Ensure dates are formatted as strings for the animation frame
full_data['Date_str'] = full_data['Date'].dt.strftime('%Y-%m')

# Pivot the full_data to have regions as columns and the cumulative investment as values
pivot_data = full_data.pivot_table(index=['Date_str', 'Sector'], columns='Region', values='Cumulative Investment', fill_value=0).reset_index()

# Create a new DataFrame suitable for the plotting with Plotly This step is crucial to ensure we have one row per
# 'Date_str' and 'Sector' with separate columns for each region's cumulative investment
plot_data = pd.melt(pivot_data, id_vars=['Date_str', 'Sector'], var_name='Region', value_name='Cumulative Investment')

# Create the interactive chart with a time slider
fig = px.bar(
    plot_data,
    x='Region',
    y='Cumulative Investment',
    color='Sector',
    animation_frame='Date_str',
    title="Cumulative Investment Size by Region and Sector Over Time (in Millions)",
    category_orders={"Date_str": sorted(plot_data['Date_str'].unique())},
    # Use a Plotly built-in palette or define a custom one with more variety:
    color_discrete_sequence=px.colors.qualitative.Alphabet
)

# Disable the default abbreviation
fig.update_layout(yaxis_tickformat='')

# Manually update the y-axis title to reflect the unit of measurement
fig.update_yaxes(title='Cumulative Investment (Millions)')

# Display the figure
fig.show()