import pandas as pd
import os
import re


def collect_data_turns(input_file, output_file, annotations_folder):
    # Extract patient ID and situation (OFF/ON) from the file name
    base_name = os.path.basename(input_file)
    patient_id = base_name.split('_')[2]  # Extract patient ID from the start of the file name
    patient_id = patient_id.upper()
    situation = 'OFF' if 'OFF' in base_name.upper() else 'ON' if 'ON' in base_name.upper() else ''

    annotations_file = None  # Initialize annotations_file to None

    # Determine the correct subfolder based on the patient ID and situation
    if 'OFF' in situation or 'ON' in situation:
        patient_folder = os.path.join(annotations_folder, 'PD_STRAIGHT')
    else:
        patient_folder = os.path.join(annotations_folder, 'EC')

    if not os.path.exists(patient_folder):
        print(f"Patient folder not found: {patient_folder}")
        return

    # Construct the annotations file path based on patient ID, situation, and file naming convention
    if 'OFF' in situation or 'ON' in situation:
        # find folder that contains patient_id
        for root, dirs, files in os.walk(patient_folder):
            for folder in dirs:
                if patient_id in folder:
                    patient_folder = os.path.join(patient_folder, folder)
                    break
            if patient_folder != os.path.join(annotations_folder, 'PD_STRAIGHT'):
                break

        # the patient_folder contains 2 files - on and off - find the correct one due to the situation
        for root, dirs, files in os.walk(patient_folder):
            for file in files:
                if (situation.lower() in file or situation in file) and not 'Thumbs' in file:
                    annotations_file = os.path.join(patient_folder, file)
                    break
            if annotations_file:
                break
    else:
        annotations_file = os.path.join(patient_folder, f'{patient_id}_straight_ניתוח.xlsx')

    # Check if annotations_file was found
    if not annotations_file or not os.path.exists(annotations_file):
        print(f"Annotations file not found for patient {patient_id} in situation {situation}")
        print(f"annotations_file: {annotations_file}")
        return

    # Read the annotations file within the patient's folder
    try:
        df_annotations = pd.read_excel(annotations_file, sheet_name='PL', engine='openpyxl')
    except Exception as e:
        print(f"Error reading annotations file {annotations_file}: {e}")
        return

    df_annotations = df_annotations.dropna(subset=['PL_EVENTS', 'SEC.MILI'])

    # Find the first walking time from the annotations file
    first_walking_time = df_annotations[df_annotations['PL_EVENTS'].str.contains("תחילת הליכה")]['SEC.MILI'].values
    end_walking_time = \
    df_annotations[df_annotations['PL_EVENTS'].str.contains("סוף") | df_annotations['PL_EVENTS'].str.contains("סיום")][
        'SEC.MILI'].values

    if len(first_walking_time) == 0:
        print(f"No walking start time found for patient {patient_id}")
        return
    if len(end_walking_time) == 0:
        print(f"No walking end time found for patient {patient_id}")
        return

    first_walking_time = first_walking_time[0]
    end_walking_time = end_walking_time[0]

    # Read the turns_data file
    df_turns = pd.read_excel(input_file, engine='openpyxl')
    turns_times = df_turns['SEC.MILI'].values

    # Initialize list to store non_turns times
    non_turns_times = []
    non_turns_times.append(first_walking_time)

    # Process to find non_turns intervals
    for time in turns_times:
        if first_walking_time < time < end_walking_time:
            non_turns_times.append(time)

    # Add the end walking time if it's not already included
    if non_turns_times[-1] != end_walking_time:
        non_turns_times.append(end_walking_time)

    # Create a DataFrame for non_turns times
    non_turns_df = pd.DataFrame(non_turns_times, columns=['SEC.MILI'])

    # Save the non_turns times to a new file in output_folder
    non_turns_df.to_excel(output_file, index=False, engine='openpyxl')
    print(f"Non-turns data saved to: {output_file}")


def process_all_files_in_folder(folder_path, output_folder, annotations_folder):
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    for root, dirs, files in os.walk(folder_path):
        for file in files:
            if file.startswith('turns_data') and file.endswith('.xlsx'):
                input_file = os.path.join(root, file)
                try:
                    output_file_name = f"non_turns_data_{os.path.splitext(file)[0]}.xlsx"
                    output_file = os.path.join(output_folder, output_file_name)
                    collect_data_turns(input_file, output_file, annotations_folder)
                except Exception as e:
                    print(f"Skipping file {input_file}: {e}")


# Define the directory containing the turns_data files and the annotations file path
turns_data_directory = r"C:\Users\shach\Documents\Shachar-s_Thesis2\דטה בסיבובים\output_files"
annotations_folder = r"D:\annotations"  # Adjust this path to match your folder structure
output_folder = r"C:\Users\shach\Documents\Shachar-s_Thesis2\דטה בסיבובים\output_files"

# Process all turns_data files in the directory
process_all_files_in_folder(turns_data_directory, output_folder, annotations_folder)
