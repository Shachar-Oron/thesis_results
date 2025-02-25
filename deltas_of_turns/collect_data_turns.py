# i have a file D:\annotations\EC\NB325_straight_ניתוח.xlsx that contains a sheet called PL
# in this sheet there is a table with column PL_EVENTS that contains events in hebrew
# i am looking for events that contains "תחילת סיבוב" or "סוף סיבוב" and i want to extract the value in the column SEC.MILI
# i want to save the output to a new Excel file called "turns_data_EC_NB325.xlsx"

import pandas as pd
import os


def collect_data_turns(input_file, output_file):
    # Read the Excel file
    df = pd.read_excel(input_file, sheet_name='PL', engine='openpyxl')

    # Filter rows based on the criteria with a regex pattern
    filtered_df = df[df['PL_EVENTS'].str.contains(r"תחילת.*סיבוב|סיום.*סיבוב", na=False, regex=True)]

    # Initialize a list to store the indices of rows to keep
    indices_to_keep = []

    i = 0
    while i < len(filtered_df):
        current_event = filtered_df.iloc[i]['PL_EVENTS']
        if "תחילת" in current_event:
            # Keep the current row
            indices_to_keep.append(i)
            # Check if next row contains "סיום"
            if i < len(filtered_df) - 1 and "סיום" in filtered_df.iloc[i + 1]['PL_EVENTS']:
                indices_to_keep.append(i + 1)
                i += 1
        i += 1

    # Create a new DataFrame with only the rows to keep
    cleaned_df = filtered_df.iloc[indices_to_keep]

    # Extract the 'SEC.MILI' column from the cleaned dataframe
    result_df = cleaned_df[['SEC.MILI']]

    # Remove the output file if it already exists
    if os.path.exists(output_file):
        os.remove(output_file)

    # Save the cleaned data to a new Excel file
    result_df.to_excel(output_file, index=False, engine='openpyxl')
    print("Data collection complete. Data saved to:", output_file)


def process_all_files_in_folder(folder_path, output_folder):
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    for root, dirs, files in os.walk(folder_path):
        for file in files:
            if file.endswith('.xlsx'):
                input_file = os.path.join(root, file)
                try:
                    df = pd.read_excel(input_file, sheet_name='PL', engine='openpyxl')
                    output_file_name = f"turns_data_{os.path.splitext(file)[0]}.xlsx"
                    output_file = os.path.join(output_folder, output_file_name)
                    collect_data_turns(input_file, output_file)
                except Exception as e:
                    print(f"Skipping file {input_file}: {e}")


def main():
    # Path to the folder containing the Excel files
    folder_path = r"D:\annotations"
    # Path to the output folder
    output_folder = r"C:\Users\shach\Documents\Shachar-s_Thesis2\דטה בסיבובים\output_files"
    # Process all files in the folder
    process_all_files_in_folder(folder_path, output_folder)

if __name__ == "__main__":
    main()
