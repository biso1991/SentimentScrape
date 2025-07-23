# open exel  file through  pandas 
import pandas as pd
def read_excel(file_path):
    try:
        # Read the Excel file
        df = pd.read_excel(file_path)
        return df
    except Exception as e:
        print(f"An error occurred: {e}")
        return None

# dataset_tiktok-scraper_2025-06-20_13-21-16-574.xlsx

 # print columns of the dataframe
def print_columns(df):
    if df is not None:
        print("Columns in the DataFrame:")
        for column in df.columns:
            print(column)
    else:
        print("No DataFrame to display columns from.")