import pandas as pd
import plotly.express as px

# Define the path to the Excel file containing investment data
file_path = 'China-Global-Investment-Tracker-2023-Fall.xlsx'

# Load the specific sheet from the Excel file that contains the data of interest
sheet_4_df = pd.read_excel(file_path, sheet_name=3)

# Identify the header row and the starting row of the actual data
header_row_index = 4
data_start_row = header_row_index + 1

# Read the data again to include column names and skip rows up to the data start row
column_names = sheet_4_df.iloc[header_row_index]
df = pd.read_excel(file_path, sheet_name=3, skiprows=data_start_row, names=column_names)

# Convert month names to their corresponding numeric values for easier date handling
month_to_num = {
    'January': 1, 'February': 2, 'March': 3, 'April': 4, 'May': 5, 'June': 6,
    'July': 7, 'August': 8, 'September': 9, 'October': 10, 'November': 11, 'December': 12
}
df['Month'] = df['Month'].map(month_to_num)

# Construct a 'Date' column by combining 'Year' and 'Month', setting day as the first of the month
df['Date'] = pd.to_datetime(df[['Year', 'Month']].assign(DAY=1))

# Ensure 'Quantity in Millions' column is treated as numeric, converting non-numeric to NaN
df['Quantity in Millions'] = pd.to_numeric(df['Quantity in Millions'], errors='coerce')

# Aggregate data by 'Date', 'Region', and 'Sector', summing up 'Quantity in Millions' for each group
grouped_data = df.groupby(['Date', 'Region', 'Sector'], as_index=False)['Quantity in Millions'].sum()

# Calculate cumulative investment totals over time for each region and sector
grouped_data['Cumulative Investment'] = grouped_data.groupby(['Region', 'Sector'])['Quantity in Millions'].cumsum()

# Generate a comprehensive range of dates to ensure continuous time series in the visualization
all_dates = pd.date_range(start=grouped_data['Date'].min(), end=grouped_data['Date'].max(), freq='MS')

# Create all possible combinations of Region, Sector, and Date to fill gaps in the time series
all_combinations = pd.MultiIndex.from_product([grouped_data['Region'].unique(), grouped_data['Sector'].unique(), all_dates], names=['Region', 'Sector', 'Date']).to_frame(index=False)

# Merge these combinations with the grouped data, filling missing entries with zeros
full_data = pd.merge(all_combinations, grouped_data, on=['Region', 'Sector', 'Date'], how='left')

# Forward fill missing 'Cumulative Investment' values within each group to maintain continuity
full_data['Cumulative Investment'] = full_data.groupby(['Region', 'Sector'])['Cumulative Investment'].ffill().fillna(0)

# Convert dates to string format to use as animation frames in Plotly visualization
full_data['Date_str'] = full_data['Date'].dt.strftime('%Y-%m')

# Pivot data to format it for plotting: sectors vs. regions with cumulative investment values
pivot_data = full_data.pivot_table(index=['Date_str', 'Sector'], columns='Region', values='Cumulative Investment', fill_value=0).reset_index()

# Melt the pivoted data back to a long format suitable for Plotly's bar chart
plot_data = pd.melt(pivot_data, id_vars=['Date_str', 'Sector'], var_name='Region', value_name='Cumulative Investment')

# Generate an animated bar chart visualizing cumulative investment over time by region and sector
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

# Customize y-axis format to display values without abbreviation
fig.update_layout(yaxis_tickformat='')

# Update y-axis label to clarify the unit of measurement is in millions
fig.update_yaxes(title='Cumulative Investment (Millions)')

# Display the animated visualization
fig.show()
