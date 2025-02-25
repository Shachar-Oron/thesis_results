import os
import pandas as pd
import numpy as np

def extract_gaze_positions(turns_file, gaze_folder, x_deltas, y_deltas):
    base_name = os.path.basename(turns_file)
    patient_id = base_name.split('_')[2]

    if 'off' in base_name.lower():
        state = 'OFF'
    elif 'on' in base_name.lower():
        state = 'ON'
    else:
        state = 'EC'

    patient_id_state = f"{patient_id}_{state}"

    patient_folder = next((f for f in os.listdir(gaze_folder) if
                           patient_id.lower().replace('_', '-').replace('-', '_')
                           in f.lower().replace('_','-').replace('-','_')),
                          None)
    if not patient_folder:
        patient_folder = next((f for f in os.listdir(gaze_folder) if patient_id in f), None)
        if not patient_folder:
            print(f"Patient folder not found for patient {patient_id}. Skipping...")
            return

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

    turns_df = pd.read_excel(turns_file)
    gaze_df = pd.read_csv(gaze_file, low_memory=False)

    for i in range(0, len(turns_df), 2):
        start_time = turns_df.iloc[i]['SEC.MILI']
        if i + 1 < len(turns_df):
            end_time = turns_df.iloc[i + 1]['SEC.MILI']
        else:
            print(f"Turns data for patient {patient_id} has incomplete pairs. Skipping...")
            return

        middle_time = (start_time + end_time) / 2

        middle_gaze_df = gaze_df[(gaze_df['#VALUE!'] >= middle_time) & (gaze_df['#VALUE!'] <= end_time)]

        if middle_gaze_df.empty:
            print(f"No matching gaze data found for turn {i // 2 + 1} of patient {patient_id}. Skipping this turn...")
            continue

        middle_gaze = middle_gaze_df.iloc[0]
        end_gaze = middle_gaze_df.iloc[-1]

        # Calculate deltas from middle to end
        x_delta = end_gaze['norm_pos_x'] - middle_gaze['norm_pos_x']
        y_delta = end_gaze['norm_pos_y'] - middle_gaze['norm_pos_y']

        x_deltas.append({'patient_id_state': patient_id_state, 'delta': x_delta})
        y_deltas.append({'patient_id_state': patient_id_state, 'delta': y_delta})

def process_all_files_in_folder(turns_folder, gaze_folder):
    x_deltas = []
    y_deltas = []

    for root, _, files in os.walk(turns_folder):
        for file in files:
            if file.endswith('.xlsx'):
                turns_file = os.path.join(root, file)
                extract_gaze_positions(turns_file, gaze_folder, x_deltas, y_deltas)

    x_df = pd.DataFrame(x_deltas)
    y_df = pd.DataFrame(y_deltas)

    x_stats = x_df.groupby('patient_id_state')['delta'].agg(['mean', 'std']).reset_index()
    y_stats = y_df.groupby('patient_id_state')['delta'].agg(['mean', 'std']).reset_index()

    output_folder = r"C:\Users\shach\Documents\Shachar-s_Thesis2\results\deltas_of_turns"
    os.makedirs(output_folder, exist_ok=True)

    with pd.ExcelWriter(os.path.join(output_folder, 'x_deltas_middle.xlsx')) as writer:
        x_df.to_excel(writer, sheet_name='Deltas', index=False)
        x_stats.to_excel(writer, sheet_name='Statistics', index=False)

    with pd.ExcelWriter(os.path.join(output_folder, 'y_deltas_middle.xlsx')) as writer:
        y_df.to_excel(writer, sheet_name='Deltas', index=False)
        y_stats.to_excel(writer, sheet_name='Statistics', index=False)

    print(f"Excel files have been saved in: {output_folder}")

def main():
    turns_folder = r"C:\Users\shach\Documents\Shachar-s_Thesis2\דטה בסיבובים\output_files\turns_data"
    gaze_folder = r"C:\Users\shach\Documents\Shachar's_Thesis1\preproccesing_data\data"

    process_all_files_in_folder(turns_folder, gaze_folder)

if __name__ == "__main__":
    main()