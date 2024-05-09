# function to convert an .xls file to a .csv file

import pandas as pd


def convert_xls_to_csv(file_path):
    # Load the Excel file
    df = pd.read_excel(file_path)
    # Save the DataFrame to a CSV file
    csv_file_path = file_path.replace('.xls', '.csv')
    df.to_csv(csv_file_path, index=False)
    return csv_file_path


convert_xls_to_csv('ETITLE.xls')
