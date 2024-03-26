import pandas as pd
import plotly.graph_objects as go
from key.key import mapbox_access_token

# Load overseas military bases data
file_path = 'Overseas Military Bases.xlsx'
df = pd.read_excel(file_path, sheet_name='Overseas military base')

# Define color codes for visualization
color_codes = {
    "United States": '#0000FF',  # Blue for the United States
    "China": "#FF0000",  # Red for China
}

# Define groups of countries with corresponding color themes
us_allies = ["United Kingdoms", "Australia", "Canada", "France", "Germany", "Japan", "South Korea", "Italy", "Spain", "Netherlands"]
adversaries = ["Russia", "Iran", "DPRK"]  # DPRK stands for North Korea

# Assign colors to allies and adversaries
for ally in us_allies:
    color_codes[ally] = "#ADD8E6"  # Light blue for US allies
for adversary in adversaries:
    color_codes[adversary] = "#FF6666"  # Light red for adversaries

default_color = "#FFFF00"  # Yellow for countries not specifically categorized

# Add a color column to the dataframe based on the 'Operator' country
df['Color'] = df['Operator'].apply(lambda x: color_codes.get(x, default_color))

# Initialize the Plotly figure
fig = go.Figure()

# Create map traces for each group based on 'Operator'
for group, color in color_codes.items():
    df_group = df[df['Operator'] == group]
    if not df_group.empty:
        fig.add_trace(go.Scattermapbox(
            lat=df_group['Y'],
            lon=df_group['X'],
            mode='markers',
            marker=go.scattermapbox.Marker(size=9, color=color),
            hoverinfo='text',
            hovertext=df_group['Name'] + ' - ' + df_group['Operator'],
            name=group  # Legend label
        ))

# Add a trace for operators not explicitly listed
df_default = df[~df['Operator'].isin(color_codes.keys())]
if not df_default.empty:
    fig.add_trace(go.Scattermapbox(
        lat=df_default['Y'],
        lon=df_default['X'],
        mode='markers',
        marker=go.scattermapbox.Marker(size=9, color=default_color),
        hoverinfo='text',
        hovertext=df_default['Name'] + ' - ' + df_default['Operator'],
        name='Other'
    ))

# Configure map layout and display
fig.update_layout(
    mapbox_style="light",
    mapbox=dict(
        accesstoken=mapbox_access_token,
        center=go.layout.mapbox.Center(lat=0, lon=0),
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

# Show the map
fig.show()
