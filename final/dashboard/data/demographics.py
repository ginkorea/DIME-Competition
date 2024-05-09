import pandas as pd

# Create the demographic data as a DataFrame
data = {
    'AgeGroup': ['Total', '0-4', '5-9', '10-14', '15-19', '20-24', '25-29', '30-34', '35-39', '40-44',
                 '45-49', '50-54', '55-59', '60-64', '65-69', '70-74', '75-79', '80-84', '85-89',
                 '90-94', '95-99', '100+'],
    'Male': [25915207, 883196, 1161247, 1168937, 1271404, 1762135, 1959723, 1742483, 1970249, 1997630,
             2196042, 2195060, 212792, 1912792, 1344575, 946539, 684291, 419037, 168643, 42951, 8024, 869],
    'Female': [25913929, 838885, 1103348, 1098544, 1178157, 1602669, 1706489, 1558848, 1835221, 1909035,
               2129635, 2176994, 2101265, 1972505, 1419612, 1081140, 916576, 701744, 395287, 149712,
               33488, 4755],
    'Total': [51829136, 1722081, 2264595, 2267481, 2449561, 3364804, 3666212, 3301331, 3805470, 3906665,
              4325697, 4372054, 4210645, 3885297, 2734187, 2027679, 1600867, 1120781, 563930, 192663,
              41512, 5624],
}

# Create the DataFrame
df_demographics = pd.DataFrame(data)


# Function to calculate the percentages
def calculate_percentages(df):
    total_population = df.loc[df['AgeGroup'] == 'Total', 'Total'].values[0]
    df['MalePercentage'] = (df['Male'] / total_population * 100).round(2)
    df['FemalePercentage'] = (df['Female'] / total_population * 100).round(2)
    df['TotalPercentage'] = (df['Total'] / total_population * 100).round(2)
    return df


# Apply the function
df_demographics = calculate_percentages(df_demographics)

# Show the updated DataFrame
df_demographics.to_csv('demographics.csv', index=False)
