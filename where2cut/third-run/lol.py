import pandas as pd
import os

# Get a list of all CSV files containing "Features" in the file name
csv_files = [file for file in os.listdir("csvs/third-run") if "Features" in file and file.endswith('.csv')]

# Create an empty dataframe to store the merged data
merged_data = pd.DataFrame()

# Loop through the CSV files and append the data to the merged data dataframe
for file in csv_files:
    data = pd.read_csv("csvs/third-run/"+file)
    merged_data = merged_data.append(data)

# Write the merged data to a CSV file
merged_data.to_csv('merged_data.csv', index=False)
