import os
import pandas as pd

# In this example, we have defined a function extract_gaze_positions that takes the path to a turns data file,
# the path to a folder containing gaze positions data, and the path to an output folder as input.
# The function reads the turns data and gaze positions data, extracts gaze positions for each turn,
# and saves the extracted data to an Excel file.

def extract_gaze_positions(turns_file, gaze_folder, output_folder):
    # Extract patient ID and ON/OFF state from the turns file name
    base_name = os.path.basename(turns_file)
    patient_id = base_name.split('_')[5]
    base_name_lower = base_name.lower()
    split_base_name = base_name_lower.split('_')

    # Check for 'on' or 'off' after the 7th '_'
    if len(split_base_name) > 7 and ('off' in split_base_name[7] or 'on' in split_base_name[7]):
        state = 'OFF' if 'off' in split_base_name[7] else 'ON'
        output_file_name = f"gaze_data_{patient_id}_{state}.xlsx"
    else:
        state = 'EC'
        output_file_name = f"gaze_data_{patient_id}_EC.xlsx"

    # Determine the patient's folder name
    # if the folder name contains the patient ID
    patient_folder = next((f for f in os.listdir(gaze_folder) if
                           patient_id.lower().replace('_', '-').replace('-', '_')
                           in f.lower().replace('_','-').replace('-','_')),
                          None)
    if not patient_folder:
        patient_folder = next((f for f in os.listdir(gaze_folder) if patient_id in f), None)
        if not patient_folder:

            print(f"Patient folder not found for patient {patient_id}. Skipping...")
            return
    # find the Path to the patient's gaze positions data
    # the file is inside one sub folder (that may has other subfolder) in the patient_folder so we need to walk through the folder
    # untill we find 'gaze_positions_new.xlsx' file
    gaze_file = None
    for root, dirs, files in os.walk(os.path.join(gaze_folder, patient_folder)):
        for file in files:
            if file == 'gaze_positions_new.csv':
                gaze_file = os.path.join(root, file)
                break
        if gaze_file:
            break

    if not gaze_file:
        print(f"Gaze file not found for patient {patient_id}. Skipping...")
        return

    # Read the turns data and gaze positions data
    turns_df = pd.read_excel(turns_file)
    # Read the gaze data
    try:
        gaze_df = pd.read_csv(gaze_file, low_memory=False)
    except Exception as e:
        print(f"Error reading gaze file for patient {patient_id}: {e}")
        return

    # Check if 'SEC.MILI' column exists
    if 'SEC.MILI' not in turns_df.columns:
        print(f"'SEC.MILI' column not found in turns file for patient {patient_id}. Columns found: {turns_df.columns}")
        return

    # Initialize an empty DataFrame to store the extracted gaze data
    extracted_gaze_data = pd.DataFrame()

    # Ensure the turns data has an even number of rows
    if len(turns_df) % 2 != 0:
        print(f"Turns data for patient {patient_id} does not contain an even number of rows. Skipping...")
        return



    # Iterate through the turns data to extract gaze positions
    for i in range(0, len(turns_df), 2):
        start_time = turns_df.iloc[i]['SEC.MILI']
        if i + 1 < len(turns_df):
            end_time = turns_df.iloc[i + 1]['SEC.MILI']
        else:
            print(f"Turns data for patient {patient_id} has incomplete pairs. Skipping...")
            return

        # Extract gaze positions for the current turn
        turn_gaze_data = gaze_df[(gaze_df.iloc[:, 0] >= start_time) & (gaze_df.iloc[:, 0] <= end_time)]
        extracted_gaze_data = pd.concat([extracted_gaze_data, turn_gaze_data])

    # Output file path
    output_file_path = os.path.join(output_folder, output_file_name)

    # Save the extracted gaze data to an Excel file
    extracted_gaze_data.to_excel(output_file_path, index=False)
    print(f"Gaze data extracted and saved to: {output_file_path}")

def process_all_files_in_folder(turns_folder, gaze_folder, output_folder):
    for root, _, files in os.walk(turns_folder):
        for file in files:
            if file.endswith('.xlsx'):
                turns_file = os.path.join(root, file)
                extract_gaze_positions(turns_file, gaze_folder, output_folder)


def main():
    turns_folder = r"C:\Users\shach\Documents\Shachar-s_Thesis2\דטה בסיבובים\non_turns_data"
    gaze_folder = r"C:\Users\shach\Documents\Shachar's_Thesis1\preproccesing_data\data"
    output_folder = r"C:\Users\shach\Documents\Shachar-s_Thesis2\דטה בסיבובים\non_turns_data"

    process_all_files_in_folder(turns_folder, gaze_folder, output_folder)


if __name__ == "__main__":
    main()
