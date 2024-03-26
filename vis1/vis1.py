import pandas as pd
import plotly.graph_objects as go
from key.key import mapbox_access_token

# Load the dataset
file_path = 'Overseas Military Bases.xlsx'
df = pd.read_excel(file_path, sheet_name='Overseas military base')

# Define hex color codes for each group
color_codes = {
    "United States": '#0000FF',  # Dark Blue
    "China": "#FF0000",  # Dark Red
}

# Allies of the US (shades of blue)
us_allies = [
    "United Kingdoms", "Australia", "Canada", "France",
    "Germany", "Japan", "South Korea", "Italy", "Spain", "Netherlands"
]

# Adversaries (shades of red)
adversaries = ["Russia", "Iran", "DPRK"]  # DPRK is North Korea

# Assign hex color codes to allies and adversaries
for ally in us_allies:
    color_codes[ally] = "#ADD8E6"  # Dodger Blue
for adversary in adversaries:
    color_codes[adversary] = "#FF6666"  # Orange Red

# Default color for countries not specifically categorized (Yellow)
default_color = "#FFFF00"  # Yellow

# Add a color column to the dataframe based on the operator's country
df['Color'] = df['Operator'].apply(lambda x: color_codes.get(x, default_color))

# Initialize a Plotly Figure for a Mapbox map
fig = go.Figure()

# Instead of iterating over each unique color, iterate over each group to create a trace
for group, color in color_codes.items():
    # Filter the DataFrame for bases operated by the current group
    df_group = df[df['Operator'] == group]
    if not df_group.empty:  # Check if there are any bases for the current group
        fig.add_trace(go.Scattermapbox(
            lat=df_group['Y'],
            lon=df_group['X'],
            mode='markers',
            marker=go.scattermapbox.Marker(size=9, color=color),
            hoverinfo='text',
            hovertext=df_group['Name'] + ' - ' + df_group['Operator'],
            name=group  # This sets the legend label to the group's name
        ))

# Add a default trace for any operators not explicitly listed in color_codes
df_default = df[~df['Operator'].isin(color_codes.keys())]
if not df_default.empty:
    fig.add_trace(go.Scattermapbox(
        lat=df_default['Y'],
        lon=df_default['X'],
        mode='markers',
        marker=go.scattermapbox.Marker(size=9, color=default_color),
        hoverinfo='text',
        hovertext=df_default['Name'] + ' - ' + df_default['Operator'],
        name='Other'  # Label for operators not explicitly listed
    ))

# Set up the figure layout with your Mapbox style and token, and correctly add a title
fig.update_layout(
    mapbox_style="light",
    mapbox=dict(
        accesstoken=mapbox_access_token,
        bearing=0,
        center=go.layout.mapbox.Center(lat=0, lon=0),
        pitch=0,
        zoom=1
    ),
    margin={"r": 0, "t": 0, "l": 0, "b": 0},
    title={
        'text': "Overseas Military Bases",
        'y':0.9,
        'x':0.5,
        'xanchor': 'center',
        'yanchor': 'top'}
)


fig.show()